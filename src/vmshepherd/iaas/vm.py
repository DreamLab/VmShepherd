import datetime
import logging
import time
from enum import Enum


class VmState(Enum):
    """
    Standard states for a node

    :var RUNNING: Vm is running.
    :var TERMINATED: Vm is terminated. This node can't be started later on.
    :var PENDING: Vm is pending.
    :var ERROR: Vm is an error state. Usually no operations can be performed
                 on the node once it ends up in the error state.
    :var UNKNOWN: Vm state is unknown.
    """

    RUNNING = 'running'
    NEARBYSHUTDOWN = 'nearbyshutdown'
    AFTERTIMESHUTDOWN = 'aftertimeshutdown'
    TERMINATED = 'terminated'
    PENDING = 'pending'
    UNKNOWN = 'unknown'
    ERROR = 'error'


class Vm:
    """
    Vm class definition.
    Define API to implement in specific IaasDrivers like Openstack or EC2.
    """

    def __init__(self, manager, id, name, ip, created, state=VmState.UNKNOWN, metadata=None, tags=None,
                 flavor=None, image=None, timed_shutdown_at=None):

        """ Init for VM.

        :arg AbstractIaasDriver manager: class implementing Vm actions.
        :arg string id: Vm uniq id.
        :arg string name: Vm name/preset_name ??.
        :arg list ip: Vm ip list.
        :arg datetime/int created: Timestamp when Vm was created
        :arg VmState state: Vm state.
        :arg dict metadata: Vm metadata.
        :arg list tags: Vm tags.
        :arg string flavor: Vm flavor name.
        :arg string image: Vm image name.
        :arg int timed_shutdown_at: Timestamp when VM will be terminated.
        """

        self.manager = manager
        self.id = id
        self.name = name
        self.ip = ip
        self.state = state
        self.metadata = metadata
        self.tags = tags
        self.flavor = flavor
        self.image = image
        self.timed_shutdown_at = timed_shutdown_at
        if isinstance(created, datetime.datetime):
            self.created = created
        elif isinstance(created, (int, float)):
            self.created = datetime.datetime.fromtimestamp(created)
        else:
            # actually it's not so crucial to fail
            self.created = time.time()

    def __str__(self):
        return f'VM id={self.id} preset={self.name} state={self.state} ip={self.ip}'

    def __eq__(self, other):
        for prop in ('id', 'ip', 'name', 'flavor', 'image'):
            if getattr(self, prop) != getattr(other, prop):
                return False
        return True

    def __gt__(self, other):
        return self.created > other.created

    def __hash__(self):
        return hash(self.id)

    async def terminate(self):
        """ Terminate vm.

        """
        logging.debug('Terminate: %s', self)
        return await self.manager.terminate_vm(self.id)

    def is_running(self):
        return self.state in (VmState.RUNNING, VmState.NEARBYSHUTDOWN)

    def is_dead(self):
        return self.state in (VmState.TERMINATED, VmState.ERROR, VmState.AFTERTIMESHUTDOWN)

    def get_state(self):
        return self.state.value
