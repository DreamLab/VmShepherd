import json
from pkg_resources import iter_entry_points


class Drivers:

    _loaded = {}

    @classmethod
    def get(cls, group: str, cfg: dict, **kwargs) -> object:
        _hash = hash(json.dumps(cfg, sort_keys=True))
        if _hash not in cls._loaded:
            for entry_point in iter_entry_points(group=f'vmshepherd.driver.{group}'):
                if entry_point.name == cfg['driver']:
                    _class = entry_point.load()
                    try:
                        cls._loaded[_hash] = _class(config=cfg, **kwargs)
                    except Exception as exc:
                        raise RuntimeError(f"Cannot load driver {cfg['driver']} for {group}.") from exc
                    break
            else:
                raise RuntimeError(f"Cannot find driver {cfg['driver']} for {group}.")
        return cls._loaded[_hash]

    @classmethod
    def flush(cls):
        cls._loaded = {}
