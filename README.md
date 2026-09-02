# cyh-flow

面向 Codex、同时兼容 Claude Code 的跨项目软件交付工作流 Skill。Codex 是优先宿主，两端共用同一套模式、授权边界与仓库台账；宿主能力不等价时使用明确降级，不把 Codex 的 Goal API 或 Agent mailbox 虚构成 Claude Code 的同名能力。它用于方案设计、代码实现、无人值守构建与收敛、只读审查、一次性修复、持续收敛，以及带截图证据的长期任务池，避免“先看看”被误解为直接改代码，也避免一次实现请求被自动扩大成提交、推送或部署。

```text
用户请求
   |
   +-- plan   -> 只读调查 -> 统一需求方案文档 -> 可执行方案
   +-- build  -> 多 Agent 实现/验证 -> 普通：问题/决策点即停；auto：AI 决策 + 台账后继续
   +-- auto   -> build auto 跑到底 -> converge 所有适用 Review/测试 -> finding 归零
   +-- review -> 冻结快照 -> 四路举证 + 主预检并行 -> 主动证伪裁决 -> 立即交付
   +-- fix      -> 修复一个明确问题 -> 针对性验证
   +-- converge -> Goal: 复查/测试 -> 修复 -> 重验 -> finding 归零
   +-- task-add -> 分析一批事项 -> 按天归档 Markdown + 截图
   `-- task-run -> Agent 原子领取 -> 自主处理 -> done / waiting
