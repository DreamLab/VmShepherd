''' Preset configuration (or sometime called Preset store) is a mechanism to fetch and prepare cluster definition/spec for VmShepherd.
Preset configuration driver should implement `_get_preset_spec` and `_list`.

Initialization - consider following config:

::

   presets:
     driver: SomeC
     param1: AAAA
     param2: BBBB
     some_x: CCC

All params will be passed as config dict to the driver init:

'''
import os
from .preset import Preset
from jinja2 import Template
from vmshepherd.drivers import Drivers
from vmshepherd.utils import get_merged_dict_recursively, async_load_from_file
from vmshepherd.errors import PresetNotFound

class AbstractConfigurationDriver:

    def __init__(self, runtime, defaults):
        self.runtime = runtime
        self.defaults = defaults
        self._presets = None

    async def _get_preset_spec(self, preset_name: str):
        """ Returns configuration of specific preset

        :arg string preset_name: Name of the preset

        Returns dict - preset configuration

        Example configuration:

        ::

            name: 'C_DEV-app-dev'
            count: 1
            flavor: m1.small
            image: ubuntu-xenial
            manage_interval: 0    # interval in seconds
            manage_expire: 120    # max time of manage (after this time another manage can be scheduled) - expiration in seconds
            network:
              security_groups:
                - PaaS PrivateCloud
                - paas
              availability_zone: nova
              subnet:
                - pl-krk-2-something
            iaas:
              project_name: PROJECT_NAME
              project_domain_name: PROJECT_DOMAIN
            userdata: ''
            meta_tags: {}

        """
        raise NotImplementedError

    async def _list(self):
        """ Returns list names of presets to manage

        Returns list of string - just names. Further information will be collected with given name and `_get_preset_spec` method.
        """
        raise NotImplementedError

    def get_preset(self, preset_name):
        try:
            return self._presets[preset_name]
        except KeyError:
            raise PresetNotFound(preset_name)

    async def list_presets(self, refresh=True):
        if refresh or self._presets is None:
            await self.refresh_presets()
        return self._presets

    async def refresh_presets(self):
        if self._presets is None:
            self._presets = {}

        fresh_presets = set(await self._list())
        loaded_presets = set(self._presets.keys())
        to_add = fresh_presets - loaded_presets
        to_remove = loaded_presets - fresh_presets

        for name in to_add:
            self._presets[name] = Preset(name)
        for name in to_remove:
            del self._presets[name]

        for name, preset in self._presets.items():
            spec = await self._get_preset_spec(name)
            params = await self._prepare_preset_params(preset, spec)
            preset.configure(**params)

    async def _prepare_preset_params(self, preset, config):
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
            await self._inject_preset_userdata(config)
            self._render_preset_userdata(config)

        return {
            'config': config, 'runtime_mgr': self.runtime,
            'iaas': iaas, 'healthcheck': healthcheck
        }

    def reconfigure(self, config, defaults):
        self.defaults = defaults

    async def _inject_preset_userdata(self, config):
        if 'userdata' not in config or not config['userdata']:
            return
        root = config.get('userdata_source_root', '')

        if config['userdata'].startswith('file://'):
            path = os.path.join(root, config['userdata'].replace('file://', ''))
            config['userdata'] = await async_load_from_file(path)

    def _render_preset_userdata(self, config):
        tpl = Template(config['userdata'])
        config['userdata'] = tpl.render(**config)
