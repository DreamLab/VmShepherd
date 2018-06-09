=======
Concept
=======

VmShepherd is an application to keep running groups of virtual machines.
*Keep running* means that there should be no less active VMs in IaaS than defined in configuration, and if healthcheck is configured, all VMs need to pass it.


States
------

Virtual Machine can be in a defined state.

.. autoclass:: vmshepherd.iaas.vm.VmState

Main mangement flow
-------------------

.. graphviz::
    :caption: Global preset flow

    digraph G {
        compound=true;
        center=true;
        "list presets" -> next;
        next -> lock [label=aquire];
        lock -> manage [label=locked];
        manage -> unlock;
        unlock -> next;
        lock -> next [label="lock failed"];
        next -> end;
    }

`Preset Driver <drivers/index.html#preset-driver>`_ is responsible for listing presets.
Each preset is an object of a ``Preset`` class.
Each preset from a list needs to be locked (via the `Runtime Driver <drivers/index.html#runtime-driver>`_)
and it can be managed after locking.


Detailed actions in one iteration (*preset manage*)
---------------------------------------------------

.. graphviz::
    :caption: Preset management flow

    digraph G {
        compound=true;
        center=true;
        "list vms" -> "terminate dead vms" -> "create missing" -> healthcheck -> end;
    }

In one cycle VmShepherd tries to maintain up and running cluster of VMs defined in the configuration.

