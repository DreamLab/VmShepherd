import aiohttp_jinja2
import jinja2
import os
import time
from .rpc_api import RpcApi
from aiohttp import web


class WebServer(web.Application):

    def __init__(self, vmshepherd, port=8888, panel=None, api=None):
        super().__init__()

        self.port = port
        self.vmshepherd = vmshepherd
        if panel:
            self.configure_panel()
        if api:
            self.configure_api()

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

    def configure_api(self):
        self.router.add_route('POST', '/api', RpcApi)

    async def start(self):
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
