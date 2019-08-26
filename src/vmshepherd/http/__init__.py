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
        allowed_methods = config.get('api', {}).get('allowed_methods')
        self.vmshepherd = vmshepherd
        self.configure_panel()
        self.configure_api(allowed_methods)

    def configure_panel(self):
        """
        Configure templates and routing
        """
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
        """
        Configure route for api
        :arg list allowed_methods: List of a methods which are turned on in our api
        """
        self.router.add_route('POST', '/api', RpcApi(allowed_methods).handler)

    async def start(self):
        """
        Initialize and start WebServer
        """
        logging.info('Starting server, listening on %s.', self.port)
        runner = web.AppRunner(self)
        await runner.setup()
        site = web.TCPSite(runner, '', self.port)
        await site.start()


class Panel(web.View):

    @aiohttp_jinja2.template('index.html.jinja2')
    async def get(self):
        """
        Inject all preset data to Panel and Render a Home Page
        """
        shepherd = self.request.app.vmshepherd
        data = {'presets': {}, 'config': shepherd.config}
        presets = await shepherd.preset_manager.list_presets()
        runtime = shepherd.runtime_manager
        for name in presets:
            preset = shepherd.preset_manager.get_preset(name)
            runtime_data = await runtime.get_preset_data(name)
            data['presets'][name] = {
                'preset': preset,
                'runtime': runtime_data,
                'vmshepherd_id': shepherd.instance_id,
                'now': time.time()
            }
        return data
