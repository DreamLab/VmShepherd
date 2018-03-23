import asyncio
import logging
from .abstract import AbstractRuntimeData


class InMemoryDriver(AbstractRuntimeData):
    ''' Simple in-memory driver for runtime data and locks managment.
    '''

    def __init__(self, instance_id, config=None):
        super().__init__(instance_id, config)
        self._storage = {}
        self._locks = {}

    async def _acquire_lock(self, name, timeout=1):
        if not self._locks.get(name):
            self._locks[name] = asyncio.Lock()
        fut = self._locks[name].acquire()
        try:
            await asyncio.wait_for(fut, timeout)
            return True
        except asyncio.TimeoutError:
            return False
        except Exception:
            logging.exception('Lock %s failed.', name)
            return False

    async def _release_lock(self, name):
        try:
            self._locks[name].release()
        except RuntimeError:
            logging.exception('Unlock %s failed.', name)

    async def _set_preset_data(self, preset_name, data):
        self._storage[preset_name] = data

    async def _get_preset_data(self, preset_name):
        return self._storage.get(preset_name, {})
