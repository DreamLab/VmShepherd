import aiohttp_jinja2
import jinja2
import os
from aiohttp import web
from time import strftime
from datetime import datetime

def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
        return datetime.fromtimestamp(int(value)).strftime(format)

class WebServer(web.Application):

    def __init__(self, vmshepherd, port=8888):
        super().__init__()

        self.port = port
        self.vmshepherd = vmshepherd

        webroot = os.path.dirname(__file__)

        self.template_path = os.path.join(webroot, 'templates')
        aiohttp_jinja2.setup(
            self, loader=jinja2.FileSystemLoader(self.template_path),
            filters={'datetimeformat': datetimeformat}
        )

        self['static_root_url'] = '/static'
        self.router.add_view('/', Panel)
        self.router.add_static(
            '/static/', path=os.path.join(webroot, 'static'), name='static'
        )

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
        for name in presets:
            preset = await vms.preset_manager.get(name)
            data['presets'][name] = {
                'preset': preset,
                'vms': await preset.list_vms()
            }
        return data
