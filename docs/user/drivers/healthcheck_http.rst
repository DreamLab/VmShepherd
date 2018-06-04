===============
HttpHealthcheck
===============

HttpHealthcheck uses HTTP request to check if our application is lives.

Main configuration:

.. code-block:: yaml
   :emphasize-lines: 3,5

   conn_timeout: 1   # (optional, default:1)
   read_timeout: 1   # (optional, default: 1)
   port: 7007        # (optional, default: 80)
   path: /           # (optional, default: /)
   method: GET       # (optional, default: GET)
   check_status: 200 # (optional, default: 200)
   terminate_heatlh_failed_delay: 600

Parameters:

1. **conn_timeout** - Timeout for connection establishing. Default: 1s.
2. **read_timeout** - Request operations timeout(more info in https://docs.aiohttp.org/en/stable/client_reference.html). Default: 1s.
3. **port** - Request port to use. Default: 80.
4. **path** - HTTP request paht. Default: /.
5. **method** - HTTP request method (GET, POST, ...). Default: GET.
6. **check_status** - Check if response status is equal to given staus. Default: 200.
7. **terminate_heatlh_failed_delay** - Seconds to wait befor terminate VM which has failed healthcheck result. This parameter is used in preset dvier. Default: -1 value means that termination is skipped. When terminate_heatlh_failed_delay is greater than 0 VM will be terminated when time pass and check count is greater than 5.

