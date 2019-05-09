import aiofiles
import asyncio
import collections
import copy
import logging
import random
import socket
import string
import yaml


def get_merged_dict_recursively(d, u):
    new = copy.deepcopy(d)
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            new[k] = get_merged_dict_recursively(new.get(k, {}), v)
        else:
            new[k] = v
    return new


def load_config_file(path):
    with open(path, 'r') as f:
        config = yaml.safe_load(f)
    return config


async def async_load_from_file(path):
    async with aiofiles.open(path, mode='r') as f:
        data = await f.read()
    return data


async def async_load_from_yaml_file(path):
    contents = await async_load_from_file(path)
    return yaml.safe_load(contents)


def add_async_delay(func):
    async def wrapper(*args, **kwargs):
        await asyncio.sleep(0.1)
        return await func(*args, **kwargs)
    return wrapper


def next_id():
    i = 0
    while True:
        yield i
        i += 1


def gen_id(rnd_length):
    hostname = socket.gethostname()
    rnd = ''.join(random.choice(
        string.ascii_lowercase + string.digits) for i in range(rnd_length)
    )
    return f'{hostname}-{rnd}'


class PrefixFilter(logging.Filter):
    """Prepends prefix to logged message."""
    def __init__(self, prefix):
        self._prefix = prefix

    def filter(self, record):
        if hasattr(record, 'preset'):
            record.msg = '[%s][%s][%s]: %s' % (self._prefix, record.preset, record.module, record.msg)
        else:
            record.msg = '[%s][%s]: %s' % (self._prefix, record.module, record.msg)
        return True


def prefix_logging(prefix, handler=None):
    if handler is not None:
        handlers = [handler]
    else:
        handlers = logging.getLogger().handlers
    for hndlr in handlers:
        hndlr.addFilter(PrefixFilter(prefix))
