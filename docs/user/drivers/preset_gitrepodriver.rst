=============
GitRepoDriver
=============

GitRepoDriver get preset configurations from git repository.
For now supports only public repositories.

Main configuration:

.. code-block:: yaml

   repositories:
     presets1: http://gitrepo.local/presets1.git
     presets2: http://gitrepo.local/presets2.git
   clone_dir: /tmp/clonedir

Parameters:

1. **repositories** - List of repositories with preset configurations. One repository can hold more than one preset configuration.
2. **clone_dir** - directory to clone git repositories. Default: *tempdir*/vmshepherd.