```

## 八种模式

| 模式 | 适合处理 | 默认允许 | 默认不允许 |
| --- | --- | --- | --- |
| `plan` | 统一定义需求行为、实现方式和验收路径 | 多个只读 sub-Agent 并行调查代码、契约、数据、测试和平台面；主 Agent 单写一份同时承担 Spec 与 Plan 职责的需求 `.md` | 子 Agent 写应用代码或竞争写需求文档、把同一需求拆成多份决策文档、建分支、提交、推送、部署或更新外部系统 |
| `build` | 实现明确需求、计划、Issue 或产品变更；`auto` 由 AI 自动决策并持续执行 | 在约定范围内修改本地文件，尽可能拆分多 Agent 实现/验证并运行验收；auto 建立 Goal，把中间问题和自动决策写入本地台账供人工 Review | Build 内启动代码 Review、普通 build 遇到问题或决策点后继续、auto 擅自扩大范围或执行高风险操作、未经明确要求的提交、推送、PR、部署、生产写入或对外消息 |
| `auto` | 无人值守完成明确实现，并把结果收敛到所有适用 Review 和测试通过 | 串行建立 Build 与 Converge 两个 Goal，先按 `build auto` 完成实现，再以四路 Review、项目既有自动化检查及受影响平台流程为必需证据持续修复和重验 | 跳过必需证据、并行运行两个 Goal、未经明确要求的提交、推送、PR、部署、生产或外部写入、破坏性操作 |
| `review` | 审查工作区、分支、提交或 Pull Request，判断是否以最优实现覆盖完整关联面 | GitHub PR 先用已认证 `gh` 解析精确远端 SHA，本地 checkout 不适合时自动改用系统临时目录中的隔离 clone；随后用确定性脚本冻结目标，四路收集满足准入门槛的候选证据，主审逐条尝试证伪后才定结论；用户显式给出他人 GitHub PR 链接时，完整 Review 后自动发布并回读一次普通 PR 评论 | 因本地脏工作树或无关分支阻塞远端 PR Review、为了 Review 切换当前 checkout、把静态怀疑直接升级为 finding、用 reviewer 数量提高置信度、直接修复、自动等待或重跑、提交、推送、批准、请求修改、Resolve thread、Merge，或对本人 PR、推断目标和不完整 Review 自动发评论 |
| `fix` | 一次性修复明确 bug、失败行为或 Review finding | 多个只读 sub-Agent 并行定位根因、契约和验证面，由一个写者完成范围内修复与针对性验证 | 多写者竞争修复、自动扩大为长期 Goal、未经明确要求的提交、推送、PR、部署或外部写入 |
| `converge` | 持续发现、修复并复查问题，直到目标范围内 finding 归零 | 建立 Goal 和 finding 台账，把用户定义的 Review、自动化测试、设备、Web、运行时、安全或性能证据通道尽可能拆给并行 sub-Agent，由一个写者修复 | 多修复写者竞争、未经明确要求的提交、推送、PR、部署、生产写入或对外消息 |
| `task-add` | 批量收录 bug、小改动、杂项或后续工作 | 多个只读 sub-Agent 拆分事项和截图证据，主 Agent 去重后单写 `.cyh-flow/tasks/YYYY-MM-DD.md` 并原样保存截图 | 子 Agent 修改应用代码、竞争写任务池、领取或处理任务、提交、推送或外部写入 |
| `task-run` | 多 Agent 独立领取并处理任务池 | 以 Markdown 状态为准原子领取不同任务，修改前执行确定性文件/资源冲突闸门，再完成本地修改和验证 | 抢占 `doing` 任务、绕过领取或冲突闸门直接处理、未经明确要求的交付或外部写入 |

八种模式全部采用 sub-Agent 优先：先拆依赖和可独立任务，尽早使用最大有效并发，并在槽位释放后持续补位；只有阶段确实不可再分或拆分成本明显超过收益时才由单 Agent 直接完成。并行不会扩大模式权限，多个写者不得碰重叠文件或 Git 状态，也不得同时操作同一浏览器、模拟器、设备、数据库、缓存、构建输出或外部环境。八种模式同时共享几条硬边界：永不 Merge PR；不擅自丢弃或覆盖用户工作；破坏性 Git 操作必须先说明精确目标和损失范围；源码检查、自动化测试、CI、部署运行时、UI/设备证据与业务验收分别报告，不能互相替代。

`converge` 中的“finding 归零”是一个可验证停止条件，不是只重复代码 Review：finding 可以来自四路审查、自动化检查、模拟器或真机流程、Web 流程、运行时日志、安全、性能和业务验收。证据通道的决定权属于用户，你可以要求“只 Review”“只测指定浏览器流程”“模拟器 + Web”，也可以在过程中增加、替换或移除通道；Agent 必须把变更记录为 Goal 证据契约的修订，不能拿其他证据替代，也不能擅自增加阻塞通道。只有当你没有指定或明确把选择权交给 Agent 时，Agent 才会先声明一个与风险相称的最小组合，建议项只有经你接受后才成为完成门槛。任一用户必需通道中的受支持 finding、失败或重大未验证项都会阻止 Goal 完成，最终修复后必须重跑被影响的必需通道。它不表示对软件做“绝对无 bug”的不可证明承诺。

顶层 `auto` 是这个证据选择规则的显式例外：显式调用 `cyh-flow auto` 就表示把选择权交给 Agent，并要求“所有适用的 Review 和测试”，其中四路代码 Review 与主复查固定必需，同时从项目文档、CI 配置、包脚本、构建文件和影响面推导单元、集成、E2E、类型、Lint、Build、契约、迁移、浏览器、模拟器、设备、安全、性能等适用通道。适用性由变更影响和项目契约决定，不由当前环境能否执行决定；当前授权内可安全执行的通道直接跑，适用但缺少环境或权限的通道会让流水线保持未完成并说明阻塞，不能悄悄跳过，也不会为了跑全而自行 push 触发远端 CI、修改外部环境或碰生产。

## 安装

### Skill Manager

在 [Skill Manager](https://github.com/cyh-skill/skill-manager) 中导入本仓库 URL：

```text
https://github.com/cyh-skill/cyh-flow
```

这是一个高频基础工作流，通常适合选择“托管直装”；如果只想在少数任务中使用，也可以放进 Lazy 冷库，由 `skill-router` 按需加载。

### Codex 手动安装

仓库为公开仓库，可直接克隆到 Codex Skill 目录：

```bash
gh repo clone cyh-skill/cyh-flow ~/.agents/skills/cyh-flow
```

更新已有安装：

```bash
git -C ~/.agents/skills/cyh-flow pull --ff-only
```

新开 Codex 会话后即可发现该 Skill。

### Claude Code 插件安装（推荐）

仓库提供 Claude Code 插件清单和一个显式调用 wrapper，可直接在 Claude Code 中添加 marketplace 并安装插件：

```text
/plugin marketplace add cyh-skill/cyh-flow
/plugin install cyh-flow@cyh-flow
```

插件的规范调用名是 `/cyh-flow:cyh-flow`；不要依赖可能因其他插件而歧义的裸别名。开发本地 checkout 时可用 `claude --plugin-dir /absolute/path/to/cyh-flow` 加载，并在可用的 Claude Code CLI 中运行 `claude plugin validate /absolute/path/to/cyh-flow --strict`。

### Claude Code 个人 Skill

不使用插件系统时，也可把仓库克隆到个人 Skill 目录：

```bash
gh repo clone cyh-skill/cyh-flow ~/.claude/skills/cyh-flow
```

个人 Skill 的调用名是 `/cyh-flow`。插件 wrapper 通过 `disable-model-invocation: true` 在宿主层强制仅用户调用；个人 Skill 仍受根 `SKILL.md` 的显式调用契约约束，但若需要宿主级硬限制，应优先使用插件安装。

## 使用

Codex 显式调用使用 `$cyh-flow`；它是 Skill 名称，不是 shell 命令，也不是 `/` 开头的 Codex 宿主命令：

```text
$cyh-flow plan 给结账流程增加批量确认，先分析影响并出方案

