from os import makedirs as _makedirs


def mk_cache_dic(path):
    _makedirs(path, exist_ok=True)
