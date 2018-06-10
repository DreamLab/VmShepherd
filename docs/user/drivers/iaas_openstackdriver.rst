===============
OpenStackDriver
===============

``OpenStackDriver`` is the `asyncopenstackclient <https://github.com/DreamLab/AsyncOpenStackClient>`_ library wrapper.

Main configuration:

.. code-block:: yaml

   auth_url: http://KEYSTONE:5000/v3
   username: USER
   password: PASS
   user_domain_name: default    # for auth only
   image_owner_ids:
     - user

Parameters:

1. **auth_url** - Keystone public api endpoint.
2. **username** - Openstack/keystone username.
3. **password** - Openstack/keystone password.
4. **user_domain_name** - User domain name.
5. **image_owner_ids** - Create method need image name. To avoid conflicts with public images created by other openstack users we can add users ids which images we want to use.

