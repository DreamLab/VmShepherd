import copy
from aiohttp_jsonrpc import handler


class RpcApi(handler.JSONRPCView):

    def __init__(self, allowed_methods=None):
        self.METHOD_PREFIX = ''
        self.allowed_methods = allowed_methods

    async def handler(self, request):
        self._request = request
        return await self

    def enabled_checker(func):
        '''
            Access decorator
        '''
        async def wrap(self, *args, **kwargs):
            if self.allowed_methods and isinstance(self.allowed_methods, list) and func.__name__ not in self.allowed_methods:
                raise Exception("Method {} is disabled".format(func.__name__))
            return await func(self, *args, **kwargs)
        return wrap

    @enabled_checker
    async def list_vms(self, preset):
        """ List VMs for preset, with runtime states.

        :arg string preset: preset name (e.g. C_DEV-apps-dev)

        """
        vmshepherd = self.request.app.vmshepherd
        await vmshepherd.preset_manager.reload()
        preset = await vmshepherd.preset_manager.get(preset)
        vms = await preset.list_vms()
        result_vms = {vm.id: {'ip': vm.ip[0], 'state': vm.state.value} for vm in vms}
        return preset.count, result_vms

    @enabled_checker
    async def terminate_vm(self, preset, vm_id):
        """ Discard vm in specified preset

        :arg string preset: preset name
        :arg int vm_id: Vm's id

        """
        vmshepherd = self.request.app.vmshepherd
        preset = await vmshepherd.preset_manager.get(preset)
        await preset.iaas.terminate_vm(vm_id)
        return 'OK'

    @enabled_checker
    async def get_vm_metadata(self, preset, vm_id):
        """ Get vm metadata

        :arg string preset: preset name
        :arg int vm_id: Vm's id

        """
        vmshepherd = self.request.app.vmshepherd
        preset = await vmshepherd.preset_manager.get(preset)
        vm_info = await preset.iaas.get_vm(vm_id)
        if self.request.remote != vm_info.ip:
            raise Exception("Calling for VM(ip:{}) info is not allowed from {}".format(vm_info.ip, self.request.remote))
        ret_info = copy.deepcopy(vm_info.metadata) if vm_info.metadata else {}
        ret_info['tags'] = vm_info.tags
        ret_info['timed_shutdown_at'] = vm_info.timed_shutdown_at
        return ret_info
