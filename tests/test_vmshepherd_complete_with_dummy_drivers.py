import asyncio
from .common import example_config
from aiounittest import AsyncTestCase, futurized
from collections import namedtuple
from unittest import expectedFailure
from unittest.mock import Mock
from vmshepherd import VmShepherd
from vmshepherd.drivers import Drivers
from vmshepherd.iaas import VmState

VmMock = namedtuple('VmMock', 'id ip name image flavor')


class TestVmShepherdInitWithDummyDrivers(AsyncTestCase):

    def setUp(self):
        super().setUp()
        Drivers.flush()
        self.vmshepherd = VmShepherd(example_config)

    async def test_initialize_preset_manager(self):
        presets_list = await self.vmshepherd.preset_manager.list_presets()
        self.assertEqual(list(presets_list.keys()), ['test-preset'])

        preset = self.vmshepherd.preset_manager.get_preset('test-preset')
        self.assertEqual(preset.count, 1)

    async def test_initialize_iaas(self):
        await self.vmshepherd.runtime_manager.acquire_lock('test-preset')
        await self.vmshepherd.runtime_manager.release_lock('test-preset')


class TestVmShepherdRunWithDummyDrivers(AsyncTestCase):

    def setUp(self):
        super().setUp()
        Drivers.flush()
        self.vmshepherd = VmShepherd(example_config)

    async def test_run(self):
        # zero run - should create on vm
        await self.vmshepherd.run(run_once=True)

        # first run
        await self.vmshepherd.run(run_once=True)

        preset = self.vmshepherd.preset_manager.get_preset('test-preset')
        self.assertEqual(
            preset.vms,
            [VmMock(0, ['127.0.0.1'], 'test-preset', 'fedora-27', 'm1.small')]
        )
        self.assertTrue(preset.vms[0].is_running())

        # # second run - there should be no change
        await self.vmshepherd.run(run_once=True)

        preset = self.vmshepherd.preset_manager.get_preset('test-preset')
        self.assertEqual(
            preset.vms,
            [VmMock(0, ['127.0.0.1'], 'test-preset', 'fedora-27', 'm1.small')]
        )
        self.assertTrue(preset.vms[0].is_running())

        # third run - virtual machine goes in ERROR
        #  - failed vm should be terminated
        #  - new vm should schdule new vm

        preset.vms[0].state = VmState.ERROR
        await self.vmshepherd.run(run_once=True)

        self.assertEqual(
            preset.vms,
            [VmMock(0, ['127.0.0.1'], 'test-preset', 'fedora-27', 'm1.small')]
        )


class TestVmShepherdLockingWithDummyDrivers(AsyncTestCase):

    def setUp(self):
        super().setUp()
        Drivers.flush()
        self.vmshepherd = VmShepherd(example_config)

    async def test_locking(self):
        await self.vmshepherd.preset_manager.list_presets()
        preset = self.vmshepherd.preset_manager.get_preset('test-preset')
        await asyncio.gather(
            self.vmshepherd.run(run_once=True),
            self.vmshepherd.run(run_once=True)
        )

        preset = self.vmshepherd.preset_manager.get_preset('test-preset')
        self.assertEqual(
            preset.vms, []
        )

    @expectedFailure
    async def test_example_of_bad_locking(self):
        # no lock-mechanism actually, always manage preset
        self.vmshepherd.runtime_manager.acquire_lock = Mock(return_value=futurized(True))
        self.vmshepherd.runtime_manager.release_lock = Mock(return_value=futurized(True))

        await asyncio.gather(
            self.vmshepherd.run(run_once=True),
            self.vmshepherd.worker._manage()  # explicit call of private method to bypass run_once check
        )

        preset = self.vmshepherd.preset_manager.get_preset('test-preset')
        self.assertEqual(
            preset.vms,
            [VmMock(0, ['127.0.0.1'], 'test-preset', 'fedora-27', 'm1.small')]
        )
