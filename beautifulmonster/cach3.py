from os import makedirs as _makedirs
from os.path import join as _join, exists as _exists


from .config import path_templates_jinja2 as _path_templates


def mk_cache_dic(path):
    _makedirs(path, exist_ok=True)


def make_template_in_templates(template_file, template_folder):

    if _exists(template_file):
        return 0

    _makedirs(template_folder, exist_ok=True)

    with open(_join(_path_templates, 'template.j2')) as f:
        template = f.read()

    with open(template_file, mode='w') as f:
        f.write(template)
