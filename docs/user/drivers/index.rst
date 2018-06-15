=======
Drivers
=======

VmShepherd is designed to cover most of its functionalities by separable drivers.
It is easy to change some logic by writing your own driver and using it.

Plugins
------------

To make it easier to create and use other drivers without code changes within VmShepherd itself, plugin architecture has been used.

Drivers can be plugged in the following destinations:

1. vmshepherd.driver.iaas - `IaaS Driver`_
2. vmshepherd.driver.presets - `Preset Driver`_
3. vmshepherd.driver.runtime - `Runtime Driver`_
4. vmshepherd.driver.healthcheck - `Healthcheck Driver`_


Iaas Driver
-----------

IaaS Driver provides abstraction layer which unifies API methods, making it easier to use many IaaS providers.

Implemented IaaS Drivers:

    1. `DummyIaasDriver <iaas_dummydriver>`_ - iaas simulation driver
    2. `OpenStackDriver <iaas_openstackdriver>`_ - asyncopenstackclient library wrapper

Config example for an IaaS Driver:

.. code-block:: yaml

    iaas:
      driver: DummyIaasDriver
      driver_arg_1: val1
      driver_arg_2: val2

.. toctree::
   :hidden:
   :maxdepth: 2

   iaas_dummydriver
   iaas_openstackdriver


Runtime Driver
--------------

Runtime Driver implements methods to lock preset before managing it. It can be very useful when many VmShepherd instances work on the same list of presets.
It can also hold runtime data - information that should be available in later iterations. That data can be for example: a number of failed checks for VM with ID X.

Implemented Runtime Drivers:

    1. `InMemoryDriver <runtime_inmemory>`_ - To use for only one VmShepherd instance. It holds all data in local memory
    2. `PostgresDriver <https://github.com/DreamLab/vmshepherd-runtime-postgres-driver>`_ - Runtime driver that utilizes PostgreSQL database engine, supplied by a separate package
    3. `ZookeeperDriver <https://github.com/kwarunek/vmshepherd-zookeeper-driver>`_ - Plugin runtime driver that takes advantage of Zookeeper configuration maintainer

.. toctree::
   :hidden:
   :titlesonly:

   runtime_inmemory
   Postgres Driver <https://github.com/DreamLab/vmshepherd-runtime-postgres-driver>
   Zookeeper Driver <https://github.com/kwarunek/vmshepherd-zookeeper-driver>

   
Preset Driver
-------------

Preset Driver is used to get information about preset configurations from its own store.

Implemented Preset Drivers:

    1. `DirectoryDriver <preset_directorydriver>`_ - read preset configurations from local files
    2. `GitRepoDriver <preset_gitrepodriver>`_ - get preset configuration from git repositories


.. toctree::
   :hidden:
   :maxdepth: 2

   preset_directorydriver
   preset_gitrepodriver


Preset global configuration:

.. code-block:: yaml

   name: NAME # preset name
   count: COUNT_OF_VMS # count of vms to keep running in this preset
   manage_interval: SECONDS_TO_NEXT_MANAGE # run manage after manage_interval delay
   manage_expire: SECONDS_TO_MANAGE_EXPIRE # run manage procedure even if lock acquire failed
   image: ubuntu16 # system image name
   flavour: small # vm flavour
   userdata_source_root: ''
   userdata: 'file://user_data' # cloud-init user data to use
   meta_tags:
     role: httpserver
     environment: prod
   key_name: user@domain # ssh key name
   network:
     security_groups:
       - security_gorup_id1  # priv
       - security_gorup_id2  # global
       - security_gorup_id3  # adm
     availability_zone: az1
     subnets:
       - net-id: network_id

Parameters:

1. **name** - preset's name used to define VMs group. Example: ``PROD_apps_cluster_1``.
2. **count** - count of virtual machines in group.
3. **manage_interval** - Delay to next manage iteration.
4. **manage_expire** - After this delay ``lock acquire failed`` manage procedure is called.
5. **image** - Image name available in iaas.
6. **flavour** - Virtual machine flavor/size.
7. **userdata** - User data (cloud-init config) can be defined like a string or a file. Content of user data can be a jinja template. To generate final config it uses all preset configuration. Example below.
8. **userdata_source_root** - If *userdata* parameter is defined like 'file://' userdata_source_root is start path to find it.
9. **meta_tags** - Virtual Machine metadata.
10. **key_name** - SSH public key name.
11. **network** - Configuration block used to define virtual machine networking.

User data example:

.. code-block:: jinja

   #cloud-config
   write_files:
   - path: /etc/salt/grains
     owner: root:root
     permissions: '0744'
     content: |
       {% for key, value in meta_tags.items() %}
       {{ key }}: {{ value }}
       {% endfor %}

Healthcheck Driver
------------------

Healthcheck Driver provides methods to check if your application (or other process) is running on a VM, and works properly.

Implemented Healthcheck Drivers:

    1. ``DummyHealthcheck`` - a healthcheck simulation driver returning always positive check result
    2. `HttpHealthcheck <healthcheck_http>`_ - uses HTTP request

.. toctree::
   :maxdepth: 2
   :hidden:

   healthcheck_http

