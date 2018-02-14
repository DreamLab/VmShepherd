import logging
import os
from vmshepherd.driver import Driver
from vmshepherd.worker import Worker


class VmShepherd:

    def __init__(self, config):
        self.config = config

        logger = logging.getLogger()
        log_level = self.config.get('log_level', 'info').upper()
        logger.setLevel(log_level)

        if logger.getEffectiveLevel() == logging.DEBUG:
            logging.debug('DEBUG mode enabled')

        self.root_dir = os.path.dirname(__file__)

        self.runtime_manager = Driver.get('runtime', self.config['runtime'])

        self.preset_manager = Driver.get('presets', self.config['presets'])
        self.preset_manager.set_defaults(self.config.get('defaults', {}))

        self.worker = Worker(self, 5, autostart=self.config.get('autostart', True))

    async def run(self, run_once=False):
        if run_once:
            await self.worker.run_once()
        else:
            await self.worker.run_forever()
