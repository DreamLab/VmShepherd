=========================
Development documentation
=========================


Makefile
--------

We provide a Makefile and docker which can be used during development.

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


.. toctree::
   :maxdepth: 2

   reference/index
