from logging import getLogger as _getLogger
from pathlib import Path as _Path


import yaml as _yaml


_logger = _getLogger(__name__)


class Config(object):
    def __init__(self, p_obj_d_parent):
        self.y = self._get_config(p_obj_d_parent / "config.yaml")
        self.p_obj_d_parent = p_obj_d_parent

    @property
    def p_obj_d_template(self):
        return self.p_obj_d_parent / self.y.get('templates', 'templates')

    @property
    def p_obj_main_template(self):
        return _Path(self.y.get('main_template', 'template.html'))

    @property
    def p_obj_template(self):
        return self.p_obj_d_template / self.p_obj_main_template

    @property
    def security_headers(self):
        return self.y.get('security_headers', {})

    @property
    def p_obj_cache(self):
        return self.p_obj_d_parent / self.y.get('cache', '.cache')

    @property
    def url(self):
        db = self.y.get('db', {})
        return db.get('db_url', 'sqlite:///test.db')

    @property
    def contents(self):
        return self.y.get('contents_directory', 'contents')

    @property
    def p_obj_d_contents(self):
        return self.p_obj_d_parent / self.contents

    @property
    def category(self):
        return self.y.get('category', dict())

    @property
    def ogp(self):
        return self.y.get('ogp', dict())

    @property
    def site_name(self):
        return self.y.get('site_name', "not set site_name")

    @property
    def base_url(self):
        return self.y.get('base_url', "/")

    @property
    def p_obj_static(self):
        return self.y.get('static', 'static')

    @property
    def p_obj_d_static(self):
        return self.p_obj_d_parent / self.p_obj_static

    @property
    def p_obj_d_scss(self):
        return self.p_obj_d_static / self.y.get('scss_directory', 'scss')

    @property
    def p_obj_d_css(self):
        return self.p_obj_d_static / self.y.get('css_directory', 'css')

    @property
    def p_obj_d_index(self):
        return self.p_obj_d_parent / self.y.get('index_directory', 'index')

    @property
    def list_ext(self):
        list_ext = self.y.get('static_ext_ok', ['jpg', 'png', 'jpeg', 'css'])
        if isinstance(list_ext, list):
            return list_ext

        elif isinstance(list_ext, str):
            return [list_ext]

        else:
            return []

    @property
    def favicon(self):
        return "favicon.ico"

    @property
    def font(self):
        return self.y.get("font", {})

    def _get_config(self, p_obj_config):
        try:
            with p_obj_config.open() as f:
                y = _yaml.safe_load(f)

        except Exception as e:
            _logger.warning(f"Can't open {p_obj_config}. \n{e}")
            y = {}
        return y
