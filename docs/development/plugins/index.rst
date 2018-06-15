===================
Plugins development
===================

To make it easier to create and use other drivers without code changes within VmShepherd itself, python's `entry point mechanism <https://packaging.python.org/specifications/entry-points/>`_ are used as plugins.

Search rules for entry points are ``vmshepherd.driver.{name}``. IaaS Driver with a name ``DummyIaasDriver`` will be searched in the ``vmshepherd.driver.iaas`` entrypoint.

.. toctree::
   :maxdepth: 2

   presets
   iaas
   runtime
   healthcheck
