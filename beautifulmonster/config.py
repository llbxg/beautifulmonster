from dataclasses import dataclass as _dataclass, field as _field
from os import getcwd as _getcwd
from os.path import join as _join, dirname as _dirname, exists as _exists
import sys as _sys

from jinja2 import (Environment as _Environment,
                    FileSystemLoader as _FileSystemLoader)
import yaml as _yaml


PATH_SETTINGS = _join(_dirname(__file__), '_settings.yaml')

with open(PATH_SETTINGS) as f:
    YAML_SETTINGS = _yaml.safe_load(f)
SETTINGS_4_JINJA2 = YAML_SETTINGS['jinja2']

path_templates_jinja2 = _join(
    _dirname(__file__), SETTINGS_4_JINJA2['DIR_TEMPLATES'])
env = _Environment(loader=_FileSystemLoader(path_templates_jinja2))

CONFIG = YAML_SETTINGS['CONFIG']
CONFIG_OGP = YAML_SETTINGS['OGP']


@_dataclass
class OGP(object):
    images: str = ''
    descriptions: dict = _field(default_factory=dict)

    @property
    def desc_error(self):
        desc_error = CONFIG_OGP['DESCRIPTION_ERROR']
        desc_error_default = CONFIG_OGP['DESCRIPTION_ERROR_DEFAULT']
        return self.descriptions.get(desc_error, desc_error_default)


class Config(object):
    def __init__(self):
        self.path_directory = _getcwd()

        self.y = self._get_config()

        if not self._check_category():
            print('nooooo')
            _sys.exit(0)

        self.ogp = self._make_ogp()

    def _get_config(self):
        try:
            with open(_join(self.path_directory, CONFIG['PATH_CONFIG'])) as f:
                y = _yaml.safe_load(f)

        except Exception:
            y = {}
        return y

    def _make_ogp(self):
        ogp = self.y.get('ogp', {})
        image = ogp.get(CONFIG_OGP['IMAGE'], '')
        description = ogp.get(CONFIG_OGP['DESCRIPTION'], {})
        return OGP(image, description)

    @property
    def template_folder(self):
        path = CONFIG['DIR_TEMPLATE']
        template_dir = self.y.get(path, CONFIG['DIR_TEMPLATE_DEFAULT'])
        return self._join_w_cwd(template_dir)

    @property
    def path_contents(self):
        return self.y.get(CONFIG['PATH_DIR'], CONFIG['PATH_DIR_DEFAULT'])

    @property
    def path_contents_dir(self):
        return _join(self.path_directory, self.path_contents)

    @property
    def static(self):
        return self.y.get(CONFIG['PATH_STATIC'], CONFIG['PATH_STATIC_DEFAULT'])

    @property
    def static_dir(self):
        return _join(self.path_directory, self.static)

    @property
    def security_headers(self):
        return self.y.get(CONFIG['SECURITY_HEADERS'], {})

    @property
    def category(self):
        return self.y.get(CONFIG['CATEGORY'], {})

    @property
    def fonts(self):
        return self.y.get(CONFIG['FONTS'], {})

    @property
    def path_favicon(self):
        return _join('favicon.ico')

    @property
    def url(self):
        db = self.y.get(CONFIG['DB'], None)
        url = CONFIG['DB_URL_DEFAULT']

        if db is not None:
            url = db.get(CONFIG['DB_URL']) or url

        return url

    @property
    def site_name(self):
        return self.y.get(CONFIG['SITE_NAME'], CONFIG['SITE_NAME_DEFAULT'])

    @property
    def base_url(self):
        return self.y.get(CONFIG['BASE_URL'], CONFIG['BASE_URL_DEFAULT'])

    @property
    def dir_index(self):
        return self.y.get(CONFIG['DIR_INDEX'], CONFIG['DIR_INDEX_DEFAULT'])

    @property
    def scss_css(self):
        path_css = _join(self.static, self.y.get(CONFIG['PATH_CSS'], ''))
        path_scss = _join(self.static, self.y.get(CONFIG['PATH_SCSS'], ''))
        return (path_scss, path_css)

    def _join_w_cwd(self, path):
        return _join(self.path_directory, path)

    def _check_category(self):
        b = all([_exists(_join(self.path_contents, c)) for c in self.category])
        return b
