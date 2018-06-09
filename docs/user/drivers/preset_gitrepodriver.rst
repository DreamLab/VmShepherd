=============
GitRepoDriver
=============

``GitRepoDriver`` loads preset configurations from a git repository.

For now it only supports public repositories.

Main configuration:

.. code-block:: yaml

   repositories:
     presets1: http://gitrepo.local/presets1.git
     presets2: http://gitrepo.local/presets2.git
   clone_dir: /tmp/clonedir

Parameters:

1. **repositories** - List of repositories with a preset configurations. One repository can hold more than one preset configuration.
2. **clone_dir** - directory to clone git repositories. Default: *tempdir*/vmshepherd.

