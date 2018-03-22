import base64
import logging
import time
from .abstract import AbstractIaasDriver
from .exception import IaasException
from .vm import Vm, VmState
from asyncopenstackclient import NovaClient, GlanceClient, AuthPassword
from bidict import bidict
from datetime import datetime
from simplejson.errors import JSONDecodeError


class OpenStackDriver(AbstractIaasDriver):

    def __init__(self, config):
        self.config = config

    def openstack_exception(func):
        '''
            Openstack exceptions decorator
        '''
        async def wrap(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logging.error(e)
                raise IaasException
        return wrap

    def initialize_openstack(func):
        '''
            Initialize and refresh openstack connection

        '''
        async def wrap(self, *args, **kwargs):
            if not hasattr(self, 'auth') or self.auth.verify() is True:
                self.auth = AuthPassword(auth_url=self.config['auth_url'],
                                         username=self.config['username'],
                                         password=self.config['password'],
                                         project_name=self.config['project_name'],
                                         user_domain_name=self.config['user_domain_name'],
                                         project_domain_name=self.config['project_domain_name'])
                self.nova = NovaClient(self.config['api_version'], session=self.auth)
                self.glance = GlanceClient(session=self.auth)
                await self.nova.init_api()
                await self.glance.init_api()

            if not hasattr(self, 'last_init') or self.last_init < (time.time() - 60):
                await self.initialize()
                self.last_init = time.time()
            return await func(self, *args, **kwargs)
        return wrap

    async def initialize(self):
        '''
         Initialize static data like images and flavores and set it as object property
        '''
        flavors = await self._list_flavors()
        images = await self._list_images()

        self.flavors_map = bidict()
        self.images_map = bidict()
        self.images_details = {}

        for flavor in flavors:
            self.flavors_map.put(flavor['id'], flavor['name'], on_dup_key='OVERWRITE', on_dup_val='OVERWRITE')

        for image in images:
            # @TODO filetes :
            # @TODO filtering by owner
            # if hasattr(image, 'owner_id') and  image.owner_id in self.config['image_owner_ids']:
            #  @TODO enable filtering by tag
            # if 'lastest' in image.tags:
            self.images_details[image['id']] = {
                'name': image['name'],
                'created_at': image['created_at'],
                'latest': 'latest' in image['tags']
            }
            self.images_map.put(image['id'], image['name'], on_dup_key='OVERWRITE', on_dup_val='OVERWRITE')

    @initialize_openstack
    @openstack_exception
    async def create_vm(self, preset_name, image, flavor, security_groups=None,
                        userdata=None, key_name=None, availability_zone=None, subnets=None):
        '''
          Create VM
         :arg preset_name: string
         :arg image: string image id
         :arg flavor: string flavor id
         :arg security_groups:  list
         :arg userdata: string
         :arg key_name: string
         :arg availability_zone: string
         :arg subnets: list
         :returns list Vm objects
         @TODO
         1. returns image id
        '''
        image_id = self.images_map.inv.get(image)
        flavor_id = self.flavors_map.inv.get(flavor)
        body = {
            "server": {
                "name": preset_name,
                "flavorRef": flavor_id,
                "imageRef": image_id,
                "security_groups": [{"name": group} for group in security_groups],
                "user_data": userdata
            }
        }
        if availability_zone is not None:
            body["server"].update({"availability_zone": availability_zone})
        if subnets is not None:
            body["server"].update({"networks": [{'uuid': subnet['net-id']} for subnet in subnets]})
        if userdata is not None:
            userdata = userdata.encode('utf-8')
            userdata = base64.b64encode(userdata).decode('utf-8')
            body["server"].update({"user_data": userdata})

        result = await self.nova.api.servers.create(body=body)
        return result.body["server"]

    @initialize_openstack
    @openstack_exception
    async def list_vms(self, preset_name):
        '''
        List VMs by preset name
        :arg present_name: string
        '''

        servers = await self.nova.api.servers.list(params={'name': f'^{preset_name}$'})
        result = []
        for server in servers.body["servers"]:
            result.append(self._map_vm_structure(server))
        return result

    @openstack_exception
    async def terminate_vm(self, vm_id):
        '''
         Terminate VM
         :arg vm_id: string
        '''
        try:
            await self.nova.api.servers.force_delete(vm_id)
        except JSONDecodeError as exc:
            logging.info("nova sent 'content-type: application/json' but no content appeared, whatever")
            pass
        except Exception:
            raise

    @initialize_openstack
    @openstack_exception
    async def get_vm(self, vm_id):
        '''
        Get VM
        :arg vm_id: string
        :returns vm: object
        '''
        result = await self.nova.api.servers.get(vm_id)
        return self._map_vm_structure(result.body["server"])

    @openstack_exception
    async def _list_flavors(self):
        '''
        Returns list of flavors from Openstack
        '''
        result = await self.nova.api.flavors.list()
        return result.body['flavors']

    @openstack_exception
    async def _list_images(self):
        '''
        Returns list of images from OpenStack
        '''
        result = await self.glance.api.images.list()
        return result.body['images']

    def _map_vm_structure(self, vm):
        '''
        Vm unification
        :arg vm: object
        :returns object
        '''
        ip = self._extract_ips(vm['addresses'])
        created = datetime.strptime(vm['created'], '%Y-%m-%dT%H:%M:%SZ')
        flavor = self.flavors_map.get(vm['flavor'].get('id'))
        image = self.images_map.get(vm['image'].get('id'))
        state = self._map_vm_status(vm['status'])
        iaasvm = Vm(self, vm['id'], vm['name'], ip, created, state=state, metadata=vm['metadata'], tags=vm.get('tags', []), flavor=flavor,
                    image=image)
        return iaasvm

    def _map_vm_status(self, openstack_status):
        '''
         Map openstack vm statuses to vmshepherd vm statuses
         openstack vm statuses: ACTIVE, BUILD, DELETED, ERROR, HARD_REBOOT, MIGRATING, PASSWORD, PAUSED, REBOOT,
         REBUILD, RESCUE, RESIZE, REVERT_RESIZE, SHELVED, SHELVED_OFFLOADED, SHUTOFF, SOFT_DELETED, SUSPENDED, UNKNOWN,
         VERIFY_RESIZE

         :arg string openstack_status
         :returns string
        '''
        statuses = {
            VmState.TERMINATED: [
                'ERROR',
                'DELETED',
                'SHUTOFF',
                'SOFT_DELETED',
                'SUSPENDED'  # do ustalenia
            ],
            VmState.PENDING: [
                'BUILD',
                'REBUILD'
            ],
            VmState.RUNNING: ['ACTIVE']
        }

        for vmstate, value in statuses.items():
            if openstack_status in value:
                return vmstate

        return VmState.UNKNOWN

    def _extract_ips(self, data):
        '''
        Extract ip addressess from openstack structure
        {
          'pl-krk-2-int-301-c2-int-1': [
           {
             'OS-EXT-IPS-MAC:mac_addr': 'fa:16:3e:29:f1:bb',
             'version': 4,
             'addr': '10.185.138.36',
             'OS-EXT-IPS:type': 'fixed'
          }
         ]
       }
       :arg data: dict
       :returns list
       '''
        result = []
        for region in data.items():
            for interface in region[1]:
                result.append(interface['addr'])
        return result