from aiounittest import futurized, AsyncTestCase
from bidict import bidict
from unittest.mock import patch
from vmshepherd.iaas import OpenStackDriver


class MockVM:
    def __init__(self):
        pass


class TestOpenStackDriver(AsyncTestCase):

    def setUp(self):
        self.config = {
            'auth_url': 'http://keystone.api.int.iaas:5000/v3',
            'username': 'paas-c2-int-1-api-access',
            'password': '00e91e6550bcd29cfd306280df1caf5e',
            'project_id': '7b6052ae16434e79bc6456808c9f37a6',
            'project_name': 'c2-int-1',
            'api_version': '2.26',
            'flavor_id': '9c17893c-6fc4-4a69-96c8-6e5a8af6b836',
            'image_id': 'c0d3fe3e-52f9-4a2c-aeb1-b8c977fd7d17',
            'flavor': 'm1.tiny',
            'image': 'ubuntu-xenial',
            'project_domain_name': 'grupa.onet',
            'user_domain_name': 'default',
            'image_owner_ids': [
                'bb321996cce74e549c4ae00a67b657b8'
            ]
        }

        self.vm = {
            'name': 'test-vm-name',
            'id': '099fds8f9ds89fdsf',
            'metadata': {},
            'status': 'ACTIVE',
            'created': '2018-02-02T14:29:49Z',
            'updated': '2018-02-02T14:30:00Z',
            'tags': [],
            'addresses': {
                'pl-krk-2-int-301-c2-int-1': [
                    {
                        'OS-EXT-IPS-MAC:mac_addr': 'fa:16:3e:29:f1:bb',
                        'version': 4,
                        'addr': '10.185.138.36',
                        'OS-EXT-IPS:type': 'fixed'
                    }
                ]
            },
            'flavor': {'id': 'testflavorid'},
            'image': {'id': 'testimgid'}
        }

    async def test_map_vm_structure(self):
        '''
        Test if mapped structure is correct
        '''
        mock_list_flavors = patch('vmshepherd.iaas.OpenStackDriver._list_flavors').start()
        mock_list_flavors.return_value = futurized([])
        mock_list_images = patch('vmshepherd.iaas.OpenStackDriver._list_images').start()
        mock_list_images.return_value = futurized([])

        osd = OpenStackDriver(self.config)

        osd.flavors_map = bidict()
        osd.flavors_map['testflavorid'] = 'testflavorname'
        osd.images_map = bidict()
        osd.images_map['testimgid'] = 'testimgname'

        result = osd._map_vm_structure(self.vm)

        self.assertEqual(result.id, '099fds8f9ds89fdsf')
        self.assertEqual(result.name, 'test-vm-name')
        self.assertEqual(result.metadata, {})
        self.assertEqual(str(result.state), 'VmState.RUNNING')
        self.assertEqual(result.ip, ['10.185.138.36'])
        self.assertEqual(result.flavor, 'testflavorname')
        self.assertEqual(result.image, 'testimgname')

    async def test_initialize(self):
        '''
        test if initialize method set flavors and images properties
        '''
        image = {
            'id': 'imageid',
            'name': 'imagename',
            'created_at': '2018-02-02T14:30:00Z',
            'tags': ['latest']
        }
        flavor = {
            'id': 'flavorid',
            'name': 'flavorname'
        }
        mock_list_flavors = patch('vmshepherd.iaas.OpenStackDriver._list_flavors').start()
        mock_list_flavors.return_value = futurized([flavor])
        mock_list_images = patch('vmshepherd.iaas.OpenStackDriver._list_images').start()
        mock_list_images.return_value = futurized([image])

        osd = OpenStackDriver(self.config)

        await osd.initialize()
        self.assertEqual(osd.flavors_map['flavorid'], 'flavorname')
        self.assertEqual(osd.images_map['imageid'], 'imagename')
