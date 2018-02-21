import asyncio
import logging
import time


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
        self.info = None

    async def _terminate_vm(self, vm):
        await vm.terminate()

    async def __aenter__(self):
        self.info = await self.runtime.get_preset_data(self.name)
        # TODO: literal, magic numbers should be taken from config
        require_manage = time.time() - self.info.last_managed > 10
        if not require_manage:
            return False

        expired = time.time() - self.info.last_managed > 120
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
                logging.error('Could not create vm with %s', args)

    async def list_vms(self):
        vms = await self.iaas.list_vms(self.name)
        return vms

    async def manage(self):
        vms = await self.list_vms()

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
        await self._healthcheck(vms)

    async def _healthcheck(self, vms):
        _healthchecks = {}
        for vm in vms:
            if vm.is_running():
                _healthchecks[vm] = asyncio.ensure_future(self.healthcheck.is_healthy(vm))
        await asyncio.gather(*list(_healthchecks.values()), return_exceptions=True)
        missing = 0
        current_fails = []

        for vm, state_check in _healthchecks.items():
            # if check failed
            if not state_check.result():
                current_fails.append(vm.id)
                last_failed = self.info.failed_checks.get(vm.id, {}).get('time', time.time())
                count_fails = self.info.failed_checks.get(vm.id, {}).get('count', 0)
                self.info.failed_checks[vm.id] = {'time': time.time(), 'count': count_fails + 1}
                terminate_heatlh_failed_delay = self.config.get('healthcheck', {}).get('terminate_heatlh_failed_delay', -1)
                if terminate_heatlh_failed_delay >= 0:
                    if terminate_heatlh_failed_delay + last_failed < time.time():
                        logging.info("Terminate %s, healthcheck fails (count %s) since %s", vm, count_fails, last_failed)
                        missing += 1
                        await self._terminate_vm(vm)

        for vm in self.info.failed_checks:
            if vm not in current_fails:
                del self.info.failed_checks[vm.id]
