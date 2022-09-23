from distutils.util import strtobool as _strtobool
import json
from logging import getLogger, NullHandler
from os.path import join as _join, isfile as _isfile
from os import environ as _environ

from flask import (Flask as _Flask, abort as _abort, jsonify as _jsonify,
                   render_template as _render_template,
                   send_from_directory as _send_from_directory,
                   request as _request)
from sqlalchemy import desc as _desc

from .building3 import building2 as building, make_session
from .config import Config
from .monster import Monster
from .need import searching
from .ohh import Love, Blue, lead, lag
from .puzzle import making_for_ogp, make_fonts, make_icons


logger = getLogger(__name__)
logger.addHandler(NullHandler())


debug = bool(_strtobool(_environ.get('BM_DEBUG', 'False')))
logger.debug(f"debug mode: {'on' if debug else 'off'}")

_environ['FLASK_DEBUG'] = 'True' if debug else 'False'


def make_app(category_boolean_items=None):

    config = Config()
    security_headers = config.security_headers
    fonts = make_fonts(config.fonts)
    icons = make_icons(config.static)

    building(config)

    app = _Flask(__name__, static_folder=None,
                 template_folder=config.template_folder)

    def wrapper_render_template(category, **kwargs):
        ogp = making_for_ogp(config, category, **kwargs)
        c = _render_template("template.html", category=category,
                             debug=app.debug, fonts=fonts,
                             ogp=ogp, icons=icons, **kwargs)
        return c

    @app.after_request
    def after_request(response):
        response.headers.update(security_headers)
        return response

    @app.route('/')
    def home():
        session = make_session(config.url)
        tags = set([tag.tag for tag in session.query(Blue).all()])
        r = wrapper_render_template(
            'home',
            loves=session.query(Love).order_by(_desc(Love.created)).limit(5),
            tags=tags)
        session.close()
        return r

    @app.route('/static/<path:filename>')
    def static(filename):
        directory_path = config.static_dir
        if _isfile(_join(directory_path, filename)):
            return _send_from_directory(directory_path, filename)
        else:
            print(filename, _isfile(_join(directory_path, filename)))
            return _abort(404)

    @app.route('/tag/<tag>/')
    def gettag(tag):
        session = make_session(config.url)
        tags = session.query(Blue).filter(Blue.tag == tag).all()
        path_list = set([tag.love_path for tag in tags])
        loves = session.query(Love).order_by(_desc(Love.created)).\
            filter(Love.path.in_(path_list)).all()
        r = wrapper_render_template('tag', tag=tag, loves=loves)
        session.close()
        return r

    for category, value in config.category.items():
        logger.debug(f'handle with {category_boolean_items} in config.yaml')

        def temp_fucn(_id):
            session = make_session(config.url)
            path = _join(config.path_contents_dir, category, f'{_id}.md')
            monster = Monster(path)
            kwargs = {}

            if value.get('laglead', False):
                lag_a = lag(session, monster.path)
                lead_a = lead(session, monster.path)
                kwargs.update({'lag': lag_a, 'lead': lead_a})

            if category_boolean_items is not None:
                for item in category_boolean_items:
                    if value.get(item, False):
                        kwargs.update({item: True})
            logger.debug(f'Use {kwargs=} in html')

            r = wrapper_render_template(category, monster=monster, **kwargs)
            session.close()
            return r

        app.add_url_rule(f'/{category}/<_id>/', view_func=temp_fucn)

    @app.route('/favicon.ico')
    def favicon():
        '''
        The old de-facto standard is to serve this file,
        with this name, at the website root.
        '''
        mimetype = 'image/vnd.microsoft.icon'
        return _send_from_directory(config.static_dir,
                                    config.path_favicon,
                                    mimetype=mimetype)

    @app.route('/about/')
    def about():
        return wrapper_render_template('about')

    @app.route('/search')
    def search():
        req = _request.args
        word = req.get('word', None)
        return wrapper_render_template('search', word=word)

    @app.errorhandler(404)
    def page_not_found(error):
        return wrapper_render_template(
            'not_found', contents=f"{error}"), 404

    app.register_error_handler(404, page_not_found)

    @app.route('/api/search')
    def api_search():
        session = make_session(config.url)
        req = _request.args
        word = req.get('word', None)
        logger.debug(word)
        if word is not None:
            results = searching(word, config.dir_index)
            logger.debug(f'{results}')
            loves = session.query(Love).filter(Love.path.in_(results))
            loves = loves.all()
            loves = {love.path: love.to_dict() for love in loves}
            logger.debug(f'{loves}')
            loves = json.dumps(loves)
            r = _jsonify(loves)
            session.close()
            return r

        r = _jsonify({})
        session.close()
        return r

    return app
