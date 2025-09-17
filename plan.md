**# 角色与使命 (Role & Mission)**

你好，Copilot Agent。你的角色是一名资深的Python开源项目开发者。你的任务是独立、完整地创建并测试一个名为 `all2ics` 的项目。

**项目核心使命**：`all2ics` 是一个命令行工具，旨在帮助用户将一个特定格式的、由AI大模型生成的课程表 JSON 文件，轻松转换为通用的 iCalendar (.ics) 格式文件。在项目的初始阶段（MVP），我们假定用户已经通过与他们自己的大模型（如 Gemini, GPT 等）交互，获取了符合我们规范的 JSON 文件。你的任务是专注于**JSON 的验证和转换**。

**语言要求**：项目中所有的代码注释、文档、命令行输出、帮助信息以及用户指南，**必须全部使用简体中文**。

---

**# 核心设计原则 (Core Design Principles)**

你在开发过程中必须严格遵守以下原则：

1.  **现代架构 (Modernity)**:
    *   **项目管理**: 使用 `pyproject.toml` 作为唯一的项目配置文件。
    *   **环境与依赖**: 项目必须使用 `uv` 进行环境和包管理。所有依赖项都在 `pyproject.toml` 中声明。
    *   **语言**: 使用 Python 3.9 或更高版本，并全程使用类型提示 (Type Hinting)。

2.  **高度可扩展性 (Extensibility)**:
    *   **模块化设计**: 将核心逻辑分离到不同的模块中。例如：数据结构定义 (`schema.py`)、核心转换逻辑 (`converter.py`)、命令行接口 (`cli.py`)。这为未来增加 Web 界面、直接集成 AI API 等功能奠定基础。
    *   **健壮的数据接口**: **必须使用 `Pydantic`** 来定义和验证输入的 JSON 数据结构。这是保证系统稳定和未来扩展的关键。

3.  **极致易用性 (Usability)**:
    *   **友好的命令行**: **必须使用 `Typer`** 来构建命令行界面（CLI）。它能自动生成帮助文档，并且接口清晰。
    *   **清晰的错误反馈**: 当用户提供的 JSON 格式错误或文件不存在时，必须在命令行中提供清晰、友好的中文错误提示。

---

**# 第一阶段 (MVP) 详细开发任务**

请按照以下结构和内容，一步一步创建项目文件：

#### **1. 项目根目录结构**

```
all2ics/
├── .gitignore
├── LICENSE
├── README.md
├── pyproject.toml
├── examples/
│   ├── sample_input.json
│   └── master_prompt_guide.md
├── src/
│   └── all2ics/
│       ├── __init__.py
│       ├── cli.py
│       ├── converter.py
│       └── schema.py
└── tests/
    └── test_converter.py
```

#### **2. 文件内容实现**

**a. `pyproject.toml`**
```toml
[project]
name = "all2ics"
version = "0.1.0"
description = "一个智能、可扩展的工具，用于将AI生成的课程表JSON转换为ICS日历文件。"
authors = [{name = "Copilot Agent", email = "agent@example.com"}]
license = {text = "MIT"}
requires-python = ">=3.9"
readme = "README.md"
dependencies = [
    "ics==0.7.2",
    "pydantic>=2.0",
    "typer[all]"
]

[project.scripts]
# 这个命令让用户可以通过在终端输入 `all2ics` 来调用程序
all2ics = "all2ics.cli:app"

[tool.pytest.ini_options]
pythonpath = ["src"]
```

**b. `src/all2ics/schema.py`**
*   **任务**: 使用 Pydantic 定义清晰、严格的 JSON 输入规范。

```python
# src/all2ics/schema.py

from pydantic import BaseModel, Field
from typing import List, Optional

class RRule(BaseModel):
    """
    定义 iCalendar 的重复规则 (RRULE)。
    这是实现“每周重复”等周期性事件的核心。
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
```

**c. `src/all2ics/converter.py`**
*   **任务**: 编写核心转换逻辑，它接收 Pydantic 验证后的数据模型，并生成 ICS 格式的字符串。

```python
# src/all2ics/converter.py

from ics import Calendar, Event
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
            
            e.rrule = ";".join(rrule_parts)

        c.events.add(e)
    
    # 返回序列化后的日历字符串
    return c.serialize()
```

**d. `src/all2ics/cli.py`**
*   **任务**: 使用 Typer 构建用户交互的命令行入口。

