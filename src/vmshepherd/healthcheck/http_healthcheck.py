import aiohttp
import logging
from .abstract import AbstractHealthcheck


class HttpHealthcheck(AbstractHealthcheck):

    def __init__(self, method='GET', path='/', port=80, check_status=200, conn_timeout=1,
                 read_timeout=1):
        self.method = method
        self.path = path
        self.port = port
        self.check_status = check_status
        self.conn_timeout = conn_timeout
        self.read_timeout = read_timeout

    def __str__(self):
        return f'HTTP on {self.port} with {self.method} {self.path} expecting {self.check_status}'

    async def is_healthy(self, vm):
        if not vm.ip:
            logging.info('[healthcheck] ip is empty:%s', vm)
            return False

        check_status = False
        try:
            async with aiohttp.ClientSession(conn_timeout=self.conn_timeout,
                                             read_timeout=self.read_timeout) as session:
                ip = vm.ip[0] if type(vm.ip) == list else vm.ip
                url = "http://{}:{}{}".format(ip, self.port, self.path)
                resp = await session.request(method=self.method, url=url)
                check_status = resp.status == self.check_status
        except aiohttp.client_exceptions.ClientError:
            pass
        logging.debug('[healthcheck] VM: %s - check status: %s', vm, check_status)
        return check_status
