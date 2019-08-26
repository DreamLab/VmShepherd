import logging
from .abstract import AbstractIaasDriver
from vmshepherd.errors import IaaSError
from .vm import Vm, VmState
from vmshepherd.utils import next_id, add_async_delay


class DummyIaasUserExc(IaaSError):
    def __init__(self, message, details):
        super().__init__(message, details)


class DummyIaasVmNotFound(DummyIaasUserExc):
    def __init__(self):
        super().__init__('VMNOTFOUND', 'Vm Not Found')


class DummyIaasDriver(AbstractIaasDriver):
    """ DummyIaasDriver - mainly for test purposes.

    Implements required API of fake-in-memory-iaas (dict).
    To mimic communication with external service additional delay has been introduced.

    """

    def __init__(self, config=None):
        """
        Init: create list of vms.
        """
        self._vms = {}
        self._id_it = next_id()

    @add_async_delay
    async def create_vm(self, *, preset_name, image, flavor, security_groups=None,
                        userdata=None, key_name=None, availability_zone=None,
                        subnet=None):
        """
        Dummy create_vm func.
        """
        info = {
            'id': next(self._id_it),
            'name': preset_name,
            'ip': ['127.0.0.1'],
            'created': 0,
            'state': VmState.RUNNING,
            'flavor': flavor,
            'image': image,
            'metadata': {'test-meta': 'abctest'},
            'timed_shutdown_at': 1522753481,
            'tags': ['a-tag', 'b-tag', 'c-tag']
        }
        logging.debug('Prepare vm: %s', info)
        vm = Vm(**info)
        self._vms[vm.id] = vm
        logging.debug('Create: %s', vm)
        return None

    @add_async_delay
    async def list_vms(self, preset_name):
        """Dummy list_vms func"""
        return list(vm for vm in self._vms.values() if vm.name == preset_name)

    @add_async_delay
    async def terminate_vm(self, vm_id):
        """ Dummy terminate_vm func """
        if vm_id not in self._vms:
            raise DummyIaasVmNotFound()
        del self._vms[vm_id]
        return None

    @add_async_delay
    async def get_vm(self, vm_id):
        """ Dummy get_vm func """
        if vm_id not in self._vms:
            raise DummyIaasVmNotFound()
        return self._vms[vm_id]
