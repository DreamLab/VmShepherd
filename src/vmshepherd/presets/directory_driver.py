import aiofiles
import logging
import os
import yaml
from .abstract import AbstractConfigurationDriver


# TODO: probably it would be better to separate list from preset data
#       This will make a lot easier to pass runtime data.
#       The change requires modification in worker, preset abstract API and a Preset class.


class DirectoryDriver(AbstractConfigurationDriver):

    def __init__(self, path):
        self._presets = {}
        self._path = path

    async def get_presets_configuration(self):
        await self.reload()
        return self._presets

    async def get_preset(self, name):
        await self.reload()
        return self._presets.get(name)

    async def get_presets_list(self):
        await self.reload()
        return list(self._presets.keys())

    async def reload(self):
        presets = {}
        for item in os.scandir(self._path):
            if os.path.isfile(item.path):
                preset_name = item.name.replace('.conf', '')
                preset = await self._load_from_file(item.path)
                if preset is not None:
                    presets[preset_name] = self.prepare_preset(preset_name, preset)
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
