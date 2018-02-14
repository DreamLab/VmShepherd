import json
from pkg_resources import iter_entry_points


class Driver:

    _cache = {}

    @classmethod
    def get(cls, group: str, cfg: dict) -> object:
        _hash = hash(json.dumps(cfg, sort_keys=True))
        if _hash not in cls._cache:
            for entry_point in iter_entry_points(group=f'vmshepherd.driver.{group}'):
                if entry_point.name == cfg['driver']:
                    _class = entry_point.load()
                    cls._cache[_hash] = _class(**cfg.get('driver_params', {}))
                    break
            else:
                raise RuntimeError(f"Cannot find driver {cfg['driver']} for {group}.")
        return cls._cache[_hash]

    @classmethod
    def flush_cache(cls):
        cls._cache = {}
