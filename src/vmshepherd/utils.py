import aiofiles
import asyncio
import collections
import copy
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
