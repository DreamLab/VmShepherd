from aiohttp_jsonrpc import handler


class RpcApi(handler.JSONRPCView):

    def __init__(self, request):
        super().__init__(request)
        self.METHOD_PREFIX = ''

    async def list_vms(self, preset):
        """ List VMs for preset, with runtime states.

        :arg string preset: preset name (e.g. C_DEV-apps-dev)
        :returns: expected VMs count and dict with runtime VMs data.

        """
        vmshepherd = self.request.app.vmshepherd
        await vmshepherd.preset_manager.reload()
        preset = await vmshepherd.preset_manager.get(preset)
        vms = await preset.list_vms()
        result_vms = {vm.id: {'ip': vm.ip[0], 'state': vm.state.value} for vm in vms}
        return preset.count, result_vms

    async def terminate_vm(self, preset, vm_id):
        """Discard vm in specified preset

        :arg string preset: preset name
        :arg int vm_id: Vm's id
        :returns: string OK

        """
        vmshepherd = self.request.app.vmshepherd
        preset = await vmshepherd.preset_manager.get(preset)
        await preset.iaas.terminate_vm(vm_id)
        return 'OK'
