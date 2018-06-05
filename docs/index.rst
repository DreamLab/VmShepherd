==========
VmShepherd
==========

VmShepherd - Virtual Machine Shepherd is a lightweight, scalable, standalone asynchronous service created to manage
clusters for different IaaS platforms.
This tool has a plugin architecture which provide an elastic way to implement
and use a various set of healtchecks, presets and cloud providers.



Key features:
-------------

IaaS Agnostic:
..............

This tool treat any cloud like OpenStack, AWS, GCP etc. as an
IaaS vendor which provide a HTTP api to create/delete or list virtual machines.

Health checks:
...............

VmShepherd provide functionality of sanity checkings for clusters.
This helps to monitor state not only your virtual machines but also
applications inside them with using simple healt check system.

Scalability:
.............

This tool implemented also a functionality of adjustable scalling for virtual machines clusters,
which provide fully automated and elastic way of monitoring and managing cluster capacity.
On the other hand application itself is easy to scale so you can administrate any size of infrastructure.

Infrastructure as a code:
..........................

Application is a client of infrastructure not a part of it.
With this approach all configuration is kept in dead simple yaml files.

Web Panel
..........................
This service is comming with lightweight and human friendly interface to administrate your infrastructure.




.. toctree::
   :maxdepth: 2

   getting_started
   extending
   reference/index
   changelog
   user/index
   releases/index
   development/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

