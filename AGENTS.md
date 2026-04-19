# AGENTS.md

本文件面向本仓库的开发者与自动化 Agent，只记录“容易做错/猜错”的约束。

## 1) 先看哪里（高优先级）

- 先读 `pyproject.toml`（版本、入口、依赖、构建配置）和 `README.md`（对外使用约定）。
- 需要改内部机制时，再看 `DEVELOPMENT.md`（解析/渲染架构）；涉及性能时看 `BENCHMARKING.md`。
- 本项目采用 uv 的 `src/` 包布局：业务代码在 `src/markcraft/`，测试在 `tests/`。

## 2) 运行与验证（最小闭环）

- 使用 `uv` 执行命令，Python 要求 `>=3.13`。
- 开发前建议先 `uv sync`，确保依赖一致。
- 改动后最小可用验证：

```bash
uv run pytest
```

- 如涉及性能相关改动，再补跑：

```bash
uv sync --group benchmark
uv run python tests/benchmark.py
```

## 3) 代码结构（按职责改）

- `src/markcraft/parser/`: 新版解析流程（document、tokens、tokenizers、state）。
- `src/markcraft/tokens/` 与 `src/markcraft/tokens/block/`: 语法 token 定义、注册与优先级行为。
- `src/markcraft/renderers/`: HTML/LaTeX/AST/Markdown 等核心渲染器。
- `src/markcraft/extensions/` 与 `src/markcraft/renderers/extensions.py`: 扩展渲染器与聚合导出。
- `tests/`: 单元测试、样例输入输出、规范测试与基准脚本。

## 4) 修改约束与兼容性

- 优先保持 CommonMark 行为稳定，新增语法或调整优先级时必须补测试。
- 修改 `tokens/block` / `tokens/span` / tokenizer（含 `parser/tokenizers.py`）时，要同时检查 HTML、Markdown、extensions 渲染器输出。
- 对外公共接口（如 `markcraft.render` / `markcraft.parse`）变更需在 `README.md` 同步说明。
- 文档一致性是强约束：代码改动若影响使用方式、入口函数、参数或默认行为，必须在同一变更中同步更新 `README.md` 与 `DEVELOPMENT.md`。
- 若改动涉及基准脚本、运行命令或性能流程，需同步检查 `tests/benchmark.py`、`BENCHMARKING.md`、`README.md` 的命令与示例是否一致。
- 提交前至少执行一次“文档对齐自检”：在仓库内搜索旧 API 名称，确保示例代码、文字说明、测试/脚本调用均已切换。

## 4.1) README 写作原则（面向用户）

- `README.md` 是“对外使用文档”，优先回答“这个项目是什么、为什么用、怎么上手”。
- 不写“改文档的理由/过程说明/术语争议背景”等元信息；这些属于 PR 描述，不属于 README。
- 只保留对用户决策有帮助的信息：能力边界、安装方式、真实可运行示例、兼容性约束。
- 术语以“现状准确 + 用户可理解”为准；避免在 README 中解释历史命名或内部迁移细节，除非直接影响使用。
- 文风可有吸引力，但避免营销空话；每个卖点都应能在代码或示例中被验证。

## 5) 版本与发布

- 项目版本需保持一致：`pyproject.toml` 与 `src/markcraft/__init__.py` 同步更新。
- 如使用脚本批量更新版本，参考 `tests/bump_version.sh`。

## 6) 提交日志强制规则（全仓库生效）

- All commit messages must be written in English.
- The first line must open with two short Shakespearean-style phrases, kept on the same line with exactly one space between them, summarizing the change.
- After the opening line, add an English body explaining motivation, key changes, and impact scope.

格式：

```text
<Shakespearean short phrase 1> <Shakespearean short phrase 2>

<English body>
```

若发现最近提交不合规，且提交尚未推送，优先修正为合规格式。

- 使用命令行提交时，`git commit -m` 的消息中不要包含反引号（`` ` ``）；shell 会触发命令替换，导致提交信息被破坏。
- 需要在提交信息中写代码标识符时，优先使用普通引号（如 'markcraft.render'）或直接不用包裹符号。
- 对于多行/复杂提交说明，优先使用单引号包裹 `-m` 内容，或用编辑器方式提交（仅 `git commit`）以避免 shell 转义问题。

## 7) Python 3.13 代码约定（实用）

- 新文件默认使用 `from __future__ import annotations`，降低前向引用与循环依赖场景的类型负担。
- 统一使用现代类型语法：`list[str]`、`dict[str, Any]`、`X | None`。
- 需要在运行时解析注解时，使用 `typing.get_type_hints()`，不要直接依赖 `__annotations__` 的字面值。
- 保持 Pydantic v2 风格：`model_validate` / `model_dump`，不要混用 v1 API。
- 命令行参数尽早校验（CLI 层），避免把非法输入下沉到 `services`。
