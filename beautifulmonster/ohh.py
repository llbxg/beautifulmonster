from sqlalchemy import desc as _desc
from sqlalchemy.ext.declarative import declarative_base as _declarative_base
from sqlalchemy.orm import backref as _backref, relationship as _relation
from sqlalchemy.schema import Column as _Column, ForeignKey as _ForeignKey
from sqlalchemy.sql import func as _func
from sqlalchemy.types import (DateTime as _DateTime,
                              Integer as _Integer, String as _String)
Base = _declarative_base()


class Love(Base):
    __tablename__ = 'love_table'

    path = _Column(_String, primary_key=True)
    title = _Column(_String, nullable=False)
    created = _Column(_DateTime)
    updated = _Column(_DateTime)

    def __repr__(self):
        s = [f"{k}={v}" for k, v in self.__dict__.items() if k[0] != "_"]
        return f"Love({', '.join(s)})"

    @classmethod
    def make(cls, path, title, created, updated):
        love = cls()
        love.path = path
        love.title = title
        love.created = created
        love.updated = updated
        return love

    def update(self, love, st_mtime, first=True):
        self.title = love.title
        if self.created is None:
            self.created = st_mtime
        elif first:
            self.updated = st_mtime

    def tuple(self):
        return (self.path, self.title, self.created, self.updated)

    def to_dict(self):
        created, updated = None, None
        if self.created is not None:
            created = self.created.strftime('%Y-%m-%d')
        if self.updated is not None:
            updated = self.updated.strftime('%Y-%m-%d')

        path = "/" + self.path.split('.')[0]
        return {'path': path, 'title': self.title, 'created': created,
                'updated': updated, 'tags': [tag.tag for tag in self.tags]}


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
        return f"Blue({self.love_path}, {self.tag})"

    @property
    def path(self):
        return self.love_path


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
