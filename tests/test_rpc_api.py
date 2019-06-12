import time
from aiounittest import futurized, AsyncTestCase
from unittest.mock import patch, Mock
from vmshepherd.http.rpc_api import RpcApi
from vmshepherd.iaas.vm import Vm, VmState


class TestRpcApi(AsyncTestCase):

    def tearDown(self):
        patch.stopall()
        super().tearDown()

    def setUp(self):
        super().setUp()
        mock_request = Mock()
        self.mock_preset_manager = Mock()
        self.mock_preset_manager.vms = [
            Vm(self, '1243454353', 'C_DEV-app-dev',
               ['10.177.51.8'], time.time(), state=VmState.RUNNING),
            Vm(self, '4535646466', 'C_DEV-app-dev',
               ['10.177.51.9'], time.time(), state=VmState.RUNNING),
            Vm(self, '5465465643', 'C_DEV-app-dev',
               ['10.177.51.10'], time.time(), state=VmState.RUNNING)
        ]
        self.mock_preset_manager.count = 3
        self.mock_preset_manager.iaas.terminate_vm.return_value = futurized('ok')
        self.mock_preset_manager.iaas.get_vm.return_value = futurized(self.mock_preset_manager.vms[0])
        mock_request.app.vmshepherd.preset_manager.get_preset.return_value = self.mock_preset_manager
        mock_request.app.vmshepherd.preset_manager.list_presets.return_value = futurized({"C_DEV-app-dev": []})
        mock_request.remote = ['10.177.51.8']
        self.rpcapi = RpcApi()
        self.rpcapi._request = mock_request
        self.mock_list_vms = {
            "1243454353": {
                "ip": "10.177.51.8",
                "state": "running"
            },
            "4535646466": {
                "ip": "10.177.51.9",
                "state": "running"
            },
            "5465465643": {
                "ip": "10.177.51.10",
                "state": "running"
            }
        }

    async def test_list_vms(self):
        self.mock_preset_manager.refresh_vms.return_value = futurized(None)
        ret = await self.rpcapi.list_vms('C_DEV-app-dev')
        self.mock_preset_manager.refresh_vms.assert_called_once_with()

        # next call should also refresh vms
        ret = await self.rpcapi.list_vms('C_DEV-app-dev')
        self.assertEqual(self.mock_preset_manager.refresh_vms.call_count, 2)

        self.assertEqual(ret[1], self.mock_list_vms)
        self.assertEqual(ret[0], 3)

    async def test_terminate_vm_success(self):
        ret = await self.rpcapi.terminate_vm('C_DEV-app-dev', 12345)
        self.assertEqual(ret, 'OK')
        self.mock_preset_manager.iaas.terminate_vm.assert_called_with(12345)

    async def test_get_vm_metadata_success(self):
        ret = await self.rpcapi.get_vm_metadata('C_DEV-app-dev', 12345)
        self.assertEqual(ret, {'tags': None, 'iaas_shutdown': None})
        self.mock_preset_manager.iaas.get_vm.assert_called_with(12345)

    async def test_list_presets_success(self):
        ret = await self.rpcapi.list_presets()
        self.assertEqual(ret, ["C_DEV-app-dev"])

    async def test_get_vm_ip(self):
        ret = await self.rpcapi.get_vm_ip('C_DEV-app-dev', '1243454353')
        self.assertEqual({'vm_ip': '10.177.51.8'}, ret)
