import aiohttp
import logging
from .abstract import AbstractHealthcheck


class HttpHealthcheck(AbstractHealthcheck):

    def __init__(self, config=None):
        config = config or {}
        self.method = config.get('method', 'GET')
        self.path = config.get('path', '/')
        self.port = config.get('port', 80)
        self.check_status = config.get('check_status', 200)
        self._client_timeout = aiohttp.ClientTimeout(
            connect=float(config.get('conn_timeout', 1)),
            total=float(config.get('read_timeout', 1))
        )

    def __str__(self):
        return f'HTTP on {self.port} with {self.method} {self.path} expecting {self.check_status}'

    async def is_healthy(self, vm):
        if not vm.ip:
            logging.info('[healthcheck] ip is empty:%s', vm)
            return False

        check_status = False
        try:
            async with aiohttp.ClientSession(timeout=self._client_timeout) as session:
                ip = vm.ip[0] if type(vm.ip) == list else vm.ip
                url = "http://{}:{}{}".format(ip, self.port, self.path)
                resp = await session.request(method=self.method, url=url)
                check_status = resp.status == self.check_status
        except aiohttp.client_exceptions.ClientError:
            pass
        logging.debug('[healthcheck] VM: %s - check status: %s', vm, check_status)
        return check_status
