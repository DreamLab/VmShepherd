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
        config = yaml.load(f)
    return config


async def async_load_from_file(path):
    async with aiofiles.open(path, mode='r') as f:
        contents = await f.read()
        data = yaml.load(contents)
    return data


# Following functions are used in dummy drivers

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
        record.msg = '[%s] %s' % (self._prefix, record.msg)
        return True


def prefix_logging(prefix, handler=None):
    if handler is not None:
        handlers = [handler]
    else:
        handlers = logging.getLogger().handlers
    for hndlr in handlers:
        hndlr.addFilter(PrefixFilter(prefix))
