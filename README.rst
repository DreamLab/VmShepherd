VmShepherd
==========


Introduction
------------

VmShepherd is an application that helps you maintain groups (clusters) of virtual machines. It keeps defined parameters (like count, image, etc.) by checking state in an IaaS layer, and tests underlying services with a specified health check.


Architecture
------------

VmShepherd is designed to be easily extensible with plugins. Empowered by ``python3`` and its ``asyncio`` module to facilitate scaling. The diagram below shows the base components of the app.

.. image:: https://user-images.githubusercontent.com/670887/41005281-1f5dfb08-691d-11e8-8221-f48f7acfc3a7.png

- **Preset Manager** is responsible for fetching cluster spec/definition (preset). Built-in presets: ``DirectoryDriver`` and ``GitRepoDriver``
- **Runtime Manger** exposes functionality of locking preset, and holds intermediate states. Currently available: ``InMemoryDriver``, ``PostgresDriver``, ``ZookeeperDriver``.
- **IaaS** is a glue (api wrapper) to IaaS provider, ``OpenStackDriver`` is the first implemented.
- **Healthcheck** allows to check service's state, not only for existence of a virtual machine. ``HttpHealthcheckDriver`` is built-in.


For more information, please take look at the `documentation <http://doc.dreamlab.pl/VmShepherd/index.html>`_.

Installation
--------------
Application requires python 3.6 or later. The latest stable version is `available on Pypi <https://pypi.org/project/vmshepherd/>`_.

::

  pip install vmshepherd

We also provide a ``Dockerfile`` which can be used for a development installation:

::

  docker build -t vmshepherd .
  docker run -it  -p 8888:8888 -p 8000:8000 vmshepherd run


Usage
-----

After installation you need to create a main configuration file (check examples in ``config/`` directory in this repo).

Run:

::

   vmshepherd -c CONFIGFILE


Contributing to VmShepherd
--------------------------

Thank you for your interest in contributing to VmShepherd. Like always there are many ways to contribute, and we appreciate all of them.

Pull requests and issues are the primary mechanism we use to change VmShepherd. Github itself has a great documentation
about using `Pull Requests <https://help.github.com/articles/about-pull-requests/>`_. We use the 
`"fork and pull" <https://help.github.com/articles/about-collaborative-development-models/>`_ model,
where contributors push changes to their personal fork and create pull requests to bring those changes into the source repository.

If you want to find something to work on, please check issues in our `roadmap <https://github.com/DreamLab/VmShepherd/projects/1>`_.


Check out the documetation `http://doc.dreamlab.pl/VmShepherd/development/index.html <http://doc.dreamlab.pl/VmShepherd/development/index.html>`_.

TL;DR
-----

Pull requests will need:

* Tests

* Documentation

* A logical series of `well written commits <https://github.com/alphagov/styleguides/blob/master/git.md>`_ 


License
-------

`Apache License 2.0 <LICENSE>`_
