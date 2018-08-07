''' Abstract class of healthcheck. There is only one method to implement,
that determines state of Vm or its underlying services.

Initialization - consider following config:

::

   healthcheck:
     driver: SomeHC
     param1: AAAA
     param2: BBBB
     some_x: CCC

All params will be passed as config dict to the driver init:

'''


class AbstractHealthcheck:

    def __init__(self, config):
        pass

    async def is_healthy(self, vm):
        ''' Checks that is a given vm is healthy

        :arg vmshepherd.iaas.Vm vm: Vm object

        Returns boolean - True means is healthy, False means unhealthy.
        '''
        raise NotImplementedError
