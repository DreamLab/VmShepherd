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

    def create_preset(self, config):
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

        self._render_preset_userdata(config)
        
        return Preset(
            config['name'], config, runtime=self.runtime,
            iaas=iaas, healthcheck=healthcheck
        )

    def reload(self):
        raise NotImplementedError

    async def inject_preset_userdata(self, config, path):
        if 'userdata' not in config or not config['userdata']:
            return
        if config['userdata'].startswith('file://'):
            path = os.path.join(path, config['userdata'].replace('file://',''))
            config['userdata'] = await async_load_from_file(path)

    def _render_preset_userdata(self, config):
        tpl = Template(config['userdata'])
        config['userdata'] = tpl.render(**config)

