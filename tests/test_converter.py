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
    assert "RRULE:FREQ=WEEKLY;UNTIL=20251031T235959Z" in ics_content
    assert "SUMMARY:计算机网络" in ics_content