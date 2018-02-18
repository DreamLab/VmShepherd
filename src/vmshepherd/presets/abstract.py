'''
'''
from .preset import Preset
from vmshepherd.drivers import Drivers
from vmshepherd.utils import get_merged_dict_recursively


class AbstractConfigurationDriver:

    def __init__(self, runtime, defaults):
        self.runtime = runtime
        self.defaults = defaults

    async def get(self, preset_name):
        raise NotImplementedError

    async def get_presets_list(self):
        raise NotImplementedError

    def validate_preset(self, preset):
        # TODO
        return True

    def create_preset(self, name, config):
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

        return Preset(
            name, config, runtime=self.runtime,
            iaas=iaas, healthcheck=healthcheck
        )

    def reload(self):
        raise NotImplementedError
