
Changelog
=========

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
