import logging
import time
from .abstract import AbstractIaasDriver
from .exception import IaasException, IaasPresetConfigurationException, IaasCommunicationException, IaasAuthException
from .vm import Vm, VmState
from bidict import bidict
from datetime import datetime
from keystoneauth1 import exceptions as keystoneauth_exceptions
from novaclient.exceptions import ClientException, NotFound, MethodNotAllowed, NotAcceptable
from asyncnovaclient import NovaClient, GlanceClient, AuthPassword


class OpenStackDriver(AbstractIaasDriver):

    def __init__(self, *args, **kwargs):
        self.config = {
            'auth_url': kwargs['auth_url'],
            'username': kwargs['username'],
            'password': kwargs['password'],
            'project_name': kwargs['project_name'],
            'user_domain_name': kwargs['user_domain_name'],
            'project_domain_name': kwargs['project_domain_name'],
            'api_version': kwargs['api_version'],
            'image_owner_ids': kwargs['image_owner_ids']
        }

    def openstack_exception(func):
        '''
            Openstack exceptions decorator
        '''
        async def wrap(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except keystoneauth_exceptions.http.Unauthorized as e:
                logging.error(e)
                raise IaasAuthException
            except keystoneauth_exceptions.auth.AuthorizationFailure as e:
                logging.error(e)
                raise IaasAuthException
            except (NotFound, MethodNotAllowed, NotAcceptable) as e:
                logging.error(e)
                raise IaasCommunicationException
            except ClientException as e:
                logging.error(e)
                raise IaasPresetConfigurationException
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
                self.glance = GlanceClient('2', session=self.auth)

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
            self.flavors_map.put(flavor.id, flavor.name, on_dup_key='OVERWRITE', on_dup_val='OVERWRITE')

        for image in images:
            # @TODO filetes :
            # @TODO filtering by owner
            # if hasattr(image, 'owner_id') and  image.owner_id in self.config['image_owner_ids']:
            #  @TODO enable filtering by tag
            # if 'lastest' in image.tags:
            self.images_details[image.id] = {
                'name': image.name,
                'created_at': image.created_at,
                'latest': 'latest' in image.tags
            }
            self.images_map.put(image.id, image.name, on_dup_key='OVERWRITE', on_dup_val='OVERWRITE')

    @initialize_openstack
    @openstack_exception
    async def create_vm(self, preset_name, image, flavor, security_groups=None,
                        userdata=None, key_name=None, availability_zone=None, subnet=None):
        '''
          Create VM
         :arg preset_name: string
         :arg image: string image id
         :arg flavor: string flavor id
         :arg security_groups:  list
         :arg userdata: dict
         :arg key_name: string
         :arg availability_zone:
         :arg subnet:
         :returns list Vm objects
         @TODO
         1. returns image id
        '''

        image_id = self.images_map.inv.get(image)
        flavor_id = self.flavors_map.inv.get(flavor)
        body = {
            "name": preset_name,
            "flavorRef": flavor_id,
            "imageRef": image_id,
            "security_groups": security_groups,
            "user_data": userdata,
            "key_name": key_name
        }
        logging.info("creating vm: %s", body)
        return self.nova.servers.create(body=body)

    @initialize_openstack
    @openstack_exception
    async def list_vms(self, preset_name):
        '''
        List VMs by preset name
        :arg present_name: string
        '''

        logging.info("listing vm: %s", preset_name)
        servers = self.nova.servers.list(params={'name': preset_name})
        result = []
        for server in servers:
            result.append(self._map_vm_structure(server))
        return result
        # except Exception as e:
        #    logging.error(e)
        #    raise IaasSystemException

    @openstack_exception
    async def terminate_vm(self, vm_id):
        '''
         Terminate VM
         :arg vm_id: string
        '''
        logging.info("killing vm: %s", vm_id)
        return self.nova.servers.force_delete(vm_id)

    @initialize_openstack
    @openstack_exception
    async def get_vm(self, vm_id):
        '''
        Get VM
        :arg vm_id: string
        :returns vm: object
        '''
        return self._map_vm_structure(self.nova.servers.get(vm_id))

    @openstack_exception
    async def _list_flavors(self):
        '''
        Returns list of flavors from Openstack
        '''
        logging.info("listing flavors")
        return self.nova.flavors.list()

    @openstack_exception
    async def _list_images(self):
        '''
        Returns list of images from OpenStack
        '''
        logging.info("listing images")
        return self.glance.images.list()

    def _map_vm_structure(self, vm):
        '''
        Vm unification
        :arg vm: object
        :returns object
        '''
        ip = self._extract_ips(vm.addresses)
        created = datetime.strptime(vm.created, '%Y-%m-%dT%H:%M:%SZ').timestamp()
        flavor = self.flavors_map.get(vm.flavor.get('id'))
        image = self.images_map.get(vm.image.get('id'))
        state = self._map_vm_status(vm.status)
        iaasvm = Vm(self, vm.id, vm.name, ip, created, state=state, metadata=vm.metadata, tags=vm.tags, flavor=flavor,
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
