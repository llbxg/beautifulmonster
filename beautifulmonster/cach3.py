from glob import glob as _glob
from hashlib import md5
from os import makedirs as _makedirs, remove as _remove
from os.path import (join as _join, exists as _exists, isdir as _isdir,
                     splitext as _splitext, basename as _basename)
from pathlib import Path
import shelve as _shelve
from typing import NamedTuple as _NamedTuple

import sass as _sass

from .config import path_templates_jinja2 as _path_templates


def mk_cache_dic(path):
    _makedirs(path, exist_ok=True)


def make_template_in_templates(template_file, template_folder):

    if _exists(template_file):
        return 0

    _makedirs(template_folder, exist_ok=True)

    with open(_join(_path_templates, 'template.j2')) as f:
        template = f.read()

    with open(template_file, mode='w') as f:
        f.write(template)


def hash_rewrote(path):
    p = Path(path)
    rewrote = p.stat().st_mtime
    return md5(str(rewrote).encode("utf-8")).hexdigest()


def hash_contents(path):
    with open(path, mode='br') as f:
        data = f.read()

    return md5(data).hexdigest()


class Cache(_NamedTuple):
    rewrote: str
    contents: str


def basename_wo_ext(path):
    return _splitext(_basename(path))[0]


def scss_2_css(file, path_css):
    css = _sass.compile(filename=file)
    base = basename_wo_ext(file)
    filename = _join(path_css, f"{base}.css")
    with open(filename, mode="w") as f:
        f.write(css)


def compile_scss(cache_dict, path_scss, path_css):
    if not _isdir(path_scss):
        return 0

    scss_files = _glob(path_scss+'/*.scss')

    if len(scss_files) == 0:
        return 0

    _makedirs(path_css, exist_ok=True)

    with _shelve.open(_join(cache_dict, "scss_cache")) as s:
        for f in s.keys() - set(scss_files):
            _remove(_join(path_css, f"{basename_wo_ext(f)}.css"))
            del s[f]

        for file in scss_files:
            h1 = hash_rewrote(file)

            file_cache = s.get(file, None)

            if file_cache is None:
                s[file] = Cache(h1, hash_contents(file))
                scss_2_css(file, path_css)

            else:
                if file_cache.rewrote != hash_rewrote(file):
                    h2 = hash_contents(file)
                    if file_cache.contents != h2:
                        s[file] = Cache(h1, h2)
                        scss_2_css(file, path_css)
