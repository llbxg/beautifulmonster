import yaml as _yaml

from .ohh import Blue as _Blue, Love as _Love
from .stew import Pot as _Pot
from .utils import (make_hash as _make_hash, make_path as _make_path,
                    read_txt as _read_txt,
                    separate_yamlblock_contents as _s_y_c,)


class Monster(object):
    """
    Monsterはtemplateへ情報を提供する。Loveを通してdbとデータを共有する。
    """

    def __init__(self, path):
        self.text = _read_txt(path)

        self.yamlblock, self.contents = _s_y_c(self.text)
        self.hash2 = _make_hash(self.contents)

        self.config = {}
        self.hash = 'no yamlblock'
        if self.yamlblock is not None:
            self.config = _yaml.load(self.yamlblock, Loader=_yaml.BaseLoader)
            self.hash = _make_hash(self.yamlblock)

        self.path = _make_path(path)

        self.love = _Love(self.path,
                          self.config.get('title', 'no title'),
                          self.config.get('created', 'no created'),
                          self.config.get('rewrote', None),
                          self.hash, self.hash2)

        tags = self.config.get('tag', [])
        if isinstance(tags, str):
            tags = [tags]

        self.love.tags = [_Blue(self.path, tag) for tag in tags]

        self.soup = _Pot(self.contents)

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
        return self.love.title

    @property
    def katex(self):
        return self.soup.katex

    @property
    def doc(self):
        return self.soup.get_doc()

    @property
    def tags_str(self):
        return " " + " ".join([tag.tag for tag in self.love.tags])
