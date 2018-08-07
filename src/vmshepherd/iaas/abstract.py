''' IaaS driver is responsible for communication with IaaS provider. To VmShepherd work,
driver should implement `create_vm`, `terminate_vms`, `list_vms` and `get_vm_info`.

Initialization - consider following config:

::

   iaas:
     driver: SomeIaaS
     auth_key: AAAA
     auth_secret: BBBB
     some_x: CCC

All params will be passed as config dict to the driver init:

'''
from .vm import Vm
from typing import Any, Dict, List


class AbstractIaasDriver:

    def __init__(self, config=None):
        pass

    async def create_vm(self, preset_name: str, image: str, flavor: str, security_groups: List=None,
                        userdata: Dict=None, key_name: str=None, availability_zone: str=None,
                        subnets: List=None) -> Any:
        """
        Create (boot) a new server.

        :arg string preset_name: Name of vm group where vm is created.
        :arg string image: Image name.
        :arg string flavor: Flavor (or instance_type in AWS) name.
        :arg list security_groups: A list of security group names.
        :arg dict userdata: A dict of arbitrary key/value metadata to store in grains.
        :arg string key_name: (optional extension) name of previously created
                      keypair to inject into the instance.
        :arg string availability_zone: Name of the availability zone for instance
                                  placement.
        :arg string subnets: List of the subnets for instance placement.

        Returns Any vm_id.
        """

        raise NotImplementedError

    async def list_vms(self, preset_name: str) -> List[Vm]:
        """
        List vms.

        :arg string preset_name: List VMs with name preset_name.

        Returns list of Vm objects.
        """

        raise NotImplementedError

    async def terminate_vm(self, vm_id: Any) -> None:
        """
        Terminates/discards vm.

        :arg string vm_id: Id Vm to terminate.
        """

        raise NotImplementedError

    async def get_vm(self, vm_id: Any) -> Vm:
        """
        Get vm info (with metadata and/or tags).

        :arg string vm_id: Id Vm to get.

        Returns list of Vm objects.
        """

        raise NotImplementedError

    def reconfigure(self, config):
        pass
