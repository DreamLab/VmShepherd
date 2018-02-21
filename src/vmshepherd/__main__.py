import argparse
import asyncio
from vmshepherd.app import VmShepherd
from vmshepherd.utils import load_config_file


def main():
    args = get_args()
    config = load_config_file(args.config_file)
    config['autostart'] = False
    config['log_level'] = args.log_level
    config['listen_port'] = int(args.port)
    vmshepherd = VmShepherd(config)
    loop = asyncio.get_event_loop()
    task = asyncio.ensure_future(vmshepherd.run(args.run_once))
    try:
        loop.run_until_complete(task)
    except KeyboardInterrupt as e:
        print("VmShepherd shutting down...")
        task.cancel()
    finally:
        loop.close()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config-file', type=str, help='config file', required=True)
    parser.add_argument('-l', '--log-level', type=str, help='logging level', default='info')
    parser.add_argument('-p', '--port', type=int, help='port for panel and api', default=8888)
    parser.add_argument('-1', '--run-once', dest='run_once', action='store_true')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()
