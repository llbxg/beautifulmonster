from datetime import datetime as _datetime
from logging import getLogger as _getLogger
from pathlib import Path as _Path, PosixPath as _PosixPath
import re as _re
from typing import (NamedTuple as _NamedTuple, List as _List,
                    Union as _Union,
                    Optional as _Optional)


import yaml as _yaml


from .util import str_2_datetime as _s2d
from .ohh import Love as _Love
from .stew import Pot as _Pot

logger = _getLogger(__name__)


class Head(_NamedTuple):
    title: _Optional[str]
    created: _Optional[_datetime]
    updated: _Optional[_datetime]
    tag: _Optional[_List]


class Monster(_NamedTuple):
    name: str
    head: _Union[Head, None]
    body: str

    def extract_love(self, p_obj_d_contents=None, updated_automatically=True):
        path = self.name
        head = self.head
        if head is None:
            return None

        title = path if head.title is None else head.title
        created = head.created
        updated = head.updated

        if p_obj_d_contents is None:
            return _Love.make(path, title, created, updated)

        p_obj = p_obj_d_contents / self.name
        st_mtime = _datetime.fromtimestamp(p_obj.stat().st_mtime)
        if created is None:
            created = st_mtime
            updated = None
        elif updated_automatically and updated is None:
            updated = st_mtime

        return _Love.make(path, title, created, updated)

    @property
    def tags(self):
        if self.head is not None:
            return self.head.tag
        else:
            return []

    @property
    def html(self):
        return _Pot(self.body).pour()

    @property
    def doc(self):
        return _Pot(self.body).get_doc()

    @property
    def title(self):
        if self.head is not None:
            return self.head.title
        return None

    @property
    def full_str(self):
        h = ""
        if self.head is not None:
            h = " ".join([str(i) for i in self.head])
        return self.name + self.body + h


def read_str_monster(p_obj):
    if not isinstance(p_obj, _PosixPath):
        p_obj = _Path(str(p_obj))

    ext = p_obj.suffix

    if ext != ".md":
        return None

    if p_obj.exists():
        with p_obj.open() as f:
            str_body = f.read()
    else:
        logger.warning(f"Unable to read {p_obj}, maybe it doesn't exist.")
        str_body = None

    return str_body


def create_head(str_header):
    yaml_header = _yaml.load(str_header, Loader=_yaml.BaseLoader)

    title = yaml_header.get('title', None)
    created = _s2d(yaml_header.get('created', None))
    updated = _s2d(yaml_header.get('updated', None))
    tag = yaml_header.get('tag', [])

    return Head(title, created, updated, tag)


def monster_surgery(str_body, mold_head=True):
    if str_body is None:
        return None, ""

    if not str_body.startswith("---"):
        return None, str_body

    header, main = None, str_body

    pattern = r"^---(?P<header>.*?)---[ \t]*\r?\n(?P<main>.*)"
    m = _re.search(pattern, str_body, _re.DOTALL)
    if m is not None:
        str_header = m.group("header")
        main = m.group("main")
        if mold_head:
            header = create_head(str_header)

    return header, main


def create_monster(p_obj, mold_head=True):
    str_body = read_str_monster(p_obj)
    body = monster_surgery(str_body, mold_head=mold_head)
    p = p_obj.relative_to(p_obj.cwd())
    path = str(_Path(*p.parts[1:]))
    return Monster(path, *body)
