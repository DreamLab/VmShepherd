from aiounittest import futurized, AsyncTestCase
from unittest.mock import patch, Mock
from vmshepherd.http.rpc_api import RpcApi
from vmshepherd.iaas.vm import Vm, VmState
import time

mock_list_vms = {
    "1243454353": {
        "iaas_vm_ip": "10.177.51.8",
        "state": "running"
    },
    "4535646466": {
        "iaas_vm_ip": "10.177.51.9",
        "state": "running"
    },
    "5465465643": {
        "iaas_vm_ip": "10.177.51.10",
        "state": "running"
    }
}


class TestRpcApi(AsyncTestCase):

    def tearDown(self):
        patch.stopall()
        super().tearDown()

    def setUp(self):
        super().setUp()
        mock_request = Mock()
        mock_preset_manager = Mock()
        mock_preset_data = [
                    Vm(self, '1243454353', 'C_DEV-app-dev', ['10.177.51.8'], time.time(), state=VmState.RUNNING),
                    Vm(self, '4535646466', 'C_DEV-app-dev', ['10.177.51.9'], time.time(), state=VmState.RUNNING),
                    Vm(self, '5465465643', 'C_DEV-app-dev', ['10.177.51.10'], time.time(), state=VmState.RUNNING)
                ]
        mock_preset_manager.list_vms.return_value = futurized(mock_preset_data)
        mock_preset_manager.count = 3
        self.mock_preset_manager = mock_preset_manager
        mock_preset_manager.iaas.terminate_vm.return_value = futurized('ok')
        mock_request.app.vmshepherd.preset_manager.get.return_value = futurized(mock_preset_manager)
        mock_request.app.vmshepherd.preset_manager.reload.return_value = futurized({})
        self.rpcapi = RpcApi(mock_request)

    async def test_rcp_list_vms(self):
        ret = await self.rpcapi.rpc_list_vms('C_DEV-app-dev')
        self.assertEqual(ret[1],  mock_list_vms)
        self.assertEqual(ret[0], 3)

    async def test_rpc_terminate_vm_success(self):
        ret = await self.rpcapi.rpc_terminate_vm('C_DEV-app-dev', 12345)
        self.assertEqual(ret, 'OK')
        self.mock_preset_manager.iaas.terminate_vm.assert_called_with(12345)
