# src/all2ics/schema.py

from pydantic import BaseModel, Field
from typing import List, Optional

class RRule(BaseModel):
    """
    定义 iCalendar 的重复规则 (RRULE)。
    这是实现"每周重复"等周期性事件的核心。
    支持完整的 RFC 5545 RRULE 规范中的常用属性。
    """
    freq: str = Field("WEEKLY", description="重复频率，常见值: 'YEARLY', 'MONTHLY', 'WEEKLY', 'DAILY'")
    interval: Optional[int] = Field(None, description="重复间隔，例如 interval=2 表示每隔一周重复")
    until: Optional[str] = Field(None, description="重复结束的日期 (格式: YYYY-MM-DD)")
    count: Optional[int] = Field(None, description="重复的总次数")
    byday: Optional[str] = Field(None, description="按星期重复，例如 'MO,WE,FR' 表示周一、三、五")
    bymonth: Optional[str] = Field(None, description="按月份重复，例如 '1,3,5' 表示1月、3月、5月")
    bysetpos: Optional[str] = Field(None, description="按位置重复，例如 '1,-1' 表示第一个和最后一个")
    wkst: Optional[str] = Field(None, description="一周的开始日，例如 'MO' 表示周一开始")

class CourseEvent(BaseModel):
    """
    定义单条课程事件的数据结构。
    每个字段都有详细的中文描述，方便用户理解 JSON 格式。
    """
    name: str = Field(..., description="课程名称")
    location: Optional[str] = Field(None, description="上课地点")
    description: Optional[str] = Field(None, description="课程的附加描述，例如教师姓名、周次范围等")
    begin: str = Field(..., description="首次上课的开始日期和时间 (格式: 'YYYY-MM-DD HH:MM:SS')")
    end: str = Field(..., description="首次上课的结束日期和时间 (格式: 'YYYY-MM-DD HH:MM:SS')")
    rrule: Optional[RRule] = Field(None, description="课程的重复规则")
    timezone: Optional[str] = Field("Asia/Shanghai", description="时区设置，默认为上海时间 (Asia/Shanghai)")

# 定义最终输入的 JSON 结构为一个 CourseEvent 对象的列表
CourseSchedule = List[CourseEvent]