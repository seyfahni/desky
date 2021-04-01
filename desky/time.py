import math
import re
import time as sys_time
import wx

duration_pattern = re.compile(r'(\d+)\s*([a-zA-Z]*)')


def parse_time_duration(time_duration_string: str):
    """
    Parse strings depicting a duration to a duration in milli seconds.

    The format follows the pattern "5 minutes 3 seconds". Units can be shortened until they become ambiguous, in that
    case the shortest unit will be used. No unit equals milliseconds, the unit "m" means minutes.

     Possible units:
    - milliseconds / ms
    - seconds
    - minutes (m will resolve as minutes instead of milliseconds)
    - hours
    - days
    - weeks
    - months
    - years
    - century / centuries

    :param time_duration_string: string to parse
    :return: duration in milliseconds
    """
    time = 0
    for time_duration_match in duration_pattern.finditer(time_duration_string):
        time_in_units = int(time_duration_match.group(1))
        time_unit = time_duration_match.group(2).lower()
        time += time_to_milli_seconds(time_in_units, time_unit)
    return time


def time_to_milli_seconds(time: int, unit: str) -> int:
    if unit and not unit == 'm' and ('milliseconds'.startswith(unit) or 'ms' == unit):
        return time
    time *= 1000
    if 'seconds'.startswith(unit):
        return time
    time *= 60
    if 'minutes'.startswith(unit):
        return time
    time *= 60
    if 'hours'.startswith(unit):
        return time
    time *= 24
    if 'days'.startswith(unit):
        return time
    if 'weeks'.startswith(unit):
        return time*7
    if 'months'.startswith(unit):
        return time*30
    time *= 365
    if 'years'.startswith(unit):
        return time
    time *= 100
    if 'century'.startswith(unit) or 'centuries'.startswith(unit):
        return time
    raise InvalidUnitException('Invalid unit: ' + unit)


def parse_time_instant(time_instant_string: str) -> wx.DateTime:
    time = wx.DateTime()
    if time.ParseTime(time_instant_string) == -1:
        raise InvalidInstantException('Invalid instant: ' + time_instant_string)
    return time


def set_to_future(date_time: wx.DateTime, now: wx.DateTime = None) -> wx.DateTime:
    """
    Set date so that the time is nearest to now but in the future.

    :param date_time: DateTime to modify
    :param now: Override now to compare to
    :return: same modified DateTime
    """
    if now is None:
        now = wx.DateTime.Now()
    diff = now.DiffAsDateSpan(date_time)
    date_time.Add(diff)
    now.IsLaterThan(date_time) and date_time.Add(wx.DateSpan.Day())
    return date_time


def milli_seconds_until(date_time: wx.DateTime, now: wx.DateTime = None):
    if now is None:
        now = wx.DateTime.UNow()
    time_span = date_time.Subtract(now)
    return time_span.GetMilliseconds()


def to_milli_seconds(now):
    if isinstance(now, wx.DateTime):
        return now.GetValue()
    if isinstance(now, int):
        return now
    raise TimeException('cannot convert ' + type(now) + ' to milli seconds')


def to_date_time(now) -> wx.DateTime:
    if isinstance(now, wx.DateTime):
        return now
    date_time = wx.DateTime()
    if isinstance(now, int):
        date_time.SetTimeT(now // 1000)
        date_time.SetMillisecond(now % 1000)
        return date_time
    raise TimeException('cannot convert ' + type(now) + ' to date time')


def now_millis():
    return math.floor(sys_time.time() * 1000)


class TimeException(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InvalidInstantException(TimeException):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InvalidUnitException(TimeException):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
