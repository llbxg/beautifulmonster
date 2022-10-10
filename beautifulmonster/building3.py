from glob import glob as _glob
from logging import getLogger as _getLogger
from os.path import join as _join, exists as _exists
from os import makedirs as _makedirs

import sass as _sass
from sqlalchemy import create_engine as _create_engine, and_ as _and_
from sqlalchemy.orm import (scoped_session as _scoped_session,
                            sessionmaker as _sessionmaker)

from .monster import Monster as _Monster
from .ohh import Base as _Base, Love as _Love, Blue as _Blue
from .puzzle import make_template as _make_template, url_2_md as _url_2_md
from .utils import debug_mode as _debug_mode


logger = _getLogger(__name__)


def make_session(url):
    engine = _wrapper_create_engine(url)
    _Base.metadata.create_all(engine)
    session = _scoped_session(_sessionmaker(autocommit=False, bind=engine))
    return session


def _wrapper_create_engine(url):
    db_name = url.split(':')[0]
    connect_args = {"check_same_thread": False} if db_name == 'sqlite' else {}
    logger.debug(f'Using {db_name}.')
    engine = _create_engine(url, connect_args=connect_args)
    return engine


def building2(config):
    template_file = config.template_file
    if not _exists(template_file):
        _makedirs(config.template_folder, exist_ok=True)
        _make_template(template_file)

    path_scss, path_css = config.scss_css
    if not _exists(path_scss):
        _makedirs(path_scss, exist_ok=True)
        logger.debug(f"makedirs({path_scss})")
    _sass.compile(dirname=(path_scss, path_css))
    logger.info(f"compiled scss {_glob(path_scss+'/*.scss')}")

    if not _debug_mode():
        return 0

    from .need import (make_writer as _make_writer, wakatigaki as _wakatigaki)
    writer = _make_writer(config.dir_index)

    session = make_session(config.url)

    path_list = []
    for cat, v in config.category.items():
        logger.debug(f'cat: {cat}, {v}')
        if v is not None and v.get('url', False):
            logger.debug("making url.md from yaml")
            path = _join(config.path_contents_dir, cat, '*.yaml')
            for file_y in _glob(path):
                _url_2_md(file_y, _join(config.path_contents_dir, cat))

        path = _join(config.path_contents_dir, cat, '*.md')
        for file in _glob(path):
            logger.debug(f"Deal w/ {file}")
            monster = _Monster(file)
            m = session.query(_Love).filter_by(path=monster.path).first()
            content = _wakatigaki(monster.contents)
            path_list.append(monster.path)

            writer.add_document(title=monster.title, path=monster.path,
                                content=(content + monster.tags_str))
            if m is None:
                # 新規の記事の場合はデータベースへ追加する。
                logger.debug(f'Add a new {monster} to database')
                session.add(monster.love)
                session.commit()

                logger.debug(f"add doc to dir_index: {monster.path}")

                continue

            if monster.hash != m.hash:
                # 登録済みの記事においてヘッダーが更新されている場合。
                log_txt = 'It looks like the header has changed.'
                logger.debug(log_txt)

                tags_new = set([tag.tag for tag in monster.love.tags])
                tags_old = set([tag.tag for tag in m.tags])

                # delete
                tags_diff = tags_old - tags_new
                cond_1 = _Blue.love_path == monster.path
                cond_2 = _Blue.tag.in_(tags_diff)
                cond = _and_(cond_1, cond_2)
                tags_delete = session.query(_Blue).filter(cond).all()
                for tag in tags_delete:
                    session.delete(tag)
                    session.commit()
                logger.debug(f"delet tag list: {tags_diff}")

                # add
                for tag in (tags_diff := tags_new - tags_old):
                    session.add(_Blue(monster.path, tag))
                    session.commit()
                logger.debug(f"add tag list: {tags_diff}")

            m.set_all(*monster.love.to_tuple())
            session.commit()

    for v in session.query(_Love).filter(_Love.path.notin_(path_list)).all():
        session.delete(v)
        session.commit()

    writer.commit()
    session.close()