```python
# src/all2ics/cli.py

import typer
import json
from pathlib import Path
from pydantic import ValidationError
from typing_extensions import Annotated

# 导入核心模块
from .schema import CourseSchedule
from .converter import create_ics_from_schedule

# 创建一个 Typer 应用实例
app = typer.Typer(help="all2ics: 一个智能的课程表转换工具，将 AI 生成的 JSON 转换为 .ics 文件。")

@app.command(name="convert", help="转换 JSON 文件为 ICS 文件")
def convert(
    input_file: Annotated[Path, typer.Argument(
        help="输入的课程表 JSON 文件路径。",
        exists=True,      # 确保文件存在
        file_okay=True,   # 必须是文件
        dir_okay=False,   # 不能是目录
        readable=True,    # 必须可读
    )],
    output_file: Annotated[Path, typer.Argument(
        help="输出的 .ics 文件路径。如果未提供，则默认为 'schedule.ics'。",
        writable=True,    # 确保路径可写
    )] = Path("schedule.ics"),
):
    """
    读取用户提供的 JSON 文件，验证其格式，然后将其转换为 iCalendar (.ics) 文件。
    """
    typer.echo(f"🚀 正在读取输入文件: {input_file}")
    
    try:
        # 1. 读取和解码 JSON 文件
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 2. 使用 Pydantic 进行严格的格式验证和数据解析
        # 这是保证数据质量的关键步骤
        schedule = [CourseEvent.model_validate(item) for item in data]
        typer.echo("✅ JSON 格式验证通过！数据结构符合规范。")

        # 3. 调用核心转换逻辑
        typer.echo("⚙️ 正在生成 ICS 内容...")
        ics_content = create_ics_from_schedule(schedule)

        # 4. 将生成的 ICS 内容写入输出文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(ics_content)
        
        typer.echo(f"🎉 成功！您的课程表已保存至: {output_file}")
        typer.echo("现在您可以将此文件导入到您的日历应用中 (如 Google Calendar, Apple Calendar)。")

    except json.JSONDecodeError:
        typer.secho("❌ 错误: 输入文件不是一个有效的 JSON。请检查文件内容。", fg=typer.colors.RED)
    except ValidationError as e:
        typer.secho("❌ 错误: JSON 内容不符合预设的课程表格式规范。", fg=typer.colors.RED)
        typer.echo("详细错误信息如下，请根据此信息修正您的 JSON 文件或 Prompt:")
        typer.echo(str(e))
    except Exception as e:
        typer.secho(f"❌ 发生了一个未知错误: {e}", fg=typer.colors.RED)

if __name__ == "__main__":
    app()
```

---

**# 文档与示例编写要求**

**a. `README.md`**
*   **任务**: 撰写一份高质量的、对用户友好的项目说明书。

````markdown
# all2ics - 智能课程表转换器

