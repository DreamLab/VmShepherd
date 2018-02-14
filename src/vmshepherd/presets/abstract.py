'''
'''
from .preset import Preset
from vmshepherd.driver import Driver
from vmshepherd.utils import update_dict_recursively


class AbstractConfigurationDriver:

    def set_defaults(self, data):
        self.defaults = data

    async def get_presets_configuration(self, preset):
        raise NotImplementedError

    def validate_preset(self, preset):
        # TODO
        return True

    def prepare_preset(self, name, config):
        iaas_cfg = update_dict_recursively(
            self.defaults.get('iaas', {}), config.get('iaas', {})
        )
        iaas = Driver.get('iaas', iaas_cfg)
        config['iaas'] = iaas_cfg

        healthcheck_cfg = update_dict_recursively(
            self.defaults.get('healthcheck', {}), config.get('healthcheck', {})
        )
        healthcheck = Driver.get('healthcheck', healthcheck_cfg)
        config['healthcheck'] = healthcheck_cfg

        return Preset(name, config, iaas=iaas, healthcheck=healthcheck)

    def reload(self):
        raise NotImplementedError
