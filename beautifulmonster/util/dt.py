from datetime import datetime as _datetime, date as _date, time as _time
import re as _re


def get_date(string):
    p_y = r'(?P<year>[12]\d{3})'
    p_m = r'(?P<month>(0?[1-9]|1[0-2]))'
    p_d = r'(?P<day>(0?[1-9]|1[0-9]|2[0-9]|3[01]))'
    pattern = rf'\D*{p_y}\D+{p_m}\D+{p_d}(\D|$)'
    prog = _re.compile(pattern)

    result = prog.match(string)
    if result:
        return _date(*(int(result.group(v)) for v in ['year', 'month', 'day']))

    else:
        return None


def get_time(string):
    p_h = r'(?P<hour>0?[0-9]|1[0-9]|2[0-3])'
    p_m = r'(?P<minute>[0-5][0-9])'
    pattern = rf'.*\s{p_h}\D+{p_m}(\D+|$)'
    prog2 = _re.compile(pattern)

    result = prog2.match(string)
    if result:
        hour = result.group('hour')
        minute = result.group('minute')

        p_s = r'(?P<second>[0-5][0-9])'
        pattern = rf".*\s\d+\D+\d+\D+{p_s}$"
        prog3 = _re.compile(pattern)
        result2 = prog3.match(string)
        if result2 is not None:
            second = result2.group('second')
        else:
            second = 0

        return _time(hour=int(hour), minute=int(minute), second=int(second))
    else:
        return None


def str_2_datetime(string):

    if isinstance(string, _datetime):
        return string

    elif isinstance(string, _date):
        return _datetime.combine(string, _time())

    elif string is None:
        return None

    elif isinstance(string, str):
        date = get_date(string)
        if date is not None:
            str_datetime = date.strftime("%Y-%m-%d")

            time = get_time(string)
            if time is not None:
                str_datetime += f'+{time.strftime("%H:%M:%S")}'
            else:
                str_datetime += '+00:00:00'

            tdatetime = _datetime.strptime(str_datetime, '%Y-%m-%d+%H:%M:%S')
            return tdatetime

    return None
