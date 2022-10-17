from logging import getLogger as _getLogger

from bs4 import BeautifulSoup as _BeautifulSoup, Tag as _Tag
from markdown import markdown as _markdown
from markdown.extensions.toc import TocExtension as _TocExtension
from markdown.extensions.wikilinks import (
    WikiLinkExtension as _WikiLink,
    WikiLinksInlineProcessor as _WikiLinksInlineProcessor)
from markupsafe import Markup as _Markup


logger = _getLogger(__name__)


class _Wiki(_WikiLink):
    def extendMarkdown(self, md):
        self.md = md
        WIKILINK_RE = r'\[\[([\w0-9_ -\/]+)\]\]'
        wikilinkPattern = _WikiLinksInlineProcessor(
            WIKILINK_RE, self.getConfigs())
        wikilinkPattern.md = md
        md.inlinePatterns.register(wikilinkPattern, 'wikilink', 75)


class Pot(object):
    """
    markdown形式をhtmlに変換する。
    課題
    - TOCはたぶんここで作るはず。
    """
    def __init__(self, contents, toc=2):
        extensions = ['extra', 'attr_list', 'nl2br', 'tables',
                      _TocExtension(baselevel=1, toc_depth=toc),
                      _Wiki(base_url='/', end_url='/')]
        html_string = _markdown(contents, extensions=extensions)
        self.soup = _BeautifulSoup(html_string, "html.parser")

        self.katex = False
        self.m_code()

        if toc:
            self.custom_toc()

    def pour(self):
        return _Markup(str(self.soup))

    def first_h1(self):
        title = self.soup.find('h1')
        if title is not None:
            title = title.text
        return title

    def custom_toc(self):
        logger.debug('use self.custom_toc')
        toc = self.soup.find("div", attrs={'class': "toc"})

        if toc is not None and isinstance(toc, _Tag):
            toc['id'] = 'toc'
            if (ul := toc.find('ul')) is not None and isinstance(ul, _Tag):
                ul.name = 'ol'

            ol = toc.ol
            if ol is not None:
                li_content = ol.find_all('ul')
                for li in li_content:
                    li.name = 'ol'

    def m_code(self):
        """
        googleのコードハイライトまたはKatexに対応するため。
        """
        pres = self.soup.find_all("pre")

        for pre in pres:
            codes = pre.find_all('code')
            try:
                lang = codes[0]['class'][0]
            except KeyError:
                lang = None

            if lang == 'language-math':
                self.katex = True
                string = pre.code.string
                pre.code.clear()
                pre.code.append(f'${string}$')
                pre.code.unwrap()
                pre.unwrap()

            if lang == 'language-python':
                lang = 'lang-py'
            elif lang == 'language-sh':
                lang = 'lang-sh'
            else:
                lang = ''

            pre['class'] = f'prettyprint {lang}'

            for code in codes:
                logger.debug(f'{type(code)}')
                code['class'] = 'in-pre'

    def get_doc(self):
        doc = self.soup.find('p')
        return doc.text if doc is not None else 'Failed to extract doc ;;'
