from os.path import join as _join
from urllib import parse as _parse

from markupsafe import Markup as _Markup

from .config import env as _env, path_templates_jinja2 as _path_templates


def make_template(template_file):
    with open(_join(_path_templates, 'template.j2')) as f:
        data = f.read()

    with open(template_file, mode='w') as f:
        f.write(data)


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
            s = c.get('weight', "").replace(',', ';')
            if len(s) != 0:
                font_weight = f":wght@{s}"
        font_name = font_name.replace(" ", "+")
        font_list.append((font_name, font_weight))

    tmpl = _env.get_template('fonts.j2')
    d = {'icon': icon, 'font_list': font_list}

    return _Markup(tmpl.render(d))


def make_icons(static):
    tmpl = _env.get_template('icon.j2')
    d = {"static": static}
    return _Markup(tmpl.render(d))


def making_for_ogp(config, category, **kwargs):
    cat_list = list(config.category.keys())

    site_name = config.site_name
    monster = kwargs.get('monster', None)

    if monster is not None:
        title = f'{monster.title} | {site_name}'
    else:
        title = site_name

    ogp = config.ogp
    image_url = ogp.images
    url = config.base_url

    if category in cat_list:
        ogp_type = 'article'
        if monster is not None:
            doc = monster.doc
            path = monster.path
            url = _parse.urljoin(url, path)
        else:
            doc = 'Where is monster ?'
    else:
        ogp_type = 'website'
        description = ogp.descriptions
        err = ogp.desc_error
        doc = description.get(category, err)

        if (category == 'tag') and (doc is not None):
            tag = kwargs.get('tag', 'no tag info')
            doc = doc.replace('$tag$', tag)
            url = _join(url, 'tag', tag)

        elif (category == 'search') and (doc is not None):
            word = kwargs.get('word', 'no word info')
            doc = doc.replace('$word$', word)
            url = _join(url, 'search')+f'?word={word}'

        elif category == 'home':
            url = url

        elif category == 'not_found':
            url = f'{url}/404/'

        else:
            url = f'{url}/{category}/'

    tmpl = _env.get_template('opg.j2')
    d = {'site_name': site_name, 'title': title, 'category': category,
         'description': doc, 'ogp_type': ogp_type,
         'url': url, 'image_url': image_url}
    hey = tmpl.render(d)

    return _Markup(hey)
