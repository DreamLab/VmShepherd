=======
Drivers
=======

Vmshepherd is designed to cover most of functionalities by drivers.
It is easy to change some logic by writing your own driver and use it.


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


Healthcheck Driver
------------------
Healthcheck Driver give methods to check if our application/something running on VM is working properly.

Implemented Healthcheck Drivers:

    1. DummyHealthcheck - healthcheck simulation driver returning always positive check result
    2. HttpHealthcheck - uses HTTP request


.. toctree::
   :maxdepth: 2

   healthcheck_http

