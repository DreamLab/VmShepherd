import asyncio
import logging
import time
from collections import Counter
from vmshepherd.iaas.vm import VmState


class Preset:

    def __init__(self, name: str):
        self.iaas = None
        self.healthcheck = None
        self.unmanaged = False
        self.runtime_mgr = None
        self.runtime = None
        self.config = {}
        self.name = name
        self.count = 0
        self.created = 0
        self.terminated = 0
        self.healthcheck_terminated = 0
        self._extra = {'preset': self.name}
        self._locked = False
        self._vms_refresh_time = 0

    def configure(self, config: dict, runtime_mgr: object, iaas: object, healthcheck: object):
        self.iaas = iaas
        self.healthcheck = healthcheck
        self.unmanaged = config.get('unmanaged', False)
        self.config = config
        self.count = config['count']
        self.runtime_mgr = runtime_mgr

    def _reset_counters(self):
        self.created = 0
        self.terminated = 0
        self.healthcheck_terminated = 0

    async def __aenter__(self):
        self.runtime = await self.runtime_mgr.get_preset_data(self.name)
        require_manage = time.time() - self.runtime.last_managed > self.config.get('manage_interval', 60)
        if not require_manage:
            return False

        expired = time.time() - self.runtime.last_managed > self.config.get('manage_expire', 120)
        self._locked = expired or (await self.runtime_mgr.acquire_lock(self.name))

        self._reset_counters()

        return self._locked

    async def __aexit__(self, exc_type, exc, tb):
        if self._locked:
            self._locked = False
            await self.runtime_mgr.set_preset_data(self.name, self.runtime)
            await self.runtime_mgr.release_lock(self.name)

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

    async def get_vms(self):
        """ Get cached vm list"""
        runtime_data = await self.runtime_mgr.get_preset_data(self.name)
        return runtime_data.iaas['vms'] if 'vms' in runtime_data.iaas else []

    async def manage(self):
        """ Manage function docstring"""
        vms = await self.iaas.list_vms(self.name)

        vms_stat = Counter([vm.get_state() for vm in vms])
        missing = self.count - len(vms) if len(vms) < self.count else 0
        logging.info(
            'State: %s, VMs Status: %s expected, %s in iaas, %s running, %s nearby shutdown, %s pending, '
            '%s after time shutdown, %s terminated, %s error, %s unknown, %s missing',
            'unmanaged' if self.unmanaged else 'managed', self.count, len(vms),
            vms_stat[VmState.RUNNING.value], vms_stat[VmState.NEARBY_SHUTDOWN.value], vms_stat[VmState.PENDING.value],
            vms_stat[VmState.AFTER_TIME_SHUTDOWN.value], vms_stat[VmState.TERMINATED.value],
            vms_stat[VmState.ERROR.value], vms_stat[VmState.UNKNOWN.value], missing, extra=self._extra
        )

        to_create = 0
        if not self.unmanaged:
            for vm in vms:
                if vm.is_dead():
                    logging.info("Terminate %s", vm, extra=self._extra)
                    await self.iaas.terminate_vm(vm_id=vm.id)
                    self.terminated += 1
            running_vms = len(vms) - self.terminated - vms_stat[VmState.NEARBY_SHUTDOWN.value]
            to_create = self.count - running_vms
            logging.debug("Create %s Vm", to_create, extra=self._extra)
            await self._create_vms(to_create)

        self.runtime.iaas['vms'] = vms
        await self._healthcheck(vms)

        if not self.unmanaged:
            logging.info(
                'VMs Status update: %s terminated, %s terminated by healthcheck, %s created, %s failed healthcheck',
                self.terminated, self.healthcheck_terminated, to_create, len(self.runtime.failed_checks),
                extra=self._extra
            )
        else:
            logging.info(
                'VMs Status update: %s failed healthcheck', len(self.runtime.failed_checks), extra=self._extra
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
                failed_data = {'time': failed_since, 'count': count_fails + 1}
                self.runtime.failed_checks[vm.id] = failed_data
                vm.set_state(VmState.UNHEALTHY, failed_data)

                # terminate check failed vms
                terminate_heatlh_failed_delay = self.config.get('healthcheck', {}).get('terminate_heatlh_failed_delay', -1)
                if not self.unmanaged and terminate_heatlh_failed_delay >= 0 and count_fails > 5:
                    if terminate_heatlh_failed_delay + failed_since < time.time():
                        logging.info("Terminate %s, healthcheck fails (count %s) since %s", vm, count_fails,
                                      failed_since, extra=self._extra)
                        await self.iaas.terminate_vm(vm_id=vm.id)
                        self.healthcheck_terminated += 1

        for vm_id in list(self.runtime.failed_checks.keys()):
            if vm_id not in current_fails:
                logging.info(
                    'Vm %s, healthcheck failed (count %s) for %s seconds', vm_id,
                    self.runtime.failed_checks[vm_id]['count'],
                    int(time.time() - self.runtime.failed_checks[vm_id]['time'])
                )
                del self.runtime.failed_checks[vm_id]
