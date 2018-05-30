=============
Configuration
=============

Vmhepherd requires configuration to be supplied with simple `YAML <http://yaml.org/>`_ file. Avaiable options are describe grouped in couple sections:

    1. general parameters
    2. runtime store configuration
    3. preset store configuration
    4. and optional `defaults` than will be combined with every preset
    

General parameters
------------------

- worker_interval
- log_level


Runtime store
-------------

Allows to set driver for runtime store. Runtime store is used to keep data that should be shared with

:: 
   runtime:
     driver: NameOfTheDriver
     some_arg1: host
     some_arg2: 345


Preset store
------------

AAAA


:: 
   presets:
     driver: NameOfTheDriver
     some_arg1: host
     some_arg2: 345

`defaults`
----------

TODO


Example configuration
---------------------

.. literalinclude:: ../../config/settings-openstack.example.yaml
