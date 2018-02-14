import os.path

root_dir = os.path.dirname(__file__)


example_config = {
    'autostart': False,
    'runtime': {
        'driver': 'InMemoryDriver',
        'driver_params': {}
    },
    'presets': {
        'driver': 'DirectoryDriver',
        'driver_params': {
            'path': os.path.join(root_dir, 'presets.d')
        }
    },
    'defaults': {
        'iaas': {
            'driver': 'DummyIaasDriver',
            'driver_params': {
                'api_key': 'asd',
                'api_secret': 'asd'
            }
        },
        'healthcheck': {
            'driver': 'HttpHealthcheck',
            'driver_params': {
                'conn_timeout': 1,
                'read_timeout': 1,
                'port': 7007,
                'path': '/',
                'method': 'GET',
                'check_status': 200
            },
            'terminate_heatlh_failed_delay': 1000
        }
    }
}
