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

我们为你准备了一份效果极佳的 **"大师级 Prompt"**，请查看：
[👉 **`examples/master_prompt_guide.md`**](./examples/master_prompt_guide.md)

请将该文件中的 Prompt 模板复制，填入你自己的信息后，发送给 AI。然后将 AI 返回的 JSON 代码块保存为一个文件，例如 `my_courses.json`。

我们也提供了一个输出示例，供你参考：[👉 `examples/sample_input.json`](./examples/sample_input.json)

### **第二步：运行转换命令**

打开你的终端，运行以下命令：

```bash
all2ics convert <你的JSON文件路径> [输出的ICS文件路径] [选项]
```

**基础示例:**
```bash
# 将 my_courses.json 转换为默认的 schedule.ics（使用上海时间）
all2ics convert my_courses.json

# 将 my_courses.json 转换为指定路径的 my_calendar.ics
all2ics convert my_courses.json my_calendar.ics
```

**时区和高级选项:**
```bash
# 指定默认时区为北京时间（与上海时间相同）
all2ics convert my_courses.json --timezone Asia/Shanghai

# 使用UTC时区
all2ics convert my_courses.json --timezone UTC

# 使用纽约时间
all2ics convert my_courses.json --timezone America/New_York

# 显示详细处理信息
all2ics convert my_courses.json --verbose

# 组合使用选项
all2ics convert my_courses.json my_calendar.ics --timezone Asia/Shanghai --verbose

# 查看常用时区列表
all2ics timezones
```

**🌍 时区说明:**
- **默认时区**: Asia/Shanghai (上海时间，北京时间)
- 支持在JSON文件中为每个课程单独设置时区
- 支持全球所有标准时区格式
- 常用时区示例：`Asia/Shanghai`, `UTC`, `America/New_York`, `Europe/London`
转换成功后，你就可以将生成的 `.ics` 文件导入到任何支持 iCalendar 格式的日历应用中了！

## 🗺️ 未来路线图 (Roadmap)

`all2ics` 的设计具有高度可扩展性，我们计划在未来：
- [ ] **直接集成 AI API**: 在工具内直接调用大模型，实现端到端自动化。
- [ ] **支持更多输入源**: 如直接解析 Excel (`.xlsx`) 文件或课表截图 (`.png`)。
- [ ] **Web 用户界面**: 提供一个图形化界面，让操作更简单。

## 🤝 贡献

我们非常欢迎各种形式的贡献！无论是提交 Issue、修复 Bug 还是实现新功能。请随时 Fork 本项目并发起 Pull Request。

## 📄 许可证

本项目基于 [MIT License](./LICENSE) 开源。