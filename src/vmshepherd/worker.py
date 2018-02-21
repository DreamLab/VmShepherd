import asyncio
import logging
import time


class Worker:

    ERROR = 'ERROR'
    OK = 'OK'

    def __init__(self, app, interval=1, autostart=True):
        self.presets = app.preset_manager
        self.runtime = app.runtime_manager
        self._interval = interval
        self._running = False
        self._start_time = 0
        if autostart:
            asyncio.ensure_future(self.run_forever())

    async def run_forever(self):
        while True:
            await self.run_once()
            await asyncio.sleep(self._interval)

    async def run_once(self):
        if self._running:
            logging.info('Already running since %s', self._start_time)
            return
        self._running = True

        self._start_time = time.time()
        logging.info('VmShepherd start cycle...')

        result, cnt_presets, cnt_failed_presets = self.ERROR, -1, -1
        try:
            result, cnt_presets, cnt_managed, cnt_failed_presets = await self._manage()
        except Exception:
            logging.exception('Error while running')
        finally:
            logging.info(
                'VmShepherd end cycle result=%s presets=%s managed=%s failed_presets=%s time=%.2f',
                result, cnt_presets, cnt_managed, cnt_failed_presets, time.time() - self._start_time
            )
            self._running = False
        return result

    async def _manage(self):
        await self.presets.reload()

        presets = await self.presets.get_presets_list()
        cnt_presets, cnt_managed, cnt_failed_presets = len(presets), 0, 0

        for name in presets:

            try:
                preset = await self.presets.get(name)
                async with preset as locked:
                    if locked:
                        cnt_managed += 1
                        await preset.manage()
            except Exception:
                logging.exception('Error managing %s', name)
                cnt_failed_presets += 1

        return self.OK, cnt_presets, cnt_managed, cnt_failed_presets
