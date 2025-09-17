# src/all2ics/converter.py

from ics import Calendar, Event
from ics.grammar.parse import ContentLine
from .schema import CourseSchedule

def create_ics_from_schedule(schedule: CourseSchedule) -> str:
    """
    根据解析和验证后的课程表数据，创建一个 iCalendar 格式的字符串。

    Args:
        schedule: 一个包含多条课程事件的列表，且已经通过 Pydantic 模型验证。

    Returns:
        一个符合 RFC 5545 标准的 iCalendar 格式字符串。
    """
    c = Calendar()
    for course in schedule:
        e = Event()
        e.name = course.name
        e.begin = course.begin
        e.end = course.end
        e.location = course.location
        e.description = course.description

        # 处理重复规则 (rrule)
        if course.rrule:
            # 将 Pydantic 模型转换为 ics.py 能理解的 rrule 字符串
            rrule_parts = [f"FREQ={course.rrule.freq}"]
            if course.rrule.until:
                # 注意：UNTIL 日期格式需要处理，移除'-'并添加UTC时间标识
                until_date = course.rrule.until.replace('-', '')
                rrule_parts.append(f"UNTIL={until_date}T235959Z")
            if course.rrule.count:
                rrule_parts.append(f"COUNT={course.rrule.count}")
            
            # 使用 ContentLine 创建 RRULE
            rrule_line = ContentLine('RRULE', value=";".join(rrule_parts))
            e.extra.append(rrule_line)

        c.events.add(e)
    
    # 返回序列化后的日历字符串
    return c.serialize()