$cyh-flow build 按 Issue #123 实现，并运行相关测试；不要提交或推送

$cyh-flow build auto 按 docs/plans/checkout.md 执行方案，由 AI 自动决策，记录问题和决定供我之后 Review

$cyh-flow auto 按 docs/plans/checkout.md 无人值守完成实现，然后跑完所有适用 Review 和测试直到 finding 归零

$cyh-flow review PR #456，只做 review，不修改代码

$cyh-flow fix 修复 Review 发现的并发问题，并运行针对性回归测试

$cyh-flow converge 持续检查结账流程直到 finding 归零；证据通道：四路 Review、iOS 模拟器、结账 Web 流程

$cyh-flow task-add 把下面这批 bug 和小改动分析后收进任务池

$cyh-flow task-run 并发处理任务池里所有可执行事项，有问题集中问我
```

Claude Code 插件安装后使用规范命名空间，个人 Skill 安装则使用短名：

```text
/cyh-flow:cyh-flow plan 给结账流程增加批量确认，先分析影响并出方案
/cyh-flow:cyh-flow auto 按 docs/plans/checkout.md 完成实现与全证据收敛

# 仅限个人 Skill 安装
/cyh-flow review PR #456，只做 review，不修改代码
```

cyh-flow 被设置为仅显式调用：普通的自然语言 plan、build、auto、review、fix、converge、task-add 或 task-run 请求不会自动进入这套流程。Codex 需要用户输入 `$cyh-flow ...` 或主动选择该 Skill；Claude Code 插件 wrapper 使用 `disable-model-invocation: true`，需要用户输入 `/cyh-flow:cyh-flow ...`。显式调用后，一次性修复明确问题属于 `fix`；只有明确要求跨轮复查和修复、模拟器或 Web 验收循环，或“直到 finding 归零”时才进入 `converge`；只有顶层 `cyh-flow auto` 会把 `build auto` 与全证据 `converge` 串起来。若一句话混合了多个模式，cyh-flow 会保留每个阶段的权限边界：方案不会自动进入实现，审查不会自动变成修复，task-add 不会自动处理刚收录的事项，任何本地实现或修复也不会自动进入交付。

## 双宿主能力映射

| 契约 | Codex | Claude Code | 兼容降级 |
| --- | --- | --- | --- |
| 显式入口 | `$cyh-flow ...` | 个人 Skill `/cyh-flow ...`；插件 `/cyh-flow:cyh-flow ...` | 文档中的 `cyh-flow` 表示当前宿主的对应入口 |
| Goal | 原生 create/get/update Goal API | 用户自行启用的 `/goal <condition>`：session-scoped、单 active、替换语义、基于 Stop hook | 两者不作 API 等价声明；可用时由 Task 工具记录当前阶段，`.cyh-flow` 台账始终承担可恢复事实源 |
| 独立工作者 | Agent 与 addressable follow-up | 标准 `Agent`；只有用户已启用实验性 Agent Teams 时才使用 `SendMessage`/共享团队协调 | 无可寻址 follow-up 时先收齐四路 specialist，再启动 fresh master；无并发时保持隔离并顺序执行 |
| 项目规则 | `AGENTS.md` | `CLAUDE.md` 及宿主加载的项目规则 | 读取当前宿主和项目实际存在的规则，不伪造统一优先级 |
| 浏览器 Skill | `browser-skill:cyh-browser-skill` | `/browser-skill:cyh-browser-skill` | 未安装则将所需浏览器证据标记为 blocked，不换用其他自动化体系 |

Claude Code 的原生 `/goal` 只能由用户激活，cyh-flow 不会替换已有 goal，也不会把它描述成 Codex Goal API。Claude Code 的 plan permission mode 适合 `cyh-flow plan` 的只读调查，但写唯一需求方案文档前必须切回可编辑模式；Claude Code 原生 `/review` 也不是 `cyh-flow review` 的别名。实验性 Agent Teams 不属于安装前提，Skill 不会自行更改设置或启用它。

Plan 阶段会把所有已经确认的需求决策写入同一份 Markdown 文档。这份文档不是并列维护 Spec 和 Plan 两块内容，而是把两者的职责融合起来，围绕用户流程、能力、规则和决策同时说明预期行为、边界与验收标准，以及对应的实现方式、影响范围、步骤和验证。先按 Issue、需求标识、标题和内容检索已有文档，同一需求始终原地更新，不拆成 `*-spec.md` 与 `*-plan.md`，也不因新会话、补充讨论或方案迭代创建日期版、`v2` 或其他副本。项目有既定目录和命名时沿用；没有时使用 `docs/plans/<requirement-slug>.md`。跨仓库需求也只维护一份主文档，其他位置只链接，不复制维护。

Build 是纯执行模式，不会在实现中调用四路代码 Review 或主复查。普通 `build` 和 `build auto` 都执行用户要求的完整范围，都会先拆解依赖，并在文件所有权和运行环境不冲突的前提下尽可能并行调度多 Agent 做实现和验证；真正区别是普通 build 遇到第一个实质性意外问题或需要取舍的决策点就停止修改和派发并向用户汇报，而显式 auto 会把范围内决策权交给主 Agent，由它根据需求、仓库证据、既有模式、兼容性和风险选择最佳方案，再继续安全修复或推进不受影响的任务。auto 会建立一个逻辑 Goal 契约，并把每个问题及自动决策写入 `.cyh-flow/build/<goal-slug>.md`：Codex 可用原生 Goal API 承载它；Claude Code 只在用户已启用匹配 `/goal` 时借助其 session loop，并可用 Task 工具镜像实时阶段。台账记录候选方案、最终选择、依据、影响、可逆性、相关文件和验证结果，默认标记为 `pending` 供人工 Review，不能冒充用户已经接受。该人工 Review 是执行后的审计交接，不会阻塞 build；若用户把人工接受明确设为 Goal 门槛则例外。范围扩大、外部写入、不可逆或高风险操作仍需另行授权；台账默认不提交，commit、push、PR 和部署也仍需单独明确授权。

顶层 `cyh-flow auto` 不是 `build auto` 的别名，而是无人值守的阶段编排：用 `.cyh-flow/auto/<goal-slug>.md` 记录唯一阶段事实，先完成 Build 逻辑 Goal，再冻结实现结果并进入 Converge 逻辑 Goal。Codex 顺序使用两个原生 Goal；Claude Code 使用一个可选的用户 `/goal`、两个逻辑阶段记录与同一编排台账，不声称存在两个可寻址 native Goal。Converge 阶段以一个互斥修复写者配合并行只读证据 Agent，任何修复都会使受影响的旧证据失效，最终必须在最新冻结目标上重跑。日常工程取舍无需人工确认，但范围变化、新权限、不可逆动作、外部写入、必需环境缺失或无法由仓库证据安全决定的产品问题仍会阻塞流水线。

任务池是独立流水线：`task-add` 把一批 bug、小改动或其他事项分析后写入首次收录日期对应的 Markdown，并自动收集当前收录批次中的用户截图，不需要用户额外说“保留截图”；截图原样保存在 `.cyh-flow/tasks/assets/<TASK-ID>/` 并以内嵌相对链接展示，只有用户明确要求跳过时才不保存。`task-run` 不依赖主 Agent，每个 Agent 都用唯一身份对任务文档执行一次极短的加锁、重读和状态更新，只有把 `pending` 成功写成 `doing` 并留下领取人和时间后才能继续；在修改任何文件或共享运行时资源前，还必须重读全部 `doing` 任务并执行冲突闸门，冲突时由较早 claim（同时间则较小 task ID）继续，其他任务转为 `waiting`。锁不保存任何业务信息，Markdown 始终是状态和归属的唯一事实来源；`doing` 任务不会被自动抢占，完成后改成 `done`，需要用户决定时改成 `waiting` 并保留问题和处理历史。

## 工作原则

- 先确认真实仓库、工作树、分支、子模块或 worktree，再开始调查或修改。
- 优先读取项目自己的 `AGENTS.md`、`CLAUDE.md` 和文档；项目规则比通用工作流更具体时，以项目规则为准。
- 存在 `.codegraph/` 且 CodeGraph 可用时，优先用它理解架构、依赖和调用路径。
- GitHub 操作默认使用已认证的 `gh`，并在依赖实时状态时重新读取 PR、检查和远端引用。
- 浏览器自动化固定使用已安装的 `cyh-browser-skill`：Codex 入口为 `browser-skill:cyh-browser-skill`，Claude Code 插件入口为 `/browser-skill:cyh-browser-skill`；普通公开网页检索使用宿主常规搜索能力。
- 八种模式都优先把独立工作拆给 sub-Agent 并填满有效并发；协调者负责权限、依赖、冲突控制和结果整合，具体单写者或多写者拓扑以各模式 reference 为准。
- 目标是满足真实需求与仓库约束的最优实现，不是最少行数或最小 diff；正确性、安全、数据完整性、兼容性等硬约束满足后，再综合复用程度、架构契合、清晰度、可测试性、可维护性、性能和变更范围作选择。
- Review 会从变更根节点向上追约束、向下追消费者、横向查共享不变量和替代路径，并让 Codex correctness、Ponytail complexity、Differential security、Performance engineer 四路在隔离上下文中审查同一冻结目标。GitHub PR 以 `gh` 返回的远端 base/head SHA 为准；当前工作树脏、有无关分支或没有 PR 分支时，协调者会自动复用精确对象或创建一次隔离临时 clone，不切换用户 checkout，也不会给每个 reviewer 重复 clone。第一轮只准入能证明本轮引入、真实可达、符合权威契约和范围决定、修复责任边界明确的候选，其余进入无严重级别和修法的 open questions；有足够槽位时独立主 Agent 同步完成事实型需求和影响面预检，四路结果到齐后忽略原始定级与修法，主动从状态生产者、跨端执行边界、角色组合、历史决定和替代路径逐条寻找反证，再决定 verified、known deferred、rejected 或 unresolved。每个阶段批量执行独立读取与检查，共享静态证据只生成一次；实时工作树后来变化只会产生漂移提示，不会扣住已经完成的冻结快照结论或自动重跑。用户显式给出他人 GitHub PR URL 时，review 完成且最终快照校验通过后会用 `gh` 自动发布一次普通评论并回读确认；正文带目标和内容指纹以避免不确定重试造成重复评论，但不会自动 Approve、Request changes、Resolve thread 或 Merge。一行代码只是可能的结果，不是目标。
- Plan 的最终答复必须给出统一需求方案文档路径及其就绪状态；最终答复先给结论，再说明证据、未完成验证和仍需用户授权的下一步。

四路人格分别适配自 [OpenAI Codex review rubric](https://github.com/openai/codex/blob/main/codex-rs/prompts/templates/review/rubric.md)、[Ponytail review](https://github.com/DietrichGebert/ponytail/tree/main/skills/ponytail-review)、[Trail of Bits differential-review](https://github.com/trailofbits/skills/tree/main/plugins/differential-review) 和 [performance-testing-review 的 performance engineer](https://github.com/wshobson/agents/tree/main/plugins/performance-testing-review)。上游链接提供真实方法来源，仓库内 adapter 统一冻结目标、只读边界、候选准入和输出契约；主复查不按投票决定，也不继承第一轮的严重级别和修法，而是主动证伪可达性、权威契约、范围决定、影响与责任边界后再给最终 P0-P3、known deferred、advisory、rejected 或 unresolved 结论。

## 仓库结构

```text
cyh-flow/
|-- SKILL.md                 # Skill 入口、模式路由和共享边界
|-- .claude-plugin/
|   |-- plugin.json          # Claude Code 插件清单
|   `-- marketplace.json     # 可直接添加的单插件 marketplace
|-- agents/
|   `-- openai.yaml          # Codex UI 展示与默认提示词
|-- claude/skills/cyh-flow/
|   `-- SKILL.md             # Claude 显式调用 wrapper 与宿主降级入口
|-- scripts/
|   |-- review_snapshot.py   # 冻结、验证并比较实时 Review 目标
|   `-- task_pool.py         # Markdown 任务入池、原子领取与状态更新
|-- tests/
|   |-- test_host_compat.py  # 双宿主 manifest、入口与链接契约
|   |-- test_review_snapshot.py # 快照复现、漂移隔离与破坏检测
|   `-- test_task_pool.py    # 截图保留、并发领取和状态流转验证
`-- references/
    |-- plan.md              # 只读调查与统一需求方案文档标准
    |-- build.md             # 多 Agent 执行、普通停止策略与 auto AI 决策审计台账
    |-- auto.md              # build auto 到全证据 converge 的无人值守编排
    |-- review.md            # 不可变快照、四路并行、重叠主复查与 clean gate
    |-- review/              # 公共契约、四种 reviewer 人格与主复查角色
    |-- fix.md               # 一次性问题修复与针对性验证
    |-- converge.md          # Goal、跨证据通道复查与 finding-zero 收敛
    |-- task-add.md          # 按天归档任务和用户截图
    `-- task-run.md          # 无主调度的原子领取与自主处理
```

`SKILL.md` 是两端唯一规范入口，每次先路由到一个主模式 reference，避免把无关流程同时载入上下文；Claude wrapper 只适配调用和宿主能力，不复制八种模式。普通 `fix` 或 `converge` 只有在用户证据通道明确要求四路 Review 时才继续按需读取 Review 协议，而顶层 `auto` 按阶段顺序读取 Build、Converge 和 Review 协议。调整模式规则时，应把共享约束留在 `SKILL.md`，把仅属于单一模式的细节留在对应 reference，并使用官方 `skill-creator` 校验根 Skill、用测试校验两端 manifest、入口和相对链接；有真实 Claude Code CLI 的环境还应运行 `claude plugin validate . --strict`。

## 可见性与授权

本仓库公开可读，但尚未附带开源许可证；公开访问不等于获得复制、修改或重新分发许可。若需要按开源方式使用，应先由仓库所有者明确许可并补充对应 LICENSE。
