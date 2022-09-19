from sqlalchemy import desc as _desc
from sqlalchemy.ext.declarative import declarative_base as _declarative_base
from sqlalchemy.orm import backref as _backref, relation as _relation
from sqlalchemy.schema import Column as _Column, ForeignKey as _ForeignKey
from sqlalchemy.sql import func as _func
from sqlalchemy.types import (DateTime as _DateTime,
                              Integer as _Integer, String as _String)

from .utils import str_2_datetime as _str_2_datetime


Base = _declarative_base()


class Love(Base):
    __tablename__ = 'love_table'

    path = _Column(_String, primary_key=True)
    title = _Column(_String, nullable=False)
    created = _Column(_DateTime)
    rewrote = _Column(_DateTime)
    hash = _Column(_String, nullable=False)
    hash2 = _Column(_String, nullable=False)

    def __init__(self, path, title, created, rewrote, hash, hash2):
        self.set_all(path, title, created, rewrote, hash, hash2)

    def __repr__(self):
        members = f'{self.path}, {self.title}, '\
                  + f'{self.created}, {self.rewrote},'\
                  + f'{self.hash}, {self.hash2}'
        return f'Love({members})'

    def to_dict(self):
        return {'path': self.path, 'title': self.title, 'date': self.date,
                'tags': [tag.tag for tag in self.tags]}

    def to_tuple(self):
        return (self.path, self.title,
                self.created, self.rewrote, self.hash, self.hash2)

    @property
    def date(self):
        d = self.rewrote or self.created
        if d is not None:
            return d.strftime('%Y-%m-%d')
        return None

    def set_all(self, path, title, created, rewrote, hash, hash2):
        self.path = path
        self.title = title
        self.created = _str_2_datetime(created)
        self.rewrote = _str_2_datetime(rewrote)
        self.hash = hash
        self.hash2 = hash2


class Blue(Base):
    __tablename__ = 'blue_table'

    id = _Column(_Integer, primary_key=True)
    love_path = _Column(_String, _ForeignKey('love_table.path'),
                        nullable=False)
    tag = _Column(_String, nullable=False,)

    backref_ = _backref('tags', uselist=True, cascade='all, delete-orphan',)
    _ = _relation('Love', uselist=False, backref=backref_)

    def __init__(self, path, tag):
        self.love_path = path
        self.tag = tag

    def __repr__(self):
        return f'Blue({self.id}, {self.love_path}, {self.tag})'


def _lead_or_lag(sess, path, less_than=True):
    def inequality(x, y):
        if less_than:
            return x < y
        return x > y

    def max_or_min(x):
        if less_than:
            return _func.max(x)
        return _func.min(x)

    now_love = sess.query(Love).filter(Love.path == path).subquery()
    ll_love = sess.query(Love).\
        order_by(_desc(Love.created)).\
        filter(inequality(Love.created, now_love.c.created)).subquery()

    created_ = sess.query(
        max_or_min(ll_love.c.created).label('day')).subquery()
    return sess.query(Love).filter(Love.created == created_.c.day).first()


def lag(sess, path):
    return _lead_or_lag(sess, path, less_than=True)


def lead(sess, path):
    return _lead_or_lag(sess, path, less_than=False)
