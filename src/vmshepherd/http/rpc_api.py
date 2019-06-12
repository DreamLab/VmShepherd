import copy
from aiohttp_jsonrpc import handler
from functools import wraps


class RpcApi(handler.JSONRPCView):
    """
    RPC Api to manage virtual machines
    """

    def __init__(self, allowed_methods=None):
        self.METHOD_PREFIX = ''
        self.allowed_methods = allowed_methods

    async def handler(self, request):
        self._request = request
        return await self

    def enabled_checker(func):
        """ Access decorator which checks if a RPC method is enabled by our configuration
        """

        @wraps(func)
        def wrap(self, *args, **kwargs):
            if self.allowed_methods and isinstance(self.allowed_methods, list) and func.__name__ not in self.allowed_methods:
                raise Exception("Method {} is disabled".format(func.__name__))
            return func(self, *args, **kwargs)

        return wrap

    @enabled_checker
    async def list_presets(self):
        """
        Listing presets

        :return:  (list of presets)

        :rtype: list

        Sample response:
            ``["preset1", "preset2"]``
        """
        presets = await self.request.app.vmshepherd.preset_manager.list_presets()
        return list(presets.keys())

    @enabled_checker
    async def list_vms(self, preset):
        """ Listing virtual machines in a given preset

        :arg string preset: preset name
        :return:  (Size of a preset, list of virtual machines)

            - first element of a tuple is a size of virtual machines in a preset
            - second element is a dict which contains all Virtual Machines, where every element of this dict looks like that:

              ``{ "VIRTUAL_MACHINE_ID": { "ip": "IP_ADDR", "state": "VM_STATE" }``

        :rtype: tuple

        Sample response:
            ``( 1, {'180aa486-ee46-4628-ab1c-f4554b63231': {'ip': '172.1.1.2', 'state': 'running'}} )``
        """
        vmshepherd = self.request.app.vmshepherd
        preset = vmshepherd.preset_manager.get_preset(preset)
        await preset.refresh_vms()
        result_vms = {vm.id: {'ip': vm.ip[0], 'state': vm.state.value} for vm in preset.vms}
        return preset.count, result_vms

    @enabled_checker
    async def terminate_vm(self, preset, vm_id):
        """ Discard vm in specified preset

        :arg string preset: preset name
        :arg int vm_id: Virtual Machine id
        :return: 'OK'

        Sample response:
           ``OK``
        """
        vmshepherd = self.request.app.vmshepherd
        preset = vmshepherd.preset_manager.get_preset(preset)
        await preset.iaas.terminate_vm(vm_id)
        return 'OK'

    @enabled_checker
    async def get_vm_metadata(self, preset, vm_id):
        """ Get vm metadata

        :arg string preset: preset name
        :arg int vm_id: Virtual Machine id
        :return:  Metadata for Virtual Machine
        :rtype: dict

        Sample response:
           ``{ 'time_shutdown' : "12312312321' }``
        """
        vmshepherd = self.request.app.vmshepherd
        preset = vmshepherd.preset_manager.get_preset(preset)
        vm_info = await preset.iaas.get_vm(vm_id)
        ret_info = copy.deepcopy(vm_info.metadata) if vm_info.metadata else {}
        ret_info['tags'] = vm_info.tags
        ret_info['iaas_shutdown'] = vm_info.timed_shutdown_at
        return ret_info

    @enabled_checker
    async def get_vm_ip(self, preset_name, vm_id):
        """ Get vm ip

        :arg string preset: preset name
        :arg int vm_id: Virtual Machine id
        :return:  Vm Ip
        :rtype: string
        """
        vmshepherd = self.request.app.vmshepherd
        preset = vmshepherd.preset_manager.get_preset(preset_name)
        # check in cache
        for vm in preset.vms:
            if vm_id == vm.id:
                return {'vm_ip': vm.ip[0]}
        # retrieve real time data
        vm_info = await preset.iaas.get_vm(vm_id)
        return {
            'vm_ip': vm_info.ip[0]
        }
