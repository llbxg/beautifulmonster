from datetime import timedelta as _timedelta

import yaml as _yaml

from .ohh import Blue as _Blue, Love as _Love
from .stew import Pot as _Pot
from .utils import (make_hash as _make_hash, make_path as _make_path,
                    read_txt as _read_txt, get_rewrote as _get_rewrote,
                    separate_yamlblock_contents as _s_y_c,
                    str_2_datetime as _str_2_datetime,
                    get_created as _get_created)


from markupsafe import Markup as _Markup


class Monster(object):
    """
    Monsterはtemplateへ情報を提供する。Loveを通してdbとデータを共有する。
    """

    def __init__(self, path, auto_rewrote=None):
        self.text = _read_txt(path)

        self.yamlblock, self.contents = _s_y_c(self.text)
        self.hash2 = _make_hash(self.contents)
        self.soup = _Pot(self.contents)

        self.config = {}
        self.hash = 'no yamlblock'
        if self.yamlblock is not None:
            self.config = _yaml.load(self.yamlblock, Loader=_yaml.BaseLoader)
            self.hash = _make_hash(self.yamlblock)

        self.path = _make_path(path)

        title = self.soup.first_h1()
        if title is None:
            title = self.path[1:-1]
        for v in ['title', 'alias']:
            title = self.config.get(v, title)

        created = (self.config.get('created', _get_created(path)))
        created = _str_2_datetime(created)

        rewrote = None
        if (auto_rewrote is not None) and isinstance(auto_rewrote, int):
            delta = _timedelta(days=auto_rewrote)
            rewrote = _get_rewrote(path)
            if (created is not None) and ((rewrote - created) < delta):
                rewrote = None

        self.love = _Love(self.path, title,
                          self.config.get('created', created),
                          self.config.get('rewrote', rewrote),
                          self.hash, self.hash2)

        tags = self.config.get('tag', [])
        if isinstance(tags, str):
            tags = [tags]

        self.love.tags = [_Blue(self.path, tag) for tag in tags]

    @property
    def html(self):
        return self.soup.pour()

    def __repr__(self):
        return (f'Monster({self.path})')

    # from template ---
    def __getitem__(self, key):
        return getattr(self.love, key)

    @property
    def title(self):
        return _Markup(self.love.title)

    @property
    def katex(self):
        return self.soup.katex

    @property
    def doc(self):
        return self.soup.get_doc()

    @property
    def tags_str(self):
        return " " + " ".join([tag.tag for tag in self.love.tags])
