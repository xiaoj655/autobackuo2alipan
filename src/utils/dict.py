from datetime import datetime
from common.constant import cntz
from utils.time import iso8601str

def mutl_dict_getter(keys: list[str], *dicts: dict[str, str]) -> list[str]:
    if "created_at" in keys:
        dicts[0].update({"created_at": iso8601str()})
    if "updated_at" in keys:
        dicts[0].update({"updated_at": iso8601str()})

    all_dict = {k: v for d in dicts for k, v in d.items()}
    return [all_dict.get(key, '') for key in keys]

def dict_zipper(keys: list[str], values: list[str]) -> dict[str, str]:
    return dict(zip(keys, values))
