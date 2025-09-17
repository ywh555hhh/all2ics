# src/all2ics/cli.py

import typer
import json
from pathlib import Path
from pydantic import ValidationError
from typing_extensions import Annotated

# 导入核心模块
from .schema import CourseSchedule, CourseEvent
from .converter import create_ics_from_schedule

# 创建一个 Typer 应用实例
app = typer.Typer(help="all2ics: 一个智能的课程表转换工具，将 AI 生成的 JSON 转换为 .ics 文件。")

@app.command(help="转换 JSON 文件为 ICS 文件")
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