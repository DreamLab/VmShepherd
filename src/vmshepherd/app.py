import logging
import os
from vmshepherd.drivers import Drivers
from vmshepherd.utils import gen_id, prefix_logging
from vmshepherd.worker import Worker


class VmShepherd:

    def __init__(self, config):
        self.config = config
        self.root_dir = os.path.dirname(__file__)
        self.instance_id = gen_id(rnd_length=5)

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

        self.worker = Worker(self, 5, autostart=self.config.get('autostart', True))

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
