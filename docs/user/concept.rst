=======
Concept
=======

Vmshepherd is an application to keep running groups of virtual machines.
*Keep running* means that live VMs in IaaS should be no less than defined in configuration and if healthcheck is configured, all VMs need to pass it.


States
------

Virtual Machine can be in defined state.

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

For listing presets is responsible Preset Driver described `in this section <drivers/index.html#preset-driver>`_.
Each preset is an object of Preset class.
Each preset from list need to be locked (via the Runtime Dviver described `here <drivers/index.html#runtime-driver>`_)
and after lock it can be managed.


Detailed actions in one iteration (*preset manage*)
--------------------------------------------------

.. graphviz::
    :caption: Preset management flow

    digraph G {
        compound=true;
        center=true;
        "list vms" -> "terminate dead vms" -> "create missing" -> healthcheck -> end;
    }

In one cycle vmshepherd tries to maintain cluster of VMs in count defined in configuration up and running.

