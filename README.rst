VmShepherd
==========


Introduction
------------

Vmshepherd is an application to maintain groups (clusters) of virtual machines. Keeps defined params (like count, image and so) by checking state in an IaaS and tests underlying services with specified health check.


Architecture
------------

VmShepherd is designed to be easy to extend via plugins. Empowered by python3 and its asyncio to facilitate scaling. Diagram show the base components.

.. image:: https://user-images.githubusercontent.com/670887/41005281-1f5dfb08-691d-11e8-8221-f48f7acfc3a7.png

- **preset manager** is responsible for fetch cluster spec/definition (preset). Built-in are DirectoryDriver and GitRepoDriver
- **runtime manger** exposes functionality of locking preset and holds intermediate states. Currently available are InMemoryDriver, PostgresDriver, ZookeeperDriver.
- **iaas** is a glue (api wrapper) to IaaS provider, OpenStackDriver is the first implemented.
- **healthcheck** allows to check service not only existence of virtual machine. HttpHealthcheckDriver is built-in.


For more infromation please take look at the documentiation - `http://doc.dreamlab.pl/VmShepherd/user/index.html <http://doc.dreamlab.pl/VmShepherd/user/index.html>`_.


Installation
--------------
The latest stable version is `available on Pypi <https://pypi.org/project/vmshepherd/>`_.

::

  pip install vmshepherd

also you can install VmShepherd manually using a make:

::

  make install

Also we provide a dockerfile which can be used for a development installation:

::

  docker build -t vmshepherd .
  docker run -it  -p 8888:8888 -p 8000:8000 vmshepherd run


Usage
-----

After installation You need to create main configuration file(examples in config/ directory in this repo).
Run:

::

   vmshepherd -c CONFIGFILE


Development
-----------

We provide a Makefile and docker which can be used during development.

Makefile
..........

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
.............

Firstly build a image:

::

 docker build -t vmshepherd . --rm

Our Dockerfile create a ``ENTRYPOINT`` for our makefile, so basically you can execute make commands in docker container like run or show-docs.

Examples of usage:

* Running vmshepherd application:

::

  docker run -it  -p 8888:8888 -p 8000:8000 vmshepherd run

* Documentation:

::

  docker run -it  -p 8888:8888 -p 8000:8000 vmshepherd show-docs

Contributing to VmShepherd
----------------------------

Thank you for your interest in contributing to VmShepherd. Like always there are a many ways to contribute, and we appreciate all of them.

Pull requests and issues are the primary mechanism we use to change VmShepherd. Github itself has a great documentation
about using `Pull Requests <https://help.github.com/articles/about-pull-requests/>`_. We use the 
`"fork and pull" <https://help.github.com/articles/about-collaborative-development-models/>`_ model,
where contributors push changes to their personal fork and create pull requests to bring those changes into the source repository.

If you want to find something to work on, please check issues and our `roadmap <https://github.com/DreamLab/VmShepherd/projects/1>`_.


TL;DR
.......

Pull requests will need:

* Tests

* Documentation

* A logical series of `well written commits <https://github.com/alphagov/styleguides/blob/master/git.md>`_ 


License
-------

`Apache License 2.0 <LICENSE>`_
