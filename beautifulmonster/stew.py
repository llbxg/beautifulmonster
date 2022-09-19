from bs4 import BeautifulSoup as _BeautifulSoup

from markdown import markdown
from markdown.extensions.toc import TocExtension
from markupsafe import Markup


class Pot(object):
    """
    markdown形式をhtmlに変換する。
    課題
    - TOCはたぶんここで作るはず。
    """
    def __init__(self, contents):
        extensions = ['extra', 'attr_list', 'nl2br', 'tables',
                      TocExtension(baselevel=1, toc_depth=2)]
        html_string = markdown(contents, extensions=extensions)
        self.soup = _BeautifulSoup(html_string, "html.parser")

        self.katex = False
        self.m_code()

    def pour(self):
        return Markup(str(self.soup))

    def m_code(self):
        """
        googleのコードハイライトまたはKatexに対応するため。
        """
        pres = self.soup.find_all("pre")

        for pre in pres:
            try:
                lang = pre.find('code')['class'][0]
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

    def get_doc(self):
        doc = self.soup.find('p')
        return doc.text if doc is not None else 'Failed to extract doc ;;'
