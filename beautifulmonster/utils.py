from datetime import datetime as _datetime
from distutils.util import strtobool as _strtobool
from hashlib import md5 as _md5
from os.path import (splitext as _splitext, basename as _basename,
                     getctime as _getctime)
from os import environ as _environ, stat as _stat
from pathlib import Path as _Path
import platform as _platform
import re as _re

from bs4 import BeautifulSoup as _BeautifulSoup
import yaml as _yaml


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


def get_date(string):
    p_y = r'(?P<year>[12]\d{3})\D+'
    p_m = r'(?P<month>(0?[1-9]|1[0-2]))\D+'
    p_d = r'(?P<day>(0?[1-9]|1[0-9]|2[0-9]|3[01]))'
    pattern = rf'\D*{p_y}{p_m}{p_d}(\D|$)'
    prog = _re.compile(pattern)

    result = prog.match(string)
    if result:
        year = result.group('year')
        month = result.group('month')
        date = result.group('day')
        return (year, month, date)
    else:
        return None


def get_time(string):
    p_h = r'(?P<hour>0?[0-9]|1[0-9]|2[0-3])'
    p_m = r'(?P<minute>[0-5][0-9])'
    pattern = rf'.*\s{p_h}\D+{p_m}$'
    prog2 = _re.compile(pattern)

    result = prog2.match(string)
    if result:
        hour = result.group('hour')
        minute = result.group('minute')
        return (hour, minute)
    else:
        return None


def str_2_datetime(string):
    if string is None:
        return None

    elif isinstance(string, _datetime):
        return string

    elif isinstance(string, str):
        print(string)
        date = get_date(string)
        print(date)
        if date is not None:
            str_datetime = f'{date[0]}-{date[1]:0>2}-{date[2]:0>2}'

            time = get_time(string)
            print(time)
            if time is not None:
                str_datetime += f'+{time[0]:0>2}:{time[1]:0>2}:00'
            else:
                str_datetime += '+00:00:00'

            tdatetime = _datetime.strptime(str_datetime, '%Y-%m-%d+%H:%M:%S')
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


def get_update_date(path, format="{0:%Y-%m-%d %H:%M:%S}"):
    return format.format(get_rewrote(path))


def get_base_path(path):
    return _splitext(_basename(path))[0]


def read_yaml(path):
    with open(path, mode='r') as f:
        y = _yaml.safe_load(f)
    return y


def get_title_tag_string(response):
    title = None

    soup = _BeautifulSoup(response, 'html.parser')
    title_tag = soup.title
    if title_tag is not None:
        title = title_tag.string

    return title


def get_rewrote(path):
    p = _Path(path)
    rewrote = _datetime.fromtimestamp(p.stat().st_mtime)
    return rewrote


def get_created(path):

    file = _Path(path)
    if not file.exists():
        return None

    p = _platform.system()
    if p == 'Windows':
        created = _getctime(path)
    else:
        stat = _stat(path)
        try:
            created = stat.st_birthtime
        except AttributeError:
            created = None

    if created is not None:
        created = _datetime.fromtimestamp(created)

    return created
