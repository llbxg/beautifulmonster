from distutils.util import strtobool as _strtobool
from os import environ as _environ


from whoosh.index import create_in as _create_in, open_dir as _open_dir
from whoosh.fields import Schema as _Schema, TEXT as _TEXT, ID as _ID
from whoosh.qparser import MultifieldParser as _MultifieldParser


from .monster import create_monster as _create_monster


def debug_mode():
    debug = _strtobool(_environ.get('BM_DEBUG', 'False'))
    return bool(debug)


if debug_mode():
    from janome.analyzer import Analyzer as _Analyzer
    from janome import charfilter as _charfilter
    from janome import tokenfilter as _tokenfilter

    def wakatigaki(content):
        char_filters = [_charfilter.UnicodeNormalizeCharFilter(),
                        _charfilter.RegexReplaceCharFilter('<.*?>', ''),
                        _charfilter.RegexReplaceCharFilter(r'\*\*', ''),
                        _charfilter.RegexReplaceCharFilter(r'`', '')
                        ]
        token_filters = [_tokenfilter.LowerCaseFilter(),
                         _tokenfilter.ExtractAttributeFilter('surface')]

        analyzer = _Analyzer(char_filters=char_filters,
                             token_filters=token_filters)

        results = analyzer.analyze(content)

        return " ".join(results)

    def make_writer(p_obj_d_index):
        schema = _Schema(title=_TEXT(stored=True),
                         path=_ID(stored=True), content=_TEXT)
        p_obj_d_index.mkdir(parents=True, exist_ok=True)
        writer = _create_in(str(p_obj_d_index), schema).writer()

        return writer

    def build_for_search(pobj_parent, p_obj_d_index):
        writer = make_writer(p_obj_d_index)
        for r in pobj_parent.glob("**/*.md"):
            monster = _create_monster(r)
            content = wakatigaki(monster.full_str)
            writer.add_document(title=monster.name, path=monster.name,
                                content=content)
        writer.commit()


def searching(word, dir_index):
    ix = _open_dir(dir_index)
    with ix.searcher() as searcher:
        query = _MultifieldParser(["title", "content"], ix.schema).parse(word)
        results = searcher.search(query)
        p = [r['path'] for r in results]
    return p
