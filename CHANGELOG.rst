
Changelog
=========



1.6.3 (2021-05-15)
------------------

* bugfix: aiohttp lib version


1.6.2 (2021-05-13)
------------------

* feature: log info how long virtual machine fails healthcheck


1.6.1 (2020-08-13)
------------------

* feature: new vm object state - unhealthy


1.6.0 (2019-12-18)
------------------

* feature: new rpc methods - list_presets_with_tags, get_preset_tags


1.5.2 (2019-09-03)
------------------

* bugfix: terminate via iaas on healthcheck


1.5.1 (2019-08-26)
------------------

* bugfix: vm class - remove terminate method


1.5.0 (2019-08-23)
------------------

* feature: the vms list is keeping in runtime driver (latest possible)
           ans is refreshed by the git worker on every cycle


1.4.2 (2019-08-14)
------------------

* bugfix: remove next _initialize_master_working_set line


1.4.1 (2019-08-14)
------------------

* bugfix: remove _initialize_master_working_set on each driver get


1.4.0 (2019-08-12)
------------------

* feature: rpc - list_vms - created at field


1.3.5 (2019-07-26)
------------------

* bugfix: fix problem with sys.path in drivers
* bugfix: reload entry_points


1.3.3 (2019-07-26)
------------------

* bugfix:  add asyncio.lock for git clone/pull commands

1.3.2 (2019-07-26)
------------------

* bugfix:  Add unique name for a tmp preset directory in a Git Driver


1.3.1 (2019-06-03)
------------------

* bugfix:  change the return type for get_vm_ip
* feature: custom exception class for errors


1.3.0 (2019-06-03)
------------------

* feature: configure unmanaged state for presets
* feature: rpc api - get_vm_ip(preset_name, vm_id)

1.2.3 (2019-05-10)
------------------

* bugfix: panel - fail to load due jinja error


1.2.1 (2019-05-09)
------------------

* bugfix: update runtime data after manage even if unlocked
* bugfix: panel - deterministic preset order


1.2.0 (2018-08-07)
------------------

* feature: api - added list_presets


1.1.0 (2018-06-13)
------------------

* feature: adjustable timeout for http requests to iaas


1.0.1 (2018-06-08)
------------------

* bugfix: API should use last cycle data
* bugfix: OpenStackDriver refresh token


1.0.0 (2018-06-06)
------------------

* preserve preset state (dashboard shows data from last cycle)
* bump AsyncOpenStackClient (0.6.2)
* docs


0.7.7 (2018-05-10)
------------------

* bump AsyncOpenStackClient (0.5.2)

0.7.6 (2018-05-10)
------------------

* bump AsyncOpenStackClient (0.5.1)

0.7.5 (2018-04-09)
------------------

* runtime driver abstract fix

0.7.4 (2018-03-22)
------------------

* cleanup, verify


0.7.3 (2018-03-22)
------------------

* bump AsyncOpenStackClient (+ compat)


0.7.2 (2018-03-22)
------------------

* user-data base64


0.7.1 (2018-03-21)
------------------

* multiple network interfaces


0.7.0 (2018-03-20)
------------------

* AsyncOpenStackClient


0.6.0 (2018-02-01)
------------------

* web panel
* rpc api


0.0.3 (2018-02-01)
------------------

* initial
