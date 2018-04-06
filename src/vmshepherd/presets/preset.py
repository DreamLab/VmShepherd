import asyncio
import logging
import time
from collections import Counter
from vmshepherd.iaas.vm import VmState


class Preset:

    def __init__(self, name: str, config: dict, runtime: object, iaas=None, healthcheck=None):
        self.iaas = iaas
        self.healthcheck = healthcheck
        self.config = config
        self.name = name
        self.runtime = runtime
        self.count = config['count']
        self.created = 0
        self.terminated = 0
        self.healthcheck_terminated = 0
        self._extra = {'preset': self.name}
        self._locked = False
        self.info = None

    async def _terminate_vm(self, vm):
        await vm.terminate()

    async def __aenter__(self):
        self.info = await self.runtime.get_preset_data(self.name)
        # TODO: literal, magic numbers should be taken from config
        require_manage = time.time() - self.info.last_managed > int(self.config.get('manage_interval', 60))
        if not require_manage:
            return False

        expired = time.time() - self.info.last_managed > int(self.config.get('manage_expire', 120))
        self._locked = await self.runtime.acquire_lock(self.name)

        return expired or self._locked

    async def __aexit__(self, exc_type, exc, tb):
        if self._locked:
            await self.runtime.set_preset_data(self.name, self.info)
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

    async def list_vms(self):
        vms = await self.iaas.list_vms(self.name)
        return vms

    async def manage(self):
        vms = await self.list_vms()

        vms_stat = Counter([vm.get_state() for vm in vms])
        missing = self.count - len(vms) if len(vms) < self.count else 0
        logging.info(
            'VMs Status: %s expected, %s in iaas, %s running, %s nearbyshutdown, %s pending, aftertimeshutdown %s, '
            '%s terminated, %s error, %s unknown, %s missing',
            self.count, len(vms), vms_stat[VmState.RUNNING.value], vms_stat[VmState.NEARBYSHUTDOWN.value],
            vms_stat[VmState.PENDING.value], vms_stat[VmState.AFTERTIMESHUTDOWN.value],
            vms_stat[VmState.TERMINATED.value], vms_stat[VmState.ERROR.value], vms_stat[VmState.UNKNOWN.value], missing, extra=self._extra
        )
        for vm in vms:
            if vm.is_dead():
                logging.info("Terminate %s", vm, extra=self._extra)
                await vm.terminate()
                self.terminated += 1
        to_create = self.count - (len(vms) - self.terminated - vms_stat[VmState.NEARBYSHUTDOWN.value])
        to_create = to_create if to_create > 0 else 0
        logging.debug("Create %s Vm", to_create, extra=self._extra)
        await self._create_vms(to_create)
        await self._healthcheck(vms)
        logging.info(
            'VMs Status update: %s terminated, %s terminated by healthcheck, %s created, %s failed healthcheck',
            self.terminated, self.healthcheck_terminated, to_create, len(self.info.failed_checks),
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
                failed_since = self.info.failed_checks.get(vm.id, {}).get('time', time.time())
                count_fails = self.info.failed_checks.get(vm.id, {}).get('count', 0)
                self.info.failed_checks[vm.id] = {'time': failed_since, 'count': count_fails + 1}
                terminate_heatlh_failed_delay = self.config.get('healthcheck', {}).get('terminate_heatlh_failed_delay', -1)
                if terminate_heatlh_failed_delay >= 0 and count_fails > 5:
                    if terminate_heatlh_failed_delay + failed_since < time.time():
                        logging.debug("Terminate %s, healthcheck fails (count %s) since %s", vm, count_fails,
                                      failed_since, extra=self._extra)
                        await self._terminate_vm(vm)
                        self.healthcheck_terminated += 1

        for vm_id in list(self.info.failed_checks.keys()):
            if vm_id not in current_fails:
                del self.info.failed_checks[vm_id]
