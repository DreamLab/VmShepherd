import asyncio
from aiohttp_jsonrpc.client import ServerProxy, batch

# initialize a loop
loop = asyncio.get_event_loop()
client = ServerProxy("http://127.0.0.1:8888/api", loop=loop)

# lets list a virtual machines
async def main():
    print(await client.list_vms(preset='C_DEV-app-dev'))

# close a client
client.close()
loop.run_until_complete(main())
