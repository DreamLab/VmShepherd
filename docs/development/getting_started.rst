===============
Getting started
===============


.. contents:: :local:


General
-------

- the minimal python version is Python 3.6.0, don't break it,
- VmShepherd is a asynchronous app. Keep in mind that every IO operation should be implemented using asyncio,
- list of built-in plugins is fixed, the purpose is to provide usable, minimal product. Additional providers should be implemented in separate modules.


Tools
-----


Makefile
........

Makefile and docker spec provides tooling to simplify development process.

Run application:

::

   make run

Run tests:

::

   make test

Create documentation:

::

   make show-docs


Docker
......

Firstly build an image:

::

 docker build -t vmshepherd . --rm

Our ``Dockerfile`` creates an ``ENTRYPOINT`` for our ``Makefile``, so basically you can execute ``make`` commands in docker container like ``run`` or ``show-docs``:

* Running a VmShepherd application:

::

  docker run -it  -p 8888:8888 -p 8000:8000 vmshepherd run

* Documentation:

::

  docker run -it  -p 8888:8888 -p 8000:8000 vmshepherd show-docs
