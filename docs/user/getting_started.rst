===============
Getting started
===============

Run VmShepherd in Docker
------------------------

The simplest way to run VmShepherd with an example config is to use docker.

.. code-block:: bash
 
   git clone https://github.com/DreamLab/VmShepherd.git
   cd VmShepherd
   docker build -t vmshepherd . --rm
   docker run -it -p 8888:8888 -p 8000:8000 vmshepherd run

Using python 3.6 

.. code-block:: bash
 
   git clone https://github.com/DreamLab/VmShepherd.git
   cd VmShepherd
   python setup.py install
   vmshepherd -c config/settings.example.yaml

