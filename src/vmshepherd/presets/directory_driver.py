import os
from .abstract import AbstractConfigurationDriver
from vmshepherd.utils import async_load_from_yaml_file


class DirectoryDriver(AbstractConfigurationDriver):

    def __init__(self, config, runtime, defaults):
        super().__init__(runtime, defaults)
        self._presets = {}
        self._path = config['path']

    async def _get_preset_spec(self, preset_name: str):
        return self._specs[preset_name]

    async def _list(self):
        await self._reload()
        return self._specs.keys()

    async def _reload(self):
        _tmp_specs = {}
        for item in os.scandir(self._path):
            if os.path.isfile(item.path) and item.path.endswith('.conf'):
                config = await async_load_from_yaml_file(item.path)
                config['name'] = preset_name = f"{config['name']}"
                config['userdata_source_root'] = self._path
                if 'meta_tags' not in config:
                    config['meta_tags'] = {}
                _tmp_specs[preset_name] = config
        self._specs = _tmp_specs

    def reconfigure(self, config, defaults):
        super().reconfigure(config, defaults)
        self._path = config.get('path', self._path)
