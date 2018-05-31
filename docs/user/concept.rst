=======
Concept
=======

Vmshepherd is an application to keep running group of virtual machines.


.. automodule:: vmshepherd.iaas.vm

.. autoclass:: vmshepherd.iaas.vm.VmState

** Preset management flow **

.. graphviz::
    :caption: Global preset flow

    digraph G {
        compound=true;
        center=true;
        "list presets" -> next;
        next -> lock [label=aquire];
        lock -> manage;
        manage -> unlock;
        unlock -> next;
        lock -> next [label="lock failed"];
        next -> end;
    }

.. automodule:: vmshepherd.worker

.. graphviz::
    :caption: Preset management flow

    digraph G {
        compound=true;
        center=true;
        "list vms" -> "terminate dead vms" -> "create missing" -> healthcheck -> end;
    }

.. automodule:: vmshepherd.presets.preset

