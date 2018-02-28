import os
from .abstract import AbstractConfigurationDriver
from vmshepherd.utils import async_load_from_yaml_file


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
                preset = await async_load_from_yaml_file(item.path)
                if preset is not None:
                    await self.inject_preset_userdata(preset, self._path)
                    presets[preset_name] = self.create_preset(preset)
        self._presets = presets
