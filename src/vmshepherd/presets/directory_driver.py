import aiofiles
import logging
import os
import yaml
from .abstract import AbstractConfigurationDriver


class DirectoryDriver(AbstractConfigurationDriver):

    def __init__(self, path, runtime, defaults):
        super().__init__(runtime, defaults)
        self._presets = {}
        self._path = path

    async def get(self, preset_name):
        return self._presets[preset_name]

    async def get_presets_list(self):
        return list(self._presets.keys())

    async def reload(self):
        presets = {}
        for item in os.scandir(self._path):
            if os.path.isfile(item.path):
                preset_name = item.name.replace('.conf', '')
                preset = await self._load_from_file(item.path)
                if preset is not None:
                    presets[preset_name] = self.create_preset(preset_name, preset)
        self._presets = presets

    async def _load_from_file(self, fn):
        try:
            async with aiofiles.open(fn, mode='r') as f:
                contents = await f.read()
                data = yaml.load(contents)

            self.validate_preset(data)
            return data
        except Exception:
            logging.exception('DirectoryDriver: Error loading %s', fn)
