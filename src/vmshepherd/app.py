import asyncio
import logging
import os
from vmshepherd.drivers import Drivers
from vmshepherd.worker import Worker
from vmshepherd.www import WebServer


class VmShepherd:

    def __init__(self, config):
        self.config = config

        logger = logging.getLogger()
        log_level = self.config.get('log_level', 'info').upper()
        logger.setLevel(log_level)

        if logger.getEffectiveLevel() == logging.DEBUG:
            logging.debug('DEBUG mode enabled')

        self.root_dir = os.path.dirname(__file__)

        self.runtime_manager = Drivers.get('runtime', self.config['runtime'])

        self.preset_manager = Drivers.get(
            'presets', self.config['presets'],
            runtime=self.runtime_manager,
            defaults=self.config.get('defaults', {})
        )

        self.worker = Worker(self, 5, autostart=self.config.get('autostart', True))

        if self.config.get('web'):
            self.web = WebServer(
                self, self.config.get('port', 8888),
            )
            asyncio.ensure_future(self.web.start())

    async def run(self, run_once=False):
        if run_once:
            await self.worker.run_once()
        else:
            await self.worker.run_forever()
