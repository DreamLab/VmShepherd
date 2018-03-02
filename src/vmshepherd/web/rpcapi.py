import logging
from aiohttp_jsonrpc import handler


class RpcApi(handler.JSONRPCView):

    TIMEDSHUTDOWN = 'timed-shutdown'
    DISCARD = 'discard'

    async def rpc_list_vms(self, preset):
        """ List VMs for preset, with runtime states.

        Returns expected VMs count and dict with runtime VMs data.

        :arg string preset: preset name (e.g. C_DEV-apps-dev)
        """
        vmshepherd = self.request.app.vmshepherd
        await vmshepherd.preset_manager.reload()
        preset = await vmshepherd.preset_manager.get(preset)
        vms = await preset.list_vms()
        result_vms = {}
        for vm in vms:
            result_vms[vm.id] = {
                'iaas_vm_ip': vm.ip[0],
                'state': vm.state.value
                }
        return preset.count, result_vms

    async def rpc_terminate_vm(self, preset, vm_id):
        """Discard vm in specified preset

        :arg string preset: preset name
        :arg int vm_id: Vm's id

        Returns string OK
        """
        vmshepherd = self.request.app.vmshepherd
        preset = await vmshepherd.preset_manager.get(preset)
        await preset.iaas.terminate_vm(vm_id)
        return 'OK'
