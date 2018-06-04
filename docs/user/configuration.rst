=============
Configuration
=============

VmShepherd requires configuration to be supplied with simple `YAML <http://yaml.org/>`_ file. Available sections:

    1. general parameters
    2. runtime store configuration (pluginable)
    3. preset store configuration (pluginable)
    4. and optional `defaults` than will be combined with every preset (pluginable)


Most of the parts of configuration it's just matter of chosen driver and its options. The options you should refer with driver documentation.
    

General parameters
------------------

- *worker_interval* - interval between manage cycles
- *log_level* - DEBUG, INFO, ERROR - default to INFO


Runtime store
-------------

Choose a runtime store driver and its options. 

.. code-block:: yaml

   runtime:
     driver: NameOfTheDriver
     some_arg1: host
     some_arg2: 345

Runtime store is used to keep data that should be shared between cycles - you can find more information in `Runtime Driver section <drivers/index.html#runtime-driver>`_. 


Preset store
------------

Specify preset store driver. 


.. code-block:: yaml

   presets:
     driver: NameOfTheDriver
     some_arg1: host
     some_arg2: 345

Preset is a definition/spec of a cluster - more info at ....

http
----

You can set api/panel port, whitelist available API methods. More about API...

.. code-block:: yaml

    http:
      api: 
        allowed_methods: 
          - list_vms
          - terminate_vm
          - get_vm_metadata
      listen_port: 8888

The `api.allowed_methods` params are optional and if are not provided entire API will be exposed.

.. code-block:: yaml

    http:
      listen_port: 8888

`defaults`
----------

Allows to provide defaults for `iaas` and `healthcheck` configuration that will be merged with preset spec.

.. code-block:: yaml

    defaults:
      iaas:
        driver: OpenStackDriver
        username: USER
        password: PASS
        project: my-project
      healthcheck:
        driver: HttpCheck
        option1: 123123


Example configuration
---------------------

.. literalinclude:: ../../config/settings-openstack.example.yaml
