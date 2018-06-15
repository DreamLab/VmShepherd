Glossary
--------

**Driver**
    is a pluginable logical unit, with specified interface, providing certain functionality. I.e. OpenStackDriver (which is implementing IaaS driver) serves set of funtions which interact with OpenStack - which acts as IaaS provider in this case.
**Healthcheck**
    is user defined way to check whether chosen service is healthy or not, custom healthcheck driver can be provided as plug-in.
**Preset**
    is a definition/spec of a cluster of virtual machines
**Preset lock**
    is preset state (assigned by runtime driver) that prevents other VmShepherd instance from managing this preset.
**IaaS**
    is vm's (compute power) provider, examples: AWS EC2 or OpenStack instance.
**Vm flavour**
    is a set of parameters defining vm properties like number of cpu's, amount of memory and so on.
**Image**
    is a collection of files for a specific operating system (OS) that you use to create or rebuild a server. 
