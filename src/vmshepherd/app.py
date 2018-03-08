import asyncio
import logging
import os
from vmshepherd.drivers import Drivers
from vmshepherd.http import WebServer
from vmshepherd.utils import gen_id, prefix_logging
from vmshepherd.worker import Worker


class VmShepherd:

    def __init__(self, config):
        self.config = config
        self.root_dir = os.path.dirname(__file__)
        self.instance_id = gen_id(rnd_length=5)
        logging.info("Starting")
        self.setup_logging()

        self.runtime_manager = Drivers.get(
            'runtime', self.config['runtime'],
            instance_id=self.instance_id
        )

        self.preset_manager = Drivers.get(
            'presets', self.config['presets'],
            runtime=self.runtime_manager,
            defaults=self.config.get('defaults', {})
        )

        self.worker = Worker(
            runtime=self.runtime_manager, presets=self.preset_manager,
            interval=int(self.config.get('worker_interval', 5)),
            autostart=self.config.get('autostart', True)
        )

        http = self.config.get('http', None)
        if http:
            panel = http.get('panel', None)
            rpc_api = http.get('rpc_api', False)
            port = http.get('listen_port', 8888)
            logging.info('Starting server, listening on %s.', port)
            self.web = WebServer(self, port, panel, rpc_api)
            asyncio.ensure_future(self.web.start())

    async def run(self, run_once=False):
        if run_once:
            await self.worker.run_once()
        else:
            await self.worker.run_forever()

    def setup_logging(self):
        logger = logging.getLogger()
        log_level = self.config.get('log_level', 'info').upper()
        logger.setLevel(log_level)
        if logger.getEffectiveLevel() == logging.DEBUG:
            logging.debug('DEBUG mode enabled')
        prefix_logging(self.instance_id)

    def reload(self, with_config=None):
        self.config = with_config or self.config
        self.runtime_manager.reconfigure(self.config.get('runtime'))
        self.preset_manager.reconfigure(self.config.get('presets'), self.config.get('defaults'))
        Drivers.flush()
