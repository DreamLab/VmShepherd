import asyncio
import logging
import os
from vmshepherd.drivers import Drivers
from vmshepherd.utils import gen_id, prefix_logging
from vmshepherd.worker import Worker
from vmshepherd.www import WebServer


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

        if self.config.get('web'):
            port = self.config.get('listen_port', 8888)
            logging.info('Starting server, listening on %s.', port)
            self.web = WebServer(self, port)
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
