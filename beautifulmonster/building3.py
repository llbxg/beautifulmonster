from collections import Counter
from pathlib import Path as _Path
import sass as _sass
from sqlalchemy import create_engine as _create_engine, and_ as _and_
from sqlalchemy.orm import (scoped_session as _scoped_session,
                            sessionmaker as _sessionmaker)


from .cach3 import (check_updated as _check_updated,
                    get_files_cache as _get_files_cache,
                    update_files_cache as _update_files_cache,
                    update_scss_cache as _update_scss_cache,
                    new_files as _new_files, get_scss_cache as _get_scss_cache)
from .monster import create_monster as _create_monster
from .ohh import Base as _Base, Love as _Love, Blue as _Blue


def add_love_and_tags(session, love, tags):
    session.add(love)
    for tag in tags:
        session.add(_Blue(love.path, tag))


def tag_update(session, love_path, tags):
    cond = _Blue.love_path == love_path
    blues_old = session.query(_Blue).filter(cond).all()
    blues_old = {blue.tag for blue in blues_old}
    blues_new = {tag for tag in tags}

    blues_update = blues_new - blues_old
    blues_delete = blues_old - blues_new

    for tag in blues_update:
        session.add(_Blue(love_path, tag))
    cond_2 = _Blue.tag.in_(blues_delete)
    for blue in session.query(_Blue).filter(_and_(cond, cond_2)).all():
        session.delete(blue)


def get_delete_loves(db_loves, p_obj_glob):
    loves = {love.path for love in db_loves}
    exist = {str(_Path(*p.relative_to(p.cwd()).parts[1:])) for p in p_obj_glob}

    return loves - exist


def building2(session, pobj_d_sample, config):
    p_obj_cache = config.p_obj_cache
    status = []

    cache_updated = _get_files_cache(p_obj_cache)

    for r in _new_files(cache_updated, pobj_d_sample):
        monster = _create_monster(r)
        love = monster.extract_love(config.p_obj_d_contents)
        if love is None:  # yamlによる情報がない場合。
            continue

        love_old = session.query(_Love).filter(_Love.path == love.path).first()

        # 新規登録
        if love_old is None:
            add_love_and_tags(session, love, monster.tags)
            session.commit()

            status.extend("1")

        # 更新
        else:
            love_old.update(love)
            tag_update(session, love.path, monster.tags)
            session.commit()

            status.extend("2")

    _update_files_cache(p_obj_cache)

    # 存在しないファイルをdbから削除
    loves_delete_set = get_delete_loves(session.query(_Love).all(),
                                        pobj_d_sample.glob("**/*.md"))
    for path in loves_delete_set:
        love = session.query(_Love).filter(_Love.path == path).first()
        session.delete(love)
    session.commit()

    status_dict = dict(Counter(status).most_common())
    status_dict["3"] = len(loves_delete_set)

    return status_dict


def _wrapper_create_engine(url):
    db_name = url.split(':')[0]
    connect_args = {"check_same_thread": False} if db_name == 'sqlite' else {}
    engine = _create_engine(url, connect_args=connect_args)
    return engine


def make_session(url):
    engine = _wrapper_create_engine(url)
    _Base.metadata.create_all(engine)
    session = _scoped_session(_sessionmaker(autocommit=False, bind=engine))
    return session


def scss_2_css(p_obj_scss, p_obj_d_css):
    css = _sass.compile(filename=str(p_obj_scss))
    file_name = p_obj_d_css / p_obj_scss.with_suffix('.css').name
    with file_name.open(mode="w") as f:
        f.write(css)


def compile_scss(p_obj_d_scss, p_obj_d_css, p_obj_cache):
    if not p_obj_d_scss.exists():
        return None

    p_obj_d_css.mkdir(parents=True, exist_ok=True)

    cache_updated = _get_scss_cache(p_obj_cache)

    p_obj_all = p_obj_d_scss.glob("**/*.scss")

    r = _check_updated(cache_updated, p_obj_all)
    for p_obj_scss in r:
        scss_2_css(p_obj_scss, p_obj_d_css)

    _update_scss_cache(p_obj_cache)
