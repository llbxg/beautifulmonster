from datetime import datetime as _datetime
from distutils.util import strtobool as _strtobool
from hashlib import md5 as _md5
from os.path import splitext as _splitext
from os import environ as _environ
import re as _re


def read_txt(path):
    """
    markdown形式のファイルだった場合開封して返す。

    課題
      - logによるエラーチェック
      - magicとかで形式チェック
      - pathlibでの書き換え
    """

    _, ext = _splitext(path)
    if ext != '.md':
        return None

    try:
        with open(path) as f:
            txt = f.read()
    except Exception:
        txt = None

    return txt


def separate_yamlblock_contents(txt):
    """
    頭の部分にyaml形式で記述された設定項目があるかどうかの確認。
    """
    if txt is None:
        return None, ""

    yamlblock = None
    contents = txt

    pattern = r'^---(?P<yamlblock>.*?)---[ \t]*\r?\n(?P<contents>.*)'
    if txt.startswith("---"):
        m = _re.search(pattern, txt, _re.DOTALL)
        if m is not None:
            contents = m.group('contents')
            yamlblock = m.group('yamlblock')

    return yamlblock, contents


def str_2_datetime(string):
    """
    strをdatetimeへ変換する。
    課題
      - 変換次のエラー処理
    """
    if string is None:
        return None

    elif isinstance(string, _datetime):
        return string

    elif isinstance(string, str):
        p_y = r'(?P<year>[12]\d{3})\D+'
        p_m = r'(?P<month>(0?[1-9]|1[0-2]))\D+'
        p_d = r'(?P<day>(0?[1-9]|1[0-9]|2[0-9]|3[01]))\D*'
        pattern = rf'\D*{p_y}{p_m}{p_d}$'
        prog = _re.compile(pattern)

        result = prog.match(string)
        if result:
            year = result.group('year')
            month = result.group('month')
            date = result.group('day')
            tdatetime = _datetime.strptime(
                f'{year}-{month:0>2}-{date:0>2} 00:00:00', '%Y-%m-%d %H:%M:%S')
            return tdatetime

    return None


def make_hash(yamlblock):
    """
    contentsからハッシュ値を計算する。
    課題
      - contentsの型について確認
    """
    hash = _md5()
    hash.update(yamlblock.encode())
    return f'h{hash.hexdigest()}'


def make_path(path):
    """
    カレントディレクトリpathからcategory以下のパスを取得する。
    課題
    - pathlibでの処理の検討
    """
    path = path[:-1] if path[-1] == '/' else path

    category, _id = path.split('/')[-2:]
    if _id.endswith('.md'):
        _id = _id.split('.')[0]
    return f'/{category}/{_id}/'


def debug_mode():
    debug = _strtobool(_environ.get('BM_DEBUG', 'False'))
    return bool(debug)
