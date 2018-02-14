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
        state, cnt_presets, cnt_failed_presets = self.ERROR, 0, 0
        try:
            # TODO: it's making runtime injection a bit harder.
            #       Separate listing from actual fetch.
            # IDEA: use __aiter__ __anext__
            presets = await self.presets.get_presets_configuration()
            cnt_presets = len(presets)

            for name, preset in presets.items():
                if (await self.runtime.lock_preset(name)):
                    try:
                        runtime_data = await self.runtime.get_preset_data(name)
                        runtime_data = await preset.manage(runtime_data)
                        await self.runtime.set_preset_data(name, runtime_data)
                    except Exception:
                        cnt_failed_presets += 1
                    finally:
                        await self.runtime.unlock_preset(name)
            state = self.OK
        except Exception:
            logging.exception('Error while running')
        finally:
            logging.info(
                'VmShepherd end cycle result=%s presets=%s failed_presets=%s f time=%.2f',
                state, cnt_presets, cnt_failed_presets, time.time() - self._start_time
            )
            self._running = False
