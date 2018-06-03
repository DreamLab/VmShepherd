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

