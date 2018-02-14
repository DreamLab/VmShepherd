import asyncio
import collections
import yaml


def update_dict_recursively(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = update_dict_recursively(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def load_config_file(path):
    with open(path, 'r') as f:
        config = yaml.load(f)
    return config


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
