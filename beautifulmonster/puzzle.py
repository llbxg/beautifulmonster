from pathlib import Path as _Path
from urllib import parse as _parse

from jinja2 import (Environment as _Environment,
                    FileSystemLoader as _FileSystemLoader)
from markupsafe import Markup as _Markup


p_obj_d_template_jinja2 = _Path(__file__).parent / "templates"

env = _Environment(loader=_FileSystemLoader(p_obj_d_template_jinja2))


def make_template(p_obj_template):
    if p_obj_template.exists():
        return None

    p_obj_t = p_obj_d_template_jinja2 / "template.j2"
    with p_obj_t.open() as f:
        data = f.read()

    with p_obj_template.open(mode='w') as f:
        f.write(data)


def make_icons(p_obj_static):
    tmpl = env.get_template('icon.j2')
    d = {"static": p_obj_static}
    return _Markup(tmpl.render(d))


def make_fonts(fonts):
    if 'Material Icons' in fonts.keys():
        fonts.pop('Material Icons')
        icon = True
    else:
        icon = False

    font_list = []
    for font_name, c in fonts.items():
        font_weight = ''
        if c is not None:
            s = c.get('weight', "")
            if isinstance(s, int):
                s = str(s)
            s = s.replace(',', ';')
            if len(s) != 0:
                font_weight = f":wght@{s}"
        font_name = font_name.replace(" ", "+")
        font_list.append((font_name, font_weight))

    tmpl = env.get_template('fonts.j2')
    d = {'icon': icon, 'font_list': font_list}

    return _Markup(tmpl.render(d))


def _return_dic(site_name, title, category, doc, ogp_type, url):
    return {'site_name': site_name, 'title': title, 'category': category,
            'description': doc, 'ogp_type': ogp_type, 'url': url}


def make_ogp(cat, category, site_name, base_url, ogp, *, monster=None,
             **kwargs):
    tmpl = env.get_template('opg.j2')

    cat_list = list(category.keys())
    title = site_name
    url = base_url

    if cat in cat_list:
        ogp_type = 'article'
        if monster is not None:
            title = f'{monster.title} | {site_name}'
            doc = monster.doc
            url = _parse.urljoin(base_url, monster.name)
        else:
            title = site_name
            doc = "Monster is not Nones"
            url = base_url
        d = _return_dic(site_name, title, cat, doc, ogp_type, url)
        return _Markup(tmpl.render(d))

    ogp_type = "website"
    ogp_descriptions = ogp.get("description", {})
    doc = ogp_descriptions.get(cat, "Not set description in ogp field")

    if cat == "tag":
        tag = kwargs.get('tag', 'no_tag_info')

        title = f'#{tag} | {site_name}'
        doc = doc.replace('$tag$', tag)
        url = _parse.urljoin(base_url, 'tag/{tag}')

    elif cat == 'search':
        word = kwargs.get('word', 'no_word_info')

        title = f'search {word} | {site_name}'
        doc = doc.replace('$word$', word)
        url = _parse.urljoin(base_url, 'search/?word={word}')

    d = {'site_name': site_name, 'title': title, 'category': category,
         'description': doc, 'ogp_type': ogp_type,
         'url': url, 'image_url': None}
    hey = tmpl.render(d)

    return _Markup(hey)
