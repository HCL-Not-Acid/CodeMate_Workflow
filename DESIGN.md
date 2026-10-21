# CodeMate Workflow 设计说明

## 1. 目标与范围

本项目实现一个轻量级的 Mini SE 软件开发工作流：将用户的自然语言需求依次交给需求分析、方案设计和代码生成三个 Agent。项目重点是演示 Agent 职责划分、阶段间信息传递、顺序编排及运行状态管理。

当前版本面向命令行使用，不包含可视化编排、并行执行、跨运行状态存储或自动恢复机制。

## 2. 架构概览

```text
用户需求
   │
   ▼
SimpleWorkflow
   ├── RequirementAgent ──需求分析文本──┐
   ├── DesignAgent ◄────────────────────┘
   │        │
   │        └──设计方案──┐
   └── CodingAgent ◄─────┘
            │
            ▼
     去除代码围栏并做 AST 语法检查
            │
            ▼
     generated_program.py
```

`RequirementAgent`、`DesignAgent` 和 `CodingAgent` 都继承 `ModelAgent`。`ModelAgent` 使用统一的 OpenAI 兼容客户端调用百炼服务，具体 API Key、服务地址和模型名由 `config.py` 提供。

## 3. Agent 职责和接口

### 3.1 ModelAgent

文件：`agents/model_agent.py`

公共基类负责创建模型客户端，并组合系统提示词和用户输入发送请求。`run(user_input)` 返回模型回答文本。当前调用为同步调用，没有重试逻辑。

### 3.2 RequirementAgent

文件：`agents/requirement_agent.py`

接收用户原始需求，整理目标、输入、输出、处理规则和边界情况。它只负责分析，不设计模块或编写程序。

### 3.3 DesignAgent

文件：`agents/design_agent.py`

接收需求分析文本，输出设计目标、模块划分、处理流程、接口和边界处理方案。它不生成完整程序代码。

### 3.4 CodingAgent

文件：`agents/coding_agent.py`

接收原始需求、需求分析结果和设计方案，输出完整 Python 程序。提示词要求它遵循用户明确要求并提供必要的交互操作提示；提示词只能引导模型，不能保证输出完全正确。

## 4. 阶段配置与执行

### 4.1 WorkflowStage

`workflow.py` 使用不可变数据类 `WorkflowStage` 描述工作流节点：

| 字段 | 含义 |
|---|---|
| `name` | 阶段名称，用于终端提示和错误追踪 |
| `output_key` | 阶段结果写入共享状态时使用的字段名 |
| `run` | 接收当前状态字典并返回字符串结果的函数 |

默认阶段在 `SimpleWorkflow._build_stages()` 中按顺序配置。`SimpleWorkflow(stages=...)` 可以接收自定义阶段列表；每个阶段读取需要的状态字段并写回自己的输出字段。空阶段列表会被拒绝。

### 4.2 默认阶段的数据流

```text
state.user_requirement
        │
        ▼
RequirementAgent.run(user_requirement)
        │
        ▼
state.requirement_analysis
        │
        ▼
DesignAgent.run(requirement_analysis)
        │
        ▼
state.design_plan
        │
        ▼
CodingAgent.run(user_requirement, requirement_analysis, design_plan)
        │
        ▼
state.generated_code
```

`SimpleWorkflow.run()` 遍历阶段列表。阶段只有在前一阶段成功并返回非空字符串后才会运行。默认代码生成阶段会清理 Markdown 围栏，并通过 `ast.parse()` 检查语法。

### 4.3 默认入口

`main()` 从终端读取多行需求，以空行为输入结束标记；执行默认工作流后，将 `generated_code` 写入项目当前目录的 `generated_program.py`。保存文件可能覆盖之前的生成结果。程序不会自动执行生成文件。

## 5. 共享状态

每次 `run()` 创建独立的状态字典：

| 字段 | 类型 | 用途 |
|---|---|---|
| `user_requirement` | `str` | 用户原始需求 |
| `requirement_analysis` | `str` | 需求分析阶段结果 |
| `design_plan` | `str` | 方案设计阶段结果 |
| `generated_code` | `str` | 代码生成阶段结果 |
| `current_stage` | `str` | 正在执行的阶段或最终阶段标记 |
| `status` | `str` | `running`、`completed` 或 `failed` |
| `error` | `str` 或 `None` | 工作流失败摘要 |
| `stage_timings` | `dict[str, float]` | 各阶段耗时，单位为秒 |
| `stage_errors` | `dict[str, str]` | 各失败阶段及其错误详情 |

阶段结果写入状态后，后续阶段通过状态字典读取。状态只保存在内存中，工作流结束后不会写入文件或数据库。

## 6. 配置与错误处理

`config.py` 使用 `python-dotenv` 从项目根目录的 `.env` 读取 `DASHSCOPE_API_KEY`。创建默认工作流前会调用 `validate_config()`；缺少 Key 时抛出中文配置错误，由 `main()` 显示并结束。`.env` 不应提交到版本控制。

执行阶段出现异常或返回空内容时，工作流会：

1. 将错误写入 `stage_errors`，并将耗时写入 `stage_timings`；
2. 设置 `status` 为 `failed`，保留失败的 `current_stage`；
3. 在 `error` 中记录阶段名称和异常信息；
4. 停止后续阶段。

阶段耗时和成功/失败状态会打印到终端。当前没有自动重试或自动恢复。最终文件写入失败由 `main()` 单独报告。

## 7. 测试策略

### 7.1 自动化测试

`tests/test_workflow.py` 使用 `unittest.mock` 替代三个 Agent，不访问网络、不需要 API Key。它检查：

- 三个阶段的调用顺序和前序结果传递；
- 状态字段、阶段耗时是否生成；
- 某阶段失败后是否记录错误并阻止后续阶段；
- 生成代码语法错误是否作为代码生成阶段失败处理。

`tests/test_config.py` 检查 API Key 缺失和已配置两种情况。运行命令：

```powershell
python -m unittest discover -s tests -v
```

这些测试验证工作流编排和配置逻辑，不判断真实模型回答的质量，也不证明模型生成程序在功能上正确。

### 7.2 真实模型演示脚本

项目根目录中的 `test_requirement_agent.py`、`test_design_agent.py` 和 `test_coding_agent.py` 会调用真实模型，适合观察 Agent 输出，需要网络和 API Key，并可能产生费用。`test_coding_agent.py` 直接调用三个 Agent 并保存代码，不经过 `SimpleWorkflow` 的阶段状态、耗时和语法校验。

## 8. 当前限制

- 模型输出存在不确定性，提示词不等同于输出校验。
- AST 检查只检查语法，不会执行生成程序，也不能验证业务行为。
- 流程为同步顺序执行；没有高级分支、循环、并行、模型调用重试或自动修复。
- 阶段记录仅在当前运行中保留，未持久化；终端输出不是结构化日志文件。
- 自动化测试使用假响应，只覆盖程序编排；真实模型行为需通过演示脚本和针对生成程序的功能检查评估。
