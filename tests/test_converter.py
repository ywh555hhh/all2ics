# tests/test_converter.py

import json
from pathlib import Path
from all2ics.schema import CourseEvent
from all2ics.converter import create_ics_from_schedule

def test_create_ics_from_schedule():
    """
    测试核心转换函数是否能正确处理一个有效的课程表示例。
    """
    # 1. 准备测试数据
    # 使用相对路径定位到示例文件
    sample_path = Path(__file__).parent.parent / "examples/sample_input.json"
    with open(sample_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 2. 使用 Pydantic 解析数据
    schedule = [CourseEvent.model_validate(item) for item in data]

    # 3. 调用被测试的函数
    ics_content = create_ics_from_schedule(schedule)

    # 4. 断言 (Assert) 结果是否符合预期
    assert isinstance(ics_content, str)
    assert "BEGIN:VCALENDAR" in ics_content
    assert "END:VCALENDAR" in ics_content
    assert "SUMMARY:软件工程" in ics_content
    assert "LOCATION:机电楼E214(276)" in ics_content
    # 检查RRULE包含了正确的UNTIL格式（时区转换后的时间）
    assert "RRULE:FREQ=WEEKLY;UNTIL=" in ics_content
    assert "SUMMARY:计算机网络" in ics_content
    # 检查时区信息被正确应用（时间应该显示为+08:00或转换为UTC）
    # 由于时区转换，上海时间的10:00 (CST+8) 应该被转换为02:00 UTC
    assert "020000Z" in ics_content or "+08" in ics_content


def test_create_ics_from_schedule_with_timezone():
    """
    测试时区功能是否正常工作。
    """
    # 创建一个带有明确时区的测试数据
    test_course = CourseEvent(
        name="测试课程",
        location="测试教室",
        description="测试描述",
        begin="2025-01-15 10:00:00",
        end="2025-01-15 11:30:00",
        timezone="Asia/Shanghai"
    )
    
    schedule = [test_course]
    ics_content = create_ics_from_schedule(schedule)
    
    # 验证基本结构
    assert isinstance(ics_content, str)
    assert "BEGIN:VCALENDAR" in ics_content
    assert "END:VCALENDAR" in ics_content
    assert "SUMMARY:测试课程" in ics_content
    assert "LOCATION:测试教室" in ics_content
    
    # 验证时区转换：上海时间10:00应该转换为UTC的02:00
    assert "020000Z" in ics_content
    assert "033000Z" in ics_content  # 11:30上海时间应该是03:30 UTC


def test_create_ics_with_interval():
    """
    测试 RRULE 中的 interval 支持（例如每隔一周重复）。
    """
    from all2ics.schema import RRule
    
    test_course = CourseEvent(
        name="双周课程",
        location="教室A",
        description="每隔一周上课的课程",
        begin="2025-01-15 10:00:00", 
        end="2025-01-15 12:00:00",
        rrule=RRule(
            freq="WEEKLY",
            interval=2,
            until="2025-06-15"
        )
    )
    
    schedule = [test_course]
    ics_content = create_ics_from_schedule(schedule)
    
    # 验证 INTERVAL=2 被正确添加到 RRULE 中
    assert "RRULE:FREQ=WEEKLY;INTERVAL=2;UNTIL=" in ics_content
    assert "SUMMARY:双周课程" in ics_content


def test_create_ics_with_comprehensive_rrule():
    """
    测试完整的 RRULE 功能，包括 byday, bymonth 等高级特性。
    """
    from all2ics.schema import RRule
    
    # 测试每月第一个周一的课程
    monthly_course = CourseEvent(
        name="月度会议",
        location="会议室B",
        description="每月第一个周一",
        begin="2025-01-06 14:00:00",
        end="2025-01-06 16:00:00", 
        rrule=RRule(
            freq="MONTHLY",
            byday="MO",
            bysetpos="1",
            count=12
        )
    )
    
    # 测试工作日课程
    weekday_course = CourseEvent(
        name="工作日课程", 
        location="教室C",
        description="周一到周五",
        begin="2025-01-06 09:00:00",
        end="2025-01-06 10:00:00",
        rrule=RRule(
            freq="WEEKLY",
            byday="MO,TU,WE,TH,FR",
            until="2025-06-30"
        )
    )
    
    schedule = [monthly_course, weekday_course]
    ics_content = create_ics_from_schedule(schedule)
    
    # 验证月度课程的 RRULE
    assert "RRULE:FREQ=MONTHLY;COUNT=12;BYDAY=MO;BYSETPOS=1" in ics_content
    assert "SUMMARY:月度会议" in ics_content
    
    # 验证工作日课程的 RRULE
    assert "RRULE:FREQ=WEEKLY;UNTIL=" in ics_content
    assert "BYDAY=MO,TU,WE,TH,FR" in ics_content
    assert "SUMMARY:工作日课程" in ics_content


def test_rrule_with_default_interval():
    """
    测试当 interval=1 或未设置时，不应在 RRULE 中包含 INTERVAL。
    """
    from all2ics.schema import RRule
    
    # interval=1 的情况
    course_interval_1 = CourseEvent(
        name="测试课程1",
        location="教室1",
        begin="2025-01-15 10:00:00",
        end="2025-01-15 12:00:00", 
        rrule=RRule(
            freq="WEEKLY",
            interval=1,
            count=10
        )
    )
    
    # 没有设置 interval 的情况
    course_no_interval = CourseEvent(
        name="测试课程2",
        location="教室2", 
        begin="2025-01-15 14:00:00",
        end="2025-01-15 16:00:00",
        rrule=RRule(
            freq="WEEKLY",
            count=10
        )
    )
    
    schedule = [course_interval_1, course_no_interval]
    ics_content = create_ics_from_schedule(schedule)
    
    # 验证 INTERVAL=1 不会出现在 RRULE 中（因为1是默认值）
    assert "INTERVAL=1" not in ics_content
    assert "RRULE:FREQ=WEEKLY;COUNT=10" in ics_content