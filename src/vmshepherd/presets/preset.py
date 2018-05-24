import asyncio
import logging
import time
from collections import Counter
from vmshepherd.iaas.vm import VmState


class Preset:

    def __init__(self, name: str, origin: str):
        self.iaas = None
        self.healthcheck = None
        self.runtime_mgr = None
        self.runtime = None
        self.config = {}
        self.name = name
        self.count = 0
        self.created = 0
        self.terminated = 0
        self.healthcheck_terminated = 0
        self.origin = origin
        self._extra = {'preset': self.name}
        self._locked = False
        self._vms = []

    @property
    def vms(self):
        return self._vms

    @property
    def path(self):
        return self.origin

    def configure(self, config: dict, runtime_mgr: object, iaas: object, healthcheck: object):
        self.iaas = iaas
        self.healthcheck = healthcheck
        self.config = config
        self.count = config['count']
        self.runtime_mgr = runtime

    def _reset_counters(self):
        self.created = 0
        self.terminated = 0
        self.healthcheck_terminated = 0

    async def _terminate_vm(self, vm):
        await vm.terminate()

    async def __aenter__(self):
        self.runtime = await self.runtime_mgr.get_preset_data(self.name)
        require_manage = time.time() - self.runtime.last_managed > int(self.config.get('manage_interval', 60))
        if not require_manage:
            return False

        expired = time.time() - self.runtime.last_managed > int(self.config.get('manage_expire', 120))
        self._locked = await self.runtime_mgr.acquire_lock(self.name)

        self._reset_counters()

        return expired or self._locked

    async def __aexit__(self, exc_type, exc, tb):
        if self._locked:
            self._locked = False
            await self.runtime.set_preset_data(self.name, self.runtime)
            await self.runtime.release_lock(self.name)

    async def _create_vms(self, count):
        for i in range(count):
            try:
                args = dict(
                    preset_name=self.name, image=self.config['image'], flavor=self.config['flavor'],
                    userdata=self.config.get('userdata'), key_name=self.config.get('key_name'),
                    **(self.config.get('network', {}))
                )
                await self.iaas.create_vm(**args)
                self.created += 1
            except Exception:
                logging.error('Could not create vm with %s', args, extra=self._extra)

    async def manage(self):
        self.vms = await self.iaas.list_vms(self.name)

        vms_stat = Counter([vm.get_state() for vm in self.vms])
        missing = self.count - len(self.vms) if len(self.vms) < self.count else 0
        logging.info(
            'VMs Status: %s expected, %s in iaas, %s running, %s nearby shutdown, %s pending, %s after time shutdown, '
            '%s terminated, %s error, %s unknown, %s missing',
            self.count, len(vms), vms_stat[VmState.RUNNING.value], vms_stat[VmState.NEARBY_SHUTDOWN.value],
            vms_stat[VmState.PENDING.value], vms_stat[VmState.AFTER_TIME_SHUTDOWN.value],
            vms_stat[VmState.TERMINATED.value], vms_stat[VmState.ERROR.value], vms_stat[VmState.UNKNOWN.value], missing, extra=self._extra
        )
        for vm in self.vms:
            if vm.is_dead():
                logging.info("Terminate %s", vm, extra=self._extra)
                await vm.terminate()
                self.terminated += 1
        to_create = self.count - (len(self.vms) - self.terminated - vms_stat[VmState.NEARBY_SHUTDOWN.value])
        to_create = to_create if to_create > 0 else 0
        logging.debug("Create %s Vm", to_create, extra=self._extra)
        await self._create_vms(to_create)
        await self._healthcheck(self.vms)
        logging.info(
            'VMs Status update: %s terminated, %s terminated by healthcheck, %s created, %s failed healthcheck',
            self.terminated, self.healthcheck_terminated, to_create, len(self.runtime.failed_checks),
            extra=self._extra
        )

    async def _healthcheck(self, vms):
        _healthchecks = {}
        for vm in vms:
            if not vm.is_dead():
                _healthchecks[vm] = asyncio.ensure_future(self.healthcheck.is_healthy(vm))
        await asyncio.gather(*list(_healthchecks.values()), return_exceptions=True)
        current_fails = []

        for vm, state_check in _healthchecks.items():
            # if check failed
            if not state_check.result():
                current_fails.append(vm.id)
                failed_since = self.runtime.failed_checks.get(vm.id, {}).get('time', time.time())
                count_fails = self.runtime.failed_checks.get(vm.id, {}).get('count', 0)
                self.runtime.failed_checks[vm.id] = {'time': failed_since, 'count': count_fails + 1}
                terminate_heatlh_failed_delay = self.config.get('healthcheck', {}).get('terminate_heatlh_failed_delay', -1)
                if terminate_heatlh_failed_delay >= 0 and count_fails > 5:
                    if terminate_heatlh_failed_delay + failed_since < time.time():
                        logging.debug("Terminate %s, healthcheck fails (count %s) since %s", vm, count_fails,
                                      failed_since, extra=self._extra)
                        await self._terminate_vm(vm)
                        self.healthcheck_terminated += 1

        for vm_id in list(self.runtime.failed_checks.keys()):
            if vm_id not in current_fails:
                del self.runtime.failed_checks[vm_id]
