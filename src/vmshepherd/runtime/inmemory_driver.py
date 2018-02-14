import asyncio
import logging
from .abstract import AbstractRuntimeData


class InMemoryDriver(AbstractRuntimeData):
    ''' Simple in-memory driver for runtime data and locks managment.
    '''

    def __init__(self):
        self._storage = {}
        self._locks = {}

    async def lock_preset(self, preset_name, timeout=1):
        if not self._locks.get(preset_name):
            self._locks[preset_name] = asyncio.Lock()
        fut = self._locks[preset_name].acquire()
        try:
            await asyncio.wait_for(fut, timeout)
            return True
        except asyncio.TimeoutError:
            return False
        except Exception:
            logging.exception('Lock %s failed.', preset_name)
            return False

    async def unlock_preset(self, preset_name):
        try:
            self._locks[preset_name].release()
        except RuntimeError:
            logging.exception('Unlock %s failed.', preset_name)

    async def set_preset_data(self, preset_name, data):
        self._storage[preset_name] = data

    async def get_preset_data(self, preset_name):
        return self._storage.get(preset_name, {})
