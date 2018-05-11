import aiohttp
from aiounittest import AsyncTestCase, futurized
from collections import namedtuple
from unittest.mock import Mock, patch
from vmshepherd.healthcheck import HttpHealthcheck

VmMock = namedtuple('VmMock', 'id ip name image flavor')
HttpResp = namedtuple('HttpResp', 'status')


class TestHttpHealthcheck(AsyncTestCase):

    def setUp(self):
        super().setUp()
        self.healthcheck = HttpHealthcheck()

    async def test_fail_without_ip(self):
        vm_without_ip = VmMock(0, [], 'test-preset', 'fedora-27', 'm1.small')
        self.assertFalse(await self.healthcheck.is_healthy(vm_without_ip))

    async def test_check_ok(self):
        vm = VmMock(0, ['127.0.0.1'], 'test-preset', 'fedora-27', 'm1.small')
        resp_200 = HttpResp(200)

        with patch('aiohttp.ClientSession.request', Mock()) as mock_request:
            mock_request.return_value = futurized(resp_200)
            self.assertTrue(await self.healthcheck.is_healthy(vm))
            mock_request.assert_called_once_with(method='GET', url='http://127.0.0.1:80/')

    async def test_check_fail(self):
        vm = VmMock(0, ['127.0.0.1'], 'test-preset', 'fedora-27', 'm1.small')

        with patch('aiohttp.ClientSession.request', Mock()) as mock_request:
            mock_request.return_value = futurized(aiohttp.client_exceptions.ClientError())
            self.assertFalse(await self.healthcheck.is_healthy(vm))
            mock_request.assert_called_once_with(method='GET', url='http://127.0.0.1:80/')
