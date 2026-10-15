# CodeMate Workflow

一个基于大语言模型的多 Agent 软件开发工作流 MVP，使用 Python 实现需求分析、方案设计和代码生成三个阶段，探索 Agent 协作、工作流编排与状态管理。

## 1. 项目简介

CodeMate Workflow 是一个轻量级的软件开发工作流项目。用户输入软件开发需求后，系统依次调用三个具有不同职责的 Agent，将自然语言需求逐步转化为软件设计方案和可运行的程序代码。

本项目采用 Mini SE（Software Engineering）流程：

**需求分析 → 方案设计 → 代码生成**

项目使用阿里云百炼提供的兼容 OpenAI 接口的大语言模型服务，通过公共基础类封装模型调用，并由 `workflow.py` 统一管理执行流程。

## 2. 主要功能

- **需求分析：** 将用户的自然语言需求整理为结构化的需求说明。
- **方案设计：** 根据需求分析结果，制定程序的模块划分、处理流程和关键接口。
- **代码生成：** 根据用户原始需求、需求分析结果和设计方案生成程序代码。
- **顺序编排：** 通过统一的工作流入口依次执行三个 Agent。
- **状态管理：** 使用共享状态记录原始需求、各阶段输出、当前执行阶段和执行状态。
- **结果保存：** 将生成的程序代码保存到 `generated_program.py`。
- **基础错误处理：** 当模型调用失败或某个阶段没有返回有效内容时，记录错误并停止后续阶段。

## 3. 工作流程

```text
用户输入软件需求
        |
        v
RequirementAgent
需求分析
        |
        v
DesignAgent
方案设计
        |
        v
CodingAgent
代码生成
        |
        v
生成代码并保存
        |
        v
generated_program.py
```

三个 Agent 按照固定顺序执行。每个阶段生成的结果会传递给后续阶段；同时，工作流保存各阶段的输出，供流程管理和结果追踪使用。

## 4. 项目结构

```text
CodeMate_Workflow/
├── agents/
│   ├── __init__.py
│   ├── model_agent.py
│   ├── requirement_agent.py
│   ├── design_agent.py
│   └── coding_agent.py
├── workflow.py
├── config.py
├── requirements.txt
├── .env
├── .gitignore
├── test_requirement_agent.py
├── test_design_agent.py
├── test_coding_agent.py
├── generated_program.py
├── README.md
└── DESIGN.md
```

说明：

- `agents/model_agent.py`：封装大语言模型的调用逻辑，供其他 Agent 复用。
- `agents/requirement_agent.py`：实现需求分析 Agent。
- `agents/design_agent.py`：实现方案设计 Agent。
- `agents/coding_agent.py`：实现代码生成 Agent。
- `workflow.py`：工作流入口，负责编排三个 Agent、管理共享状态并保存最终代码。
- `config.py`：读取模型 API 配置。
- `requirements.txt`：记录项目依赖。
- `.env`：在本地保存 API Key 等敏感配置，不应提交到远程仓库。
- `test_requirement_agent.py`：单独测试需求分析 Agent。
- `test_design_agent.py`：测试需求分析和方案设计阶段。
- `test_coding_agent.py`：联合测试三个 Agent 并生成程序代码。
- `generated_program.py`：工作流运行后生成的程序文件，每次成功生成后可能被覆盖。

测试脚本也可以在后续统一整理到 `tests/` 目录中。

## 5. 环境要求

- Python 3.10 或更高版本
- 可访问阿里云百炼模型服务的网络环境
- 有效的阿里云百炼 API Key

项目依赖包括 `openai` 和 `python-dotenv`，具体安装依赖以 `requirements.txt` 为准。

## 6. 安装与配置

### 6.1 获取项目并创建虚拟环境

在终端进入项目根目录，然后执行：

```bash
python -m venv .venv
```

Windows PowerShell 激活虚拟环境：

```powershell
.\.venv\Scripts\Activate.ps1
```

如果使用 Windows CMD：

```bat
.venv\Scripts\activate.bat
```

### 6.2 安装依赖

确保虚拟环境已经激活，然后执行：

```bash
python -m pip install -r requirements.txt
```

### 6.3 配置 API Key

在项目根目录创建本地 `.env` 文件，写入自己的阿里云百炼 API Key：

```text
DASHSCOPE_API_KEY=在这里填写你自己的API密钥
```

项目通过 `config.py` 读取环境变量，并配置模型访问地址和模型名称。

请勿将 `.env` 上传到 GitHub 或 Gitee，也不要在代码、日志和文档中公开真实 API Key。

## 7. 运行项目

在项目根目录运行：

```bash
python workflow.py
```

按照提示输入软件开发需求。可以输入多行内容，输入完成后提交一个空行，工作流便开始执行。

系统依次展示：

1. 需求分析结果
2. 方案设计结果
3. 生成的程序代码

工作流成功完成后，代码将保存到项目根目录下的 `generated_program.py`。

例如，可以输入：

```text
请开发一个 Python 命令行程序。
用户逐个输入学生成绩，每次输入一个成绩。
输入空行时结束录入。
录入结束后计算并显示平均分、最高分和最低分。
平均分保留两位小数。
如果没有输入任何成绩，应显示提示信息。
不需要把成绩保存到文件。
```

生成程序后，可以根据实际需求检查代码，再使用 Python 运行：

```bash
python generated_program.py
```

注意：当前工作流负责生成和保存代码，不会自动执行生成的程序。

## 8. 测试方法

项目提供三个测试脚本，用于分别验证 Agent 的功能和协作流程。

单独测试需求分析 Agent：

```bash
python test_requirement_agent.py
```

测试需求分析和方案设计两个阶段：

```bash
python test_design_agent.py
```

测试三个 Agent 的联合调用和代码生成：

```bash
python test_coding_agent.py
```

这些脚本会调用大语言模型，因此运行时需要正确配置 API Key，并可能产生模型调用费用。

测试脚本主要用于开发阶段的验证；正式的工作流入口为 `workflow.py`。

## 9. 当前实现与限制

当前版本实现了三个 Agent 的顺序编排、阶段间的结果传递、共享状态记录、基础错误处理和代码文件保存。

目前仍有以下限制：

- Agent 输出由大语言模型生成，内容和表达可能存在差异。
- 提示词能够约束 Agent 的职责，但不能保证模型在所有情况下都严格遵守要求。
- 当前流程采用固定的顺序执行方式，不包含并行执行、复杂条件分支或可视化编排界面。
- 生成代码保存后需要人工检查；工作流暂未集成代码语法验证、自动执行或自动修复机制。
- 共享状态仅在当前工作流运行过程中使用，没有实现跨运行的持久化存储。
- 基础错误处理能够报告阶段失败，但暂未实现自动重试与恢复。

## 10. 后续改进方向

后续可以围绕以下方向完善项目：

- 增加生成代码的语法检查。
- 补充执行日志和阶段状态追踪。
- 完善异常场景测试。
- 增加必要的输出校验和错误恢复机制。
- 根据实际需求扩展 Agent 或调整工作流。

## 11. 项目总结

本项目通过需求分析、方案设计和代码生成三个 Agent，构建了一个可运行的轻量级软件开发工作流 MVP。

项目重点在于验证 Agent 的职责分工、顺序执行、消息传递和共享状态管理，为后续扩展更完整的软件开发自动化流程提供基础。