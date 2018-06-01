VmShepherd
==========


Introduction
------------

TO DO

Installation
------------

You can install easily from pypi.org

::
   pip install VmShepherd

or use a docker image

TODO

Usage
-----

TODO

::
   vmshepherd -c CONFIGFILE -l LOGLEVEL

Development
-----------

::
   make test

:: Docker

You can run VmShepherd locally in a development environment using docker.

Firstly build a image:

``docker build -t vmshepherd . --rm``

Our Dockerfile create a ``ENTRYPOINT`` for our makefile, so basically you can execute make commands in docker container like run or show-docs.

Examples of usage:

* Running vmshepherd application:

``docker run -it  -p 8888:8888 -p 8000:8000 vmshepherd run``

* Documentation:

``docker run -it  -p 8888:8888 -p 8000:8000 vmshepherd show-docs``



License
-------

`Apache License 2.0 <LICENSE>`_
