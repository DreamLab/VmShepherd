=======
Drivers
=======

Vmshepherd is designed to cover most of functionalities by drivers.
It is easy to change some logic by writing your own driver and use it.

Entry points
------------

To make easier to create and use other drivers without code changes within VmShepherd itself, python entry point mechanizm are being used (https://packaging.python.org/specifications/entry-points/)

Entry points for drivers:

1. vmshepherd.driver.iaas - IaaS Driver
2. vmshepherd.driver.presets - Preset Driver
3. vmshepherd.driver.runtime - Runtime Driver
4. vmshepherd.driver.healthcheck - Healthcheck Driver

Config example for IaaS Driver:

.. code-block:: yaml
   :emphasize-lines: 3,5

    iaas:
      driver: DummyIaasDriver
      driver_arg_1: val1
      driver_arg_2: val2

Search rules for entry points are vmshepherd.driver.{name}. IaaS Driver with name DummyIaasDriver will be searched in vmshepherd.driver.iaas entrypoint.

Iaas Driver
-----------
IaaS Driver gives abstraction layer which unifies API methods making easier to use many IaaS providers.

Implemented IaaS Drivers:

    1. DummyIaasDriver - iaas simulation driver
    2. OpenStackDriver - asyncopenstackclient library wrapper


.. toctree::
   :maxdepth: 2

   iaas_dummydriver
   iaas_openstackdriver


Runtime Driver
--------------
Runtime Driver implements methods to lock preset before manage it. It can be useful when many VmShepherd instances working on one list of presets.
It also can hold runtime data - information that should be avaliable in later manage iterations. That data can be for example number of failed check for VM with ID X.

Implemented Runtime Drivers:

    1. InMemoryDriver - To use for only one VmShepherd instance. It holds all data in local memory.
    2. (chcialo by sie tu opisac jeszcze PostgresDriver ale nie jest upubliczniony)


.. toctree::
   :maxdepth: 2

   runtime_postgresdriver


Preset Driver
-------------
Preset Driver is used to get information about preset confiturations from its own store.

Implemented Preset Drivers:

    1. DirectoryDriver - read preset configurations from local files
    2. GitRepoDriver - get preset configuration from git repositories


.. toctree::
   :maxdepth: 2

   preset_directorydriver
   preset_gitrepodriver


Preset global configuration:

.. code-block:: yaml
   :emphasize-lines: 3,5

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

1. **name** - preset name used to define VMs group. Example: PROD_apps_cluster_1.
2. **count** - count of virtual machines in group.
3. **manage_interval** - Delay to next manage proceed.
4. **manage_expire** - After this delay even lock acquire failed manage procedure is called.
5. **image** - Image name avaliable in iaas.
6. **flavour** - Virtual machine flavor/size.
7. **userdata** - User data (cloud-init config) can be defined like string or file. Content of user data can be a jinja template. To generate final config it use all preset configuration. Example below.
8. **userdata_source_root** - If *userdata* parameter is defined like 'file://' userdata_source_root is start path to find it.
9. **meta_tags** - Virtual Machine metadata.
10. **key_name** - Ssh public key name.
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
Healthcheck Driver give methods to check if our application/something running on VM is working properly.

Implemented Healthcheck Drivers:

    1. DummyHealthcheck - healthcheck simulation driver returning always positive check result
    2. HttpHealthcheck - uses HTTP request


.. toctree::
   :maxdepth: 2

   healthcheck_http