[![PyPI version](https://badge.fury.io/py/all2ics.svg)](https://badge.fury.io/py/all2ics) <!-- 你可以先用占位符 -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**`all2ics` 是一个智能、可扩展的命令行工具，用于将AI大模型生成的课程表 JSON 文件，轻松转换为通用的 iCalendar (.ics) 格式文件。**

## ✨ 核心理念

我们发现，直接让 AI 输出 `.ics` 文件效果往往不佳且格式不稳定。而让 AI 输出结构化的 `JSON` 则非常可靠。

`all2ics` 的工作流正是基于此：
**用户提供上下文 -> AI 生成标准 JSON -> `all2ics` 验证并转换为 ICS 文件**

这个流程将复杂的格式转换任务，变成了一个简单可靠的两步操作。

## 🚀 安装

确保你的 Python 版本 >= 3.9。我们推荐使用 `uv` 进行安装：

```bash
uv pip install all2ics
```

## 💡 使用方法

### **第一步：获取课程表 JSON**

这是最关键的一步。你需要与你选择的 AI 大模型（如文心一言、Gemini、ChatGPT等）进行交互，让它根据你的课表和一些上下文信息，生成符合规范的 JSON 文件。

我们为你准备了一份效果极佳的 **“大师级 Prompt”**，请查看：
[👉 **`examples/master_prompt_guide.md`**](./examples/master_prompt_guide.md)

请将该文件中的 Prompt 模板复制，填入你自己的信息后，发送给 AI。然后将 AI 返回的 JSON 代码块保存为一个文件，例如 `my_courses.json`。

我们也提供了一个输出示例，供你参考：[👉 `examples/sample_input.json`](./examples/sample_input.json)

### **第二步：运行转换命令**

打开你的终端，运行以下命令：

```bash
all2ics convert <你的JSON文件路径> [输出的ICS文件路径]
```

**示例:**
```bash
# 将 my_courses.json 转换为默认的 schedule.ics
all2ics convert my_courses.json

# 将 my_courses.json 转换为指定路径的 my_calendar.ics
all2ics convert ./data/my_courses.json ./output/my_calendar.ics
```
转换成功后，你就可以将生成的 `.ics` 文件导入到任何支持 iCalendar 格式的日历应用中了！

## 🗺️ 未来路线图 (Roadmap)

`all2ics` 的设计具有高度可扩展性，我们计划在未来：
- [ ] **直接集成 AI API**: 在工具内直接调用大模型，实现端到端自动化。
- [ ] **支持更多输入源**: 如直接解析 Excel (`.xlsx`) 文件或课表截图 (`.png`)。
- [ ] **Web 用户界面**: 提供一个图形化界面，让操作更简单。

##🤝 贡献

我们非常欢迎各种形式的贡献！无论是提交 Issue、修复 Bug 还是实现新功能。请随时 Fork 本项目并发起 Pull Request。

##📄 许可证

本项目基于 [MIT License](./LICENSE) 开源。
````

**b. `examples/master_prompt_guide.md`**
*   **任务**: 创建一份详细的指南，教用户如何与 AI 交互以获取正确的 JSON。

````markdown
# 大师级 Prompt 指南 (Master Prompt Guide)

为了让 `all2ics` 工具能够正常工作，你需要先从 AI 大模型那里获取一份格式正确的 JSON 文件。请复制以下模板，**修改 `【】`中的占位符为你自己的真实信息**，然后发送给你正在使用的大模型（如 Gemini, GPT, 文心一言等）。

---

## Prompt 模板

你是一位专业的课表分析助手。你的任务是严格按照我提供的上下文信息和格式规范，从非结构化的课表文本中，提取所有课程安排，并生成一个结构化的 JSON 数组。

**重要上下文信息:**
*   学期第一周的周一日期是: **【例如: 2025-09-01】**
*   节次时间映射表 (请根据你的学校实际情况修改):
    *   "1-2": { "begin": "08:00:00", "end": "09:40:00" }
    *   "3-4": { "begin": "10:00:00", "end": "11:40:00" }
    *   "3-5": { "begin": "10:00:00", "end": "12:25:00" }
    *   "6-8": { "begin": "14:00:00", "end": "16:25:00" }
    *   "8-10": { "begin": "18:30:00", "end": "20:55:00" }
    *   **【请在此处继续添加或修改你的学校的节次时间】**

**输出的 JSON 格式规范 (必须严格遵守):**
```json
[
  {
    "name": "课程名称",
    "location": "上课地点",
    "description": "附加信息，例如：'教师: 张三'",
    "begin": "首次上课的开始日期和时间 (格式: 'YYYY-MM-DD HH:MM:SS')",
    "end": "首次上课的结束日期和时间 (格式: 'YYYY-MM-DD HH:MM:SS')",
    "rrule": {
        "freq": "WEEKLY",
        "until": "最后一次上课所在的周的结束日期 (格式: 'YYYY-MM-DD')"
    }
  }
]
```
**处理规则:**
1.  根据“学期第一周的周一日期”和课程的周次、星期信息，精确计算出 `begin` 和 `end` 的具体日期。
2.  根据课程的结束周次，精确计算出 `rrule` 中的 `until` 日期。
3.  如果一门课在原始文本中有多个不同的上课时间/地点（用分号隔开），请为每一个时间/地点组合生成一个独立的 JSON 对象。
4.  如果一门课只上一次（例如只有第10周），则输出的 JSON 对象中**不应包含** `rrule` 字段。

---

**【请在这里粘贴你的原始课表文本或截图中的文字】**

例如:
```
课程: [610ZH111]软件工程
任课教师:徐健锋
上课时间地点: 1-9周 四[3-5] 机电楼E214(276); 10周 六[6-8] 机电楼E214(276)
```

---
请开始处理。
````

**c. `examples/sample_input.json`**
*   **任务**: 创建一个符合 `schema.py` 规范的示例 JSON 文件。

```json
[
  {
    "name": "软件工程",
    "location": "机电楼E214(276)",
    "description": "教师: 徐健锋",
    "begin": "2025-09-04 10:00:00",
    "end": "2025-09-04 12:25:00",
    "rrule": {
      "freq": "WEEKLY",
      "until": "2025-10-31"
    }
  },
  {
    "name": "软件工程",
    "location": "机电楼E214(276)",
    "description": "教师: 徐健锋",
    "begin": "2025-11-08 14:00:00",
    "end": "2025-11-08 16:25:00"
  },
  {
    "name": "计算机网络",
    "location": "机电楼E625(135)",
    "description": "教师: 韩清",
    "begin": "2025-09-05 10:00:00",
    "end": "2025-09-05 12:25:00",
    "rrule": {
      "freq": "WEEKLY",
      "until": "2025-12-20"
    }
  }
]
```

---

**# 测试要求 (Testing Requirements)**

**a. `tests/test_converter.py`**
*   **任务**: 编写一个基本的单元测试，确保核心转换功能正常工作。

```python
# tests/test_converter.py

import json
from pathlib import Path
from all2ics.schema import CourseSchedule
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
```

**b. 其他文件**
*   **`LICENSE`**: 生成标准的 MIT 许可证文本。
*   **`.gitignore`**: 生成一个标准的 Python 项目 `.gitignore` 文件（包含 `__pycache__`, `.venv`, `*.pyc` 等）。

---

**# 最终指令 (Final Instruction)**

你已经接收了完整的项目蓝图。请现在以一名专业、严谨的开发者身份，开始逐步创建和实现上述所有文件和代码。确保每一步都符合设计原则，代码风格清晰，注释详尽。开发完成后，请准备好整个项目的目录结构和文件内容，以便进行最终的审查。完成后，请准备好整个项目的目录结构和文件内容，以便进行最终的审查。
