=====
Flow
=====

Vmshepherd preset management flow

.. graphviz::
    :caption: Preset management flow

    digraph G {
        compound=true;
        center=true;
        "list presets" -> next;
        next -> lock [label=aquire];
        lock -> next [label="lock failed"];
        subgraph cluster0 {
            lock -> "list vms" -> "terminate dead vms" -> "create missing" -> healthcheck;
            label = "preset driver";
        }
        healthcheck -> next;
        next -> end;
    }


