''' Runtime manager or runtime data storage stores intermediate states of VmShepherd cycles
that need to be shared across multiple instances of application like:
 - healthchecks status,
 - try counts
 - time and dates of last manage

and locking mechanism.

The locking mechanism guarantees a preset is managed by one instance at a time.

Initialization - consider following config:

::

   runtime:
     driver: SomeHC
     param1: AAAA
     param2: BBBB
     some_x: CCC

All params will be passed as config dict to the driver init:
'''
import time


# TODO: it should be @dataclass
class Data:

    def __init__(self, d):
        self.last_managed = d.get('last_managed', {}).get('time', 0)
        self.last_managed_by = d.get('last_managed', {}).get('id', '')
        self.failed_checks = d.get('failed_checks', {})
        self.iaas = d.get('iaas', {})

    def dump(self):
        return {'iaas': self.iaas, 'failed_checks': self.failed_checks}

    def __str__(self):
        return str(self.__dict__)


class AbstractRuntimeData:

    def __init__(self, instance_id, config=None):
        self.instance_id = instance_id
        self.preset_lock_ttl = config.get('preset_lock_ttl', 60) if config else 60

    async def _acquire_lock(self, name: str) -> bool:
        ''' Locks preset during manage process, any other VMgr instance won't disrubt it.

        :arg string name: Lock name in particular preset name.

        If lock was acquired it should return True, otherwise False.
        '''
        raise NotImplementedError

    async def _release_lock(self, name: str) -> None:
        ''' Unlocks presets, other VMgr instance will be able to manage it.

        :arg string name: Lock name in particular preset name.
        :arg string preset_name: Preset name
        '''
        raise NotImplementedError

    async def _set_preset_data(self, preset_name: str, data: dict) -> None:
        ''' Saves preset's runtime data - fail counters, times

        :arg string preset_name: Preset name
        :arg dict data: Set of counters and other volatile data
        '''
        raise NotImplementedError

    async def _get_preset_data(self, preset_name: str) -> dict:
        ''' Gets preset's runtime data eg. fail counters, times

        :arg string preset_name: Preset name
        '''
        raise NotImplementedError

    async def get_preset_data(self, name):
        response = await self._get_preset_data(name)
        return Data(response)

    async def set_preset_data(self, name, data):
        commit = {
            'last_managed': {
                'time': time.time(),
                'id': self.instance_id
            }
        }
        commit.update(data.dump())
        return await self._set_preset_data(name, commit)

    async def acquire_lock(self, name):
        return await self._acquire_lock(name)

    async def release_lock(self, name):
        return await self._release_lock(name)

    def reconfigure(self, config):
        pass
