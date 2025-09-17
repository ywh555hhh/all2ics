# src/all2ics/converter.py

from ics import Calendar, Event
from ics.grammar.parse import ContentLine
from .schema import CourseSchedule
import pytz
from datetime import datetime

def parse_datetime_with_timezone(datetime_str: str, timezone_str: str = "Asia/Shanghai") -> datetime:
    """
    解析日期时间字符串并添加时区信息。
    
    Args:
        datetime_str: 格式为 'YYYY-MM-DD HH:MM:SS' 的日期时间字符串
        timezone_str: 时区字符串，默认为上海时间
        
    Returns:
        带时区信息的 datetime 对象
    """
    try:
        # 解析时间字符串
        dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        # 获取时区对象
        tz = pytz.timezone(timezone_str)
        # 本地化时间
        return tz.localize(dt)
    except Exception as e:
        # 如果时区解析失败，回退到上海时间
        tz = pytz.timezone("Asia/Shanghai")
        dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        return tz.localize(dt)


def create_ics_from_schedule(schedule: CourseSchedule, default_timezone: str = "Asia/Shanghai") -> str:
    """
    根据解析和验证后的课程表数据，创建一个 iCalendar 格式的字符串。

    Args:
        schedule: 一个包含多条课程事件的列表，且已经通过 Pydantic 模型验证。
        default_timezone: 默认时区，当课程没有指定时区时使用

    Returns:
        一个符合 RFC 5545 标准的 iCalendar 格式字符串。
    """
    c = Calendar()
    c.extra.append(ContentLine('PRODID', value='-//all2ics//Course Schedule//CN'))
    
    for course in schedule:
        e = Event()
        e.name = course.name
        
        # 使用课程指定的时区，如果没有则使用默认时区
        course_tz = getattr(course, 'timezone', default_timezone) or default_timezone
        
        # 解析开始和结束时间，添加时区信息
        e.begin = parse_datetime_with_timezone(course.begin, course_tz)
        e.end = parse_datetime_with_timezone(course.end, course_tz)
        
        e.location = course.location
        e.description = course.description

        # 处理重复规则 (rrule)
        if course.rrule:
            # 将 Pydantic 模型转换为 ics.py 能理解的 rrule 字符串
            rrule_parts = [f"FREQ={course.rrule.freq}"]
            
            # 添加 INTERVAL 支持
            if course.rrule.interval and course.rrule.interval > 1:
                rrule_parts.append(f"INTERVAL={course.rrule.interval}")
            
            # 处理 UNTIL 日期
            if course.rrule.until:
                # 处理 UNTIL 日期，需要转换为正确的时区
                until_dt = datetime.strptime(course.rrule.until, '%Y-%m-%d')
                tz = pytz.timezone(course_tz)
                # 将结束日期设置为当天的最后一秒，并使用正确的时区
                until_dt = until_dt.replace(hour=23, minute=59, second=59)
                until_dt_tz = tz.localize(until_dt)
                # 转换为UTC用于RRULE UNTIL
                until_utc = until_dt_tz.astimezone(pytz.UTC)
                until_date = until_utc.strftime('%Y%m%dT%H%M%SZ')
                rrule_parts.append(f"UNTIL={until_date}")
            
            # 添加 COUNT 支持
            if course.rrule.count:
                rrule_parts.append(f"COUNT={course.rrule.count}")
            
            # 添加 BYDAY 支持
            if course.rrule.byday:
                rrule_parts.append(f"BYDAY={course.rrule.byday}")
            
            # 添加 BYMONTH 支持
            if course.rrule.bymonth:
                rrule_parts.append(f"BYMONTH={course.rrule.bymonth}")
            
            # 添加 BYSETPOS 支持
            if course.rrule.bysetpos:
                rrule_parts.append(f"BYSETPOS={course.rrule.bysetpos}")
            
            # 添加 WKST 支持
            if course.rrule.wkst:
                rrule_parts.append(f"WKST={course.rrule.wkst}")
            
            # 使用 ContentLine 创建 RRULE
            rrule_line = ContentLine('RRULE', value=";".join(rrule_parts))
            e.extra.append(rrule_line)

        c.events.add(e)
    
    # 返回序列化后的日历字符串
    return c.serialize()