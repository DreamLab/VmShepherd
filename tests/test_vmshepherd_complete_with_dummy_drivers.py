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
        await self.vmshepherd.preset_manager.reload()
        presets_list = await self.vmshepherd.preset_manager.get_presets_list()
        self.assertEqual(presets_list, ['test-preset'])

        preset = await self.vmshepherd.preset_manager.get('test-preset')
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
        # first run - should create on vm
        await self.vmshepherd.run(run_once=True)

        preset = await self.vmshepherd.preset_manager.get('test-preset')
        vm_list = await preset.list_vms()
        self.assertEqual(
            vm_list,
            [VmMock(0, ['127.0.0.1'], 'test-preset', 'fedora-27', 'm1.small')]
        )
        self.assertTrue(vm_list[0].is_running())

        # second run - there should be no change
        await self.vmshepherd.run(run_once=True)

        vm_list = await preset.list_vms()
        self.assertEqual(
            vm_list,
            [VmMock(0, ['127.0.0.1'], 'test-preset', 'fedora-27', 'm1.small')]
        )
        self.assertTrue(vm_list[0].is_running())

        # third run - virtual machine goes in ERROR
        #  - failed vm should be terminated
        #  - new vm should be created

        vm_list[0].state = VmState.ERROR
        await self.vmshepherd.run(run_once=True)

        vm_list = await preset.list_vms()
        self.assertEqual(
            vm_list,
            [VmMock(1, ['127.0.0.1'], 'test-preset', 'fedora-27', 'm1.small')]
        )
        self.assertTrue(vm_list[0].is_running())

        # third run - virtual machine goes in TERMINATED
        #  - terminated vm should be skipped
        #  - new vm should be created

        vm_list[0].state = VmState.TERMINATED
        await self.vmshepherd.run(run_once=True)

        vm_list = await preset.list_vms()
        self.assertEqual(
            vm_list,
            [VmMock(2, ['127.0.0.1'], 'test-preset', 'fedora-27', 'm1.small')]
        )
        self.assertTrue(vm_list[0].is_running())


class TestVmShepherdLockingWithDummyDrivers(AsyncTestCase):

    def setUp(self):
        super().setUp()
        Drivers.flush()
        self.vmshepherd = VmShepherd(example_config)

    async def test_locking(self):
        await self.vmshepherd.preset_manager.reload()
        preset = await self.vmshepherd.preset_manager.get('test-preset')
        await asyncio.gather(
            self.vmshepherd.run(run_once=True),
            self.vmshepherd.run(run_once=True)
        )

        preset = await self.vmshepherd.preset_manager.get('test-preset')
        vm_list = await preset.list_vms()
        self.assertEqual(
            vm_list,
            [VmMock(0, ['127.0.0.1'], 'test-preset', 'fedora-27', 'm1.small')]
        )
        self.assertTrue(vm_list[0].is_running())

    @expectedFailure
    async def test_example_of_bad_locking(self):
        await self.vmshepherd.preset_manager.reload()

        # no lock-mechanism actually, always manage preset
        self.vmshepherd.runtime_manager.acquire_lock = Mock(return_value=futurized(True))
        self.vmshepherd.runtime_manager.release_lock = Mock(return_value=futurized(True))

        await asyncio.gather(
            self.vmshepherd.run(run_once=True),
            self.vmshepherd.worker._manage()  # explicit call of private method to bypass run_once check
        )

        preset = await self.vmshepherd.preset_manager.get('test-preset')
        vm_list = await preset.list_vms()
        self.assertEqual(
            vm_list,
            [VmMock(0, ['127.0.0.1'], 'test-preset', 'fedora-27', 'm1.small')]
        )
        self.assertTrue(vm_list[0].is_running())
