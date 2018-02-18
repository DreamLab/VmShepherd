''' Abstract of runtime data storage.

Storage is used to keep runtime data like fail, try count.
It also should provide lock mechanism - in multiinstance deployment, a preset should be managed by the only one VmShepherd at a time.

'''


class AbstractRuntimeData:


    async def acquire_lock(self, name: str) -> bool:
        ''' Locks preset during manage process, any other VMgr instance won't disrubt it.

        If lock was acquired it should return True, otherwise False.
        '''
        raise NotImplementedError

    async def release_lock(self, name: str) -> None:
        ''' Unlocks presets, other VMgr instance will be able to manage it.

        :arg string preset_name: Preset name
        '''
        raise NotImplementedError

    async def set_preset_data(self, preset_name: str, data: dict) -> None:
        ''' Saves preset's runtime data - fail counters, times

        :arg string preset_name: Preset name
        :arg dict data: Set of counters and other volatile data
        '''
        raise NotImplementedError

    async def get_preset_data(self, preset_name: str) -> dict:
        ''' Gets preset's runtime data eg. fail counters, times

        :arg string preset_name: Preset name
        '''
        raise NotImplementedError
