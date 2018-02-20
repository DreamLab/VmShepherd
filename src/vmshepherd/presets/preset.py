import asyncio
import logging
from datetime import datetime, timedelta


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
        self._locked = False

    async def _terminate_vm(self, vm):
        await vm.terminate()

    async def __aenter__(self):
        self._locked = await self.runtime.acquire_lock(self.name)
        return self._locked

    async def __aexit__(self, exc_type, exc, tb):
        if self._locked:
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
                logging.error('Could not create vm with %s', args)

    async def list_vms(self):
        vms = await self.iaas.list_vms(self.name)
        return vms

    async def manage(self):
        vms = await self.list_vms()
        runtime_stats = await self.runtime.get_preset_data(self.name)

        missing = self.count - len(vms) if len(vms) < self.count else 0

        logging.info(
            '%s iaas_count: %s preset_count: %s missing: %s',
            self.name, len(vms), self.count, missing
        )
        for vm in vms:
            if vm.is_dead():
                missing += 1
                self.terminated += 1
                await vm.terminate()

        await self._create_vms(missing)
        runtime_stats['CHECK'] = await self._healthcheck(vms, runtime_stats)
        await self.runtime.set_preset_data(self.name, runtime_stats)

    async def _healthcheck(self, vms, data):
        _healthchecks = {}
        for vm in vms:
            if vm.is_running():
                _healthchecks[vm] = asyncio.ensure_future(self.healthcheck.is_healthy(vm))
        await asyncio.gather(*list(_healthchecks.values()), return_exceptions=True)
        vms_prev_fails = data.get('CHECK', {})
        vms_fails = {}
        missing = 0
        for vm, state_check in _healthchecks.items():
            # if check failed
            if not state_check.result():
                vms_fails[vm.id] = {
                    'time': vms_prev_fails.get(vm.id, {}).get('time', datetime.now()),
                    'count': vms_prev_fails.get(vm.id, {}).get('count', 0) + 1
                }
                terminate_heatlh_failed_delay = self.config.get('healthcheck', {}).get('terminate_heatlh_failed_delay', -1)
                if terminate_heatlh_failed_delay >= 0:
                    if timedelta(seconds=terminate_heatlh_failed_delay) + vms_fails[vm.id]['time'] < datetime.now():
                        logging.info("Terminate %s, healthcheck fails since %s", vm, vms_fails[vm.id]['time'])
                        missing += 1
                        await self._terminate_vm(vm)
        return vms_fails
