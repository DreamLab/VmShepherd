'''
'''
import os
from .preset import Preset
from jinja2 import Template
from vmshepherd.drivers import Drivers
from vmshepherd.utils import get_merged_dict_recursively, async_load_from_file


class AbstractConfigurationDriver:

    def __init__(self, runtime, defaults):
        self.runtime = runtime
        self.defaults = defaults
        self._presets = {}


    def get_preset(self, preset_name):
        return self._presets[preset_name]

    def list_presets(self, fresh=True):
        if fresh:
            async self.refresh_presets()
        return self._presets

    async def refresh_presets(self):
        fresh_presets = set(await self._list())
        loaded_presets = set(self._presets.keys())
        to_add = fresh_presets - loaded_presets
        to_remove = loaded_presets
        for name in to_add:
            self._presets[name] = Preset(name)
        for name in to_remove:
            del self._presets[name]

    async def _get(self, preset_name):
        raise NotImplementedError

    async def _list(self):
        raise NotImplementedError

    async def reload(self):
        raise NotImplementedError

    def _get_preset_create_preset(self, config):
        iaas_cfg = get_merged_dict_recursively(
            self.defaults.get('iaas', {}), config.get('iaas', {})
        )
        iaas = Drivers.get('iaas', iaas_cfg)
        config['iaas'] = iaas_cfg

        healthcheck_cfg = get_merged_dict_recursively(
            self.defaults.get('healthcheck', {}), config.get('healthcheck', {})
        )
        healthcheck = Drivers.get('healthcheck', healthcheck_cfg)
        config['healthcheck'] = healthcheck_cfg

        if 'userdata' in config:
            self._render_preset_userdata(config)
        return Preset(
            config['name'], config, runtime=self.runtime,
            iaas=iaas, healthcheck=healthcheck
        )

    def reconfigure(self, config, defaults):
        self.defaults = defaults

    async def inject_preset_userdata(self, config, path):
        if 'userdata' not in config or not config['userdata']:
            return
        if config['userdata'].startswith('file://'):
            path = os.path.join(path, config['userdata'].replace('file://', ''))
            config['userdata'] = await async_load_from_file(path)

    def _render_preset_userdata(self, config):
        tpl = Template(config['userdata'])
        config['userdata'] = tpl.render(**config)
