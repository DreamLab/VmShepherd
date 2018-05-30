===============
Api
===============


Description
-----------------

VMShepherd provide a RPC api which is available at `api' handler and can be configured.
In configuration you provide a information which method is available to a user.
This api provide a simple interface to control a Virtual Machines lifecycle in our environment.
Also we provide a easy way to gather information about presets and virtual machines in environment.

Configuration
-----------------

For api you can configure which methods are available:

Example:
.........................

.. code-block:: yaml
   :emphasize-lines: 3,5

    http:
    # example of allowed_methods list
      api:
        allowed_methods:
          - list_vms
          - terminate_vm
          - get_vm_metadata

Code
-----------------

vmshepherd.http.rpc\_api module
................................

.. automodule:: vmshepherd.http.rpc_api
    :members:
    :undoc-members:
    :show-inheritance:


Sample calls to api:
-----------------

Sample code is also available in `repository <.https://github.com/DreamLab/VmShepherd/blob/master/examples>`_


List Virtual Machines in a preset
................................

.. code-block:: python
   :emphasize-lines: 3,5

    >>> import asyncio
    >>> from aiohttp_jsonrpc.client import ServerProxy, batch
    >>> loop = asyncio.get_event_loop()
    >>> client = ServerProxy("http://127.0.0.1/api", loop=loop)
    >>> async def main():
    >>>     print(await client.list_vms(preset='samplePreset'))
    >>> client.close()
    >>> loop.run_until_complete(main())
    [2, {'1111111-1111-1111-1111-11111111': {'ip': '10.177.1.2', 'state': 'running'}, '22222-2222-2222-2222-2222222': {'ip': '10.177.1.3, 'state': 'running'}}]

Get Virtual Machine metadata
.............................

.. code-block:: python
   :emphasize-lines: 3,5

    >>> import asyncio
    >>> from aiohttp_jsonrpc.client import ServerProxy, batch
    >>> loop = asyncio.get_event_loop()
    >>> client = ServerProxy("http://127.0.0.1/api", loop=loop)
    >>> async def main():
    >>>     print(await client.get_vm_metadata(preset='samplePreset', id='1111111111111111111))
    >>> client.close()
    >>> loop.run_until_complete(main())
    {'timed_shutdown': '111111111111'}

Terminate Virtual Machine
............................

.. code-block:: python
   :emphasize-lines: 3,5

    >>> import asyncio
    >>> from aiohttp_jsonrpc.client import ServerProxy, batch
    >>> loop = asyncio.get_event_loop()
    >>> client = ServerProxy("http://127.0.0.1/api", loop=loop)
    >>> async def main():
    >>>     print(await client.terminate_vm(preset='samplePreset', id='1111111111111111111))
    >>> client.close()
    >>> loop.run_until_complete(main())
    'OK'
