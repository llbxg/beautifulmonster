from distutils.util import strtobool as _strtobool
from functools import partial as _partial
import json as _json
from os import environ as _environ
from pathlib import Path as _Path


from flask import (Flask as _Flask, abort as _abort, jsonify as _jsonify,
                   render_template as _render_template,
                   send_from_directory as _send_from_directory,
                   request as _request)
from sqlalchemy import desc as _desc


from .building3 import building2, make_session, compile_scss
from .config import Config
from .monster import create_monster, Monster
from .ohh import Love, Blue, lag, lead
from .need import searching
from .puzzle import make_ogp, make_template, make_icons, make_fonts


__all__ = ['Monster']

_default_p_obj_config = _Path().cwd()

DEBUG = bool(_strtobool(_environ.get('BM_DEBUG', 'False')))
_environ['FLASK_DEBUG'] = 'True' if DEBUG else 'False'


def loves_list_2_json(loves_list):
    loves = _json.dumps(
        {love.path: love.to_dict() for love in loves_list if love is not None})
    r = _jsonify(loves)
    return r


def make_app(p_obj_d_parent=_default_p_obj_config,
             s_icons=True, s_fonts=False):
    config = Config(p_obj_d_parent)

    session = make_session(config.url)
    building2(session, p_obj_d_parent, config)
    session.close()
    compile_scss(config.p_obj_d_scss, config.p_obj_d_css, config.p_obj_cache)

    if DEBUG:
        from .need import build_for_search
        build_for_search(p_obj_d_parent, config.p_obj_d_index)

    make_template(config.p_obj_template)
    icons = make_icons(config.p_obj_static) if s_icons else None

    fonts = make_fonts(config.font) if s_fonts else None

    app = _Flask(__name__, static_folder=None,
                 template_folder=config.p_obj_d_template)

    site_name = config.site_name
    base_url = config.base_url

    def wrapper_render_template(category, **kwargs):
        ogp = make_ogp(category, config.category, site_name, base_url,
                       config.ogp, **kwargs)
        c = _render_template(str(config.p_obj_main_template), ogp=ogp,
                             icons=icons, fonts=fonts, category=category,
                             debug=DEBUG, **kwargs)
        return c

    security_headers = config.security_headers

    @app.after_request
    def after_request(response):
        response.headers.update(security_headers)
        return response

    @app.route('/')
    def home():
        r = wrapper_render_template('home')
        return r

    for category, value in config.category.items():
        def temp_fucn(_id, cat, v):
            path = config.p_obj_d_contents / cat / f'{_id}.md'

            kwargs = v if v is not None else {}

            monster = create_monster(path)

            r = wrapper_render_template(cat, monster=monster, **kwargs)
            return r

        view_func = _partial(temp_fucn, cat=category, v=value)
        app.add_url_rule(f'/{category}/<_id>/', endpoint=category,
                         view_func=view_func)

    @app.route('/search')
    def need():
        req = _request.args
        word = req.get('word', None)
        return wrapper_render_template('search', word=word)

    @app.route('/tag/<tag>/')
    def gettag(tag):
        r = wrapper_render_template('tag', tag=tag)
        return r

    @app.route('/static/<path:filename>')
    def static(filename):
        p_obj_d_static = config.p_obj_d_static
        p_obj = p_obj_d_static / filename
        if not p_obj.is_file() or (p_obj.suffix[1:] not in config.list_ext):
            return _abort(404)

        return _send_from_directory(p_obj_d_static, filename)

    @app.errorhandler(404)
    def page_not_found(error):
        return wrapper_render_template(
            'not_found', contents=f"{error}"), 404

    app.register_error_handler(404, page_not_found)

    @app.route('/favicon.ico')
    def favicon():
        '''
        The old de-facto standard is to serve this file,
        with this name, at the website root.
        '''
        mimetype = 'image/vnd.microsoft.icon'
        return _send_from_directory(config.p_obj_d_static,
                                    config.favicon,
                                    mimetype=mimetype)

    @app.route('/all/')
    def all():
        session = make_session(config.url)
        r = wrapper_render_template(
            'all',
            loves=session.query(Love).order_by(_desc(Love.created)).all())
        session.close()
        return r

    @app.route('/about/')
    def about():
        return wrapper_render_template('about')

    @app.route('/api/leadlag/<path:name>/')
    def api_lead_lag(name):
        name = name+'.md'
        session = make_session(config.url)

        love_lag = lag(session, name)
        _lag = {} if love_lag is None else love_lag.to_dict()

        love_lead = lead(session, name)
        _lead = {} if love_lead is None else love_lead.to_dict()

        loves = _json.dumps({'lag': _lag, 'lead': _lead})

        session.close()
        return _jsonify(loves)

    @app.route('/api/loves/<int:num>')
    def api_love_num(num):
        session = make_session(config.url)
        loves = session.query(Love).order_by(_desc(Love.created)).limit(num)
        r = loves_list_2_json(loves)
        session.close()
        return r

    @app.route('/api/tag/<tag>')
    def apt_tags(tag):
        session = make_session(config.url)
        tags = session.query(Blue).filter(Blue.tag == tag).all()
        path_list = set([tag.love_path for tag in tags])
        loves = session.query(Love).order_by(_desc(Love.created)).\
            filter(Love.path.in_(path_list)).all()
        r = loves_list_2_json(loves)
        session.close()
        return r

    @app.route('/api/search')
    def api_search():
        if not config.p_obj_d_index.exists():
            _abort(404)
        req = _request.args

        word = req.get('word', None)
        if word is None:
            return _jsonify({})

        session = make_session(config.url)
        results = searching(word, config.p_obj_d_index)
        loves = session.query(Love).filter(Love.path.in_(results))
        r = loves_list_2_json(loves.all())
        session.close()
        return r

    return app
