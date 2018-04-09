import aiohttp_jinja2
import jinja2
import logging
import os
import time
from .rpc_api import RpcApi
from aiohttp import web


class WebServer(web.Application):

    def __init__(self, vmshepherd, config=None):
        super().__init__()
        self.port = config.get('listen_port', 8888)
        panel_conf = config.get('panel')
        api_conf = config.get('api')

        self.vmshepherd = vmshepherd
        panel_enabled = panel_conf.get('enabled', True) if isinstance(panel_conf, dict) else panel_conf
        if panel_enabled:
            self.configure_panel()
        api_enabled = api_conf.get('enabled', True) if isinstance(api_conf, dict) else api_conf
        if api_enabled:
            allowed_methods = None
            if isinstance(api_conf, dict):
                allowed_methods = api_conf.get('allowed_methods')
            self.configure_api(allowed_methods)

    def configure_panel(self):
        webroot = os.path.dirname(__file__)

        self.template_path = os.path.join(webroot, 'templates')
        aiohttp_jinja2.setup(
            self, loader=jinja2.FileSystemLoader(self.template_path),
            filters={'sorted': sorted, 'int': int}
        )

        self['static_root_url'] = '/static'
        self.router.add_view('/', Panel)
        self.router.add_static(
            '/static/', path=os.path.join(webroot, 'static'), name='static'
        )

    def configure_api(self, allowed_methods=None):
        logging.info("Api allowed methods: %s", allowed_methods if allowed_methods else 'all')
        self.router.add_route('POST', '/api', RpcApi(allowed_methods).handler)

    async def start(self):
        logging.info('Starting server, listening on %s.', self.port)
        runner = web.AppRunner(self)
        await runner.setup()
        site = web.TCPSite(runner, '', self.port)
        await site.start()


class Panel(web.View):

    @aiohttp_jinja2.template('index.html.jinja2')
    async def get(self):
        vms = self.request.app.vmshepherd
        data = {'presets': {}, 'config': vms.config}
        await vms.preset_manager.reload()
        presets = await vms.preset_manager.get_presets_list()
        runtime = vms.runtime_manager
        for name in presets:
            preset = await vms.preset_manager.get(name)
            data['presets'][name] = {
                'preset': preset,
                'vms': await preset.list_vms(),
                'runtime': await runtime.get_preset_data(name),
                'vmshepherd_id': vms.instance_id,
                'now': time.time()
            }
        return data
