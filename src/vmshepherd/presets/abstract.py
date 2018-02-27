'''
'''
import os
from jinja2 import Template
from .preset import Preset
from vmshepherd.drivers import Drivers
from vmshepherd.utils import get_merged_dict_recursively, async_load_from_file


class AbstractConfigurationDriver:

    def __init__(self, runtime, defaults):
        self.runtime = runtime
        self.defaults = defaults

    async def get(self, preset_name):
        raise NotImplementedError

    async def get_presets_list(self):
        raise NotImplementedError

    async def create_preset(self, config, base_path):
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

        await self._load_preset_userdata(config, base_path)

        return Preset(
            config['name'], config, runtime=self.runtime,
            iaas=iaas, healthcheck=healthcheck
        )

    def reload(self):
        raise NotImplementedError

    async def _load_preset_userdata(self, config, base_path):
        if config['userdata'] and config['userdata'].startswith('file://'):
            path = os.path.join(base_path, config['userdata'].replace('file://',''))
            config['userdata'] = await async_load_from_file(path)

        if config['meta_tags']:
            tpl = Template(config['userdata'])
            config['userdata'] = tpl.render(**config['meta_tags'])

