# CYH Flow

面向 Codex 的跨项目软件交付工作流 Skill，用同一套授权边界处理方案设计、代码实现、只读审查和 Goal 驱动的持续修复，避免“先看看”被误解为直接改代码，也避免一次实现请求被自动扩大成提交、推送或部署。

```text
用户请求
   |
   +-- plan   -> 只读调查 -> 可执行方案
   +-- build  -> 范围内修改 -> 分层验证
   +-- review -> 只读审查 -> 有证据的 findings / clean result
   `-- fix    -> Goal: review -> 修复 -> 对抗复审 -> 循环至零 finding
```

## 四种模式

| 模式 | 适合处理 | 默认允许 | 默认不允许 |
| --- | --- | --- | --- |
| `plan` | 理解需求、追踪调用链、评估影响、制定实施方案 | 读取代码、配置、文档和实时状态 | 修改文件、建分支、提交、推送、部署或更新外部系统 |
| `build` | 实现明确需求、计划、Issue 或已确认修复 | 在约定范围内修改本地文件并运行验证 | 未经明确要求的提交、推送、PR、部署、生产写入或对外消息 |
| `review` | 审查工作区、分支、提交或 Pull Request | 读取完整 diff、上下文、检查与实时 PR 状态 | 直接修复、提交、推送、批准、发评论或改变 PR 状态 |
| `fix` | 持续审查和修复复杂问题，直到各适用角度没有可证实 finding | 建立 Goal、范围内本地修复、验证、只读多 Agent 对抗复审 | 未经明确要求的提交、推送、PR、部署、生产写入或对外消息 |

四种模式共享几条硬边界：永不 Merge PR；不擅自丢弃或覆盖用户工作；破坏性 Git 操作必须先说明精确目标和损失范围；源码检查、自动化测试、CI、部署运行时、UI/设备证据与业务验收分别报告，不能互相替代。

`fix` 中的“bug 为 0”是一个可验证停止条件：当前范围内 finding 台账归零，最终代码变更后最新一轮独立对抗审查没有新增可证实问题，且 Goal 约定的检查和真实流程证据全部满足；它不表示对软件做“绝对无 bug”的不可证明承诺。多个 reviewer 只读并分别挑战正确性、安全、兼容性、测试和运行时等适用角度，主 Agent 统一验证、去重和修复，避免并行写代码造成冲突。

## 安装

### Skill Manager

在 [Skill Manager](https://github.com/cyh-skill/skill-manager) 中导入本仓库 URL：

```text
https://github.com/cyh-skill/cyh-flow
```

这是一个高频基础工作流，通常适合选择“托管直装”；如果只想在少数任务中使用，也可以放进 Lazy 冷库，由 `skill-router` 按需加载。

### 手动安装

仓库当前为私有仓库，先确认 `gh` 已登录且账号有访问权限，然后克隆到 Codex Skill 目录：

```bash
gh auth status
gh repo clone cyh-skill/cyh-flow ~/.agents/skills/cyh-flow
```

更新已有安装：

```bash
git -C ~/.agents/skills/cyh-flow pull --ff-only
```

重新启动 Codex 会话后即可发现该 Skill。仓库目前主要按 Codex 的宿主行为和项目约定维护；其他 Agent 即使能读取 `SKILL.md`，命令、规则文件和工具能力也可能不同，不应直接假定完全兼容。

## 使用

显式调用时使用 `$cyh-flow`，它是 Skill 名称，不是 shell 命令，也不是 `/` 开头的 Codex 宿主命令：

```text
$cyh-flow plan 给结账流程增加批量确认，先分析影响并出方案

$cyh-flow build 按 Issue #123 实现，并运行相关测试；不要提交或推送

$cyh-flow review PR #456，只做 review，不修改代码

$cyh-flow fix 修复结账流程的并发问题，建立 Goal，持续对抗复审和修复直到零个可证实 finding
```

也可以直接用自然语言描述任务；命中 `SKILL.md` 中的适用范围时，Codex 可以自动选择该 Skill。普通的一次性 bug 修复仍属于 `build`；只有明确要求 Goal、对抗 Agent、重复 review/fix 或“直到 bug 为 0”时才进入 `fix`。若一句话混合了多个模式，CYH Flow 会保留每个阶段的权限边界：方案不会自动进入实现，审查不会自动变成修复，实现或持续修复也不会自动进入交付。

## 工作原则

- 先确认真实仓库、工作树、分支、子模块或 worktree，再开始调查或修改。
- 优先读取项目自己的 `AGENTS.md` 和文档；项目规则比通用工作流更具体时，以项目规则为准。
- 存在 `.codegraph/` 且 CodeGraph 可用时，优先用它理解架构、依赖和调用路径。
- GitHub 操作默认使用已认证的 `gh`，并在依赖实时状态时重新读取 PR、检查和远端引用。
- 浏览器自动化固定使用 `browser-skill:cyh-browser-skill`；普通公开网页检索使用常规搜索能力。
- 只做满足需求的最小完整改动，复用现有模式，保留无关的已跟踪和未跟踪文件。
- 最终答复先给结论，再说明证据、未完成验证和仍需用户授权的下一步。

## 仓库结构

```text
cyh-flow/
|-- SKILL.md                 # Skill 入口、模式路由和共享边界
|-- agents/
|   `-- openai.yaml          # Codex UI 展示与默认提示词
`-- references/
    |-- plan.md              # 只读调查与实施方案标准
    |-- build.md             # 范围内实现、验证与交付边界
    |-- review.md            # 只读审查、证据和 findings 标准
    `-- fix.md               # Goal、修复和多 Agent 对抗复审循环
```

`SKILL.md` 每次只路由到一个模式 reference，避免把无关流程同时载入上下文。调整模式规则时，应把共享约束留在 `SKILL.md`，把仅属于单一模式的细节留在对应 reference，并使用 Codex 自带的 `skill-creator` 校验 Skill 结构。

## 可见性与授权

本仓库当前为私有仓库，尚未附带开源许可证。将来若要公开发布，应先明确授权方式并补充对应 LICENSE；获得仓库访问权限本身不等于获得重新分发许可。
