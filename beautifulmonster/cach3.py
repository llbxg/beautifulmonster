import datetime as _datetime
from dbm import error as _dbm_error
from logging import getLogger as _getLogger
from multiprocessing import Pool as _Pool
from pathlib import Path as _Path
import shelve as _shelve


_logger = _getLogger(__name__)

PATH_CWD = _Path().cwd()
PATH_CACHE = PATH_CWD


def get_cache(p_obj_cache, key):
    try:
        with _shelve.open(str(p_obj_cache)) as c:
            cache_updated = c.get(key, None)

    except _dbm_error as e:
        _logger.info(f"dbm.error: {e}. "
                     f"The file format of {p_obj_cache} is not supported.")
        cache_updated = None

    return cache_updated


def get_files_cache(p_obj_cache):
    return get_cache(p_obj_cache, 'file')


def get_scss_cache(p_obj_cache):
    return get_cache(p_obj_cache, 'scss')


def update_cache(p_obj_cache, key):
    now = _datetime.datetime.now()
    with _shelve.open(str(p_obj_cache)) as c:
        c[key] = now
    return now


def update_files_cache(p_obj_cache):
    return update_cache(p_obj_cache, "file")


def update_scss_cache(p_obj_cache):
    return update_cache(p_obj_cache, "scss")


def stime(x):
    now, pobj = x
    if _datetime.datetime.fromtimestamp(pobj.stat().st_ctime) > now:
        return pobj
    return None


def check_updated(cache_updated, pobj_all):
    if cache_updated is None:
        return set(pobj_all)

    g = ((cache_updated, pobj) for pobj in pobj_all)

    p = _Pool(4)
    result = set(p.map(stime, g))
    result.discard(None)

    return set(result)


def new_files(cache_updated, pobj_parent):
    pobj_all = pobj_parent.glob("**/*.md")

    return check_updated(cache_updated, pobj_all)
