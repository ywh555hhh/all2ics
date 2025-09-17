# src/all2ics/schema.py

from pydantic import BaseModel, Field
from typing import List, Optional

class RRule(BaseModel):
    """
    定义 iCalendar 的重复规则 (RRULE)。
    这是实现"每周重复"等周期性事件的核心。
    """
    freq: str = Field("WEEKLY", description="重复频率，对于课程表，通常是 'WEEKLY' (每周)")
    until: Optional[str] = Field(None, description="重复结束的日期 (格式: YYYY-MM-DD)")
    count: Optional[int] = Field(None, description="重复的总次数")

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

# 定义最终输入的 JSON 结构为一个 CourseEvent 对象的列表
CourseSchedule = List[CourseEvent]