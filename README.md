# cyh-flow

面向 Codex、同时兼容 Claude Code 的跨项目软件交付工作流 Skill。Codex 是优先宿主，两端共用同一套模式、授权边界与仓库台账；宿主能力不等价时使用明确降级，不把 Codex 的 Goal API 或 Agent mailbox 虚构成 Claude Code 的同名能力。它用于方案设计、代码实现、无人值守构建与收敛、一次性或无人值守 PR 审查、既有 Review 问题验收、一次性修复、持续收敛，以及带截图证据的长期任务池，避免“先看看”被误解为直接改代码，也避免一次实现请求被自动扩大成提交、推送或部署。

```text
用户请求
   |
   +-- plan   -> 只读调查 -> 统一需求方案文档 -> 可执行方案
   +-- build  -> 多 Agent 实现/验证 -> 普通：问题/决策点即停；auto：AI 决策 + 台账后继续
   +-- auto   -> build auto 跑到底 -> converge 所有适用 Review/测试 -> finding 归零
   +-- review    -> 日常单 reviewer；deep：四路 specialist + 主审证伪；auto：单 reviewer 跟进 PR
   +-- re-review -> 逐条验收既有 Review 问题 -> 自动回贴 PR
   +-- fix      -> 修复一个明确问题 -> 针对性验证
   +-- converge -> Goal: 复查/测试 -> 修复 -> 重验 -> finding 归零
   +-- task-add -> 分析一批事项 -> 按天归档 Markdown + 截图
   `-- task-run -> Agent 原子领取 -> 自主处理 -> done / waiting
```

## 九种模式

| 模式 | 适合处理 | 默认允许 | 默认不允许 |
| --- | --- | --- | --- |
| `plan` | 统一定义需求行为、实现方式和验收路径 | 多个只读 sub-Agent 并行调查代码、契约、数据、测试和平台面；主 Agent 单写一份同时承担 Spec 与 Plan 职责的需求 `.md` | 子 Agent 写应用代码或竞争写需求文档、把同一需求拆成多份决策文档、建分支、提交、推送、部署或更新外部系统 |
| `build` | 实现明确需求、计划、Issue 或产品变更；`auto` 由 AI 自动决策并持续执行 | 在约定范围内修改本地文件，尽可能拆分多 Agent 实现/验证并运行验收；auto 建立 Goal，把中间问题和自动决策写入本地台账供人工 Review | Build 内启动代码 Review、普通 build 遇到问题或决策点后继续、auto 擅自扩大范围或执行高风险操作、未经明确要求的提交、推送、PR、部署、生产写入或对外消息 |
| `auto` | 无人值守完成明确实现，并把结果收敛到所有适用 Review 和测试通过 | 串行建立 Build 与 Converge 两个 Goal，先按 `build auto` 完成实现，再显式以 `review deep`、项目既有自动化检查及受影响平台流程为必需证据持续修复和重验 | 跳过必需证据、并行运行两个 Goal、未经明确要求的提交、推送、PR、部署、生产或外部写入、破坏性操作 |
| `review` | 日常审查工作区、分支、提交或 Pull Request；`review deep` 执行多 Agent 深审；`review auto` 无人值守跟进 GitHub PR | 普通和 auto 每轮只用一个五轴 reviewer；deep 才运行四个 specialist 与 fresh master；GitHub PR 统一通过已认证 `gh` 一次缓存原始证据，只为具体候选运行最小复现并用脚本幂等发布评论 | 普通或 auto 偷启多 Agent，跑完整单测、全量 lint/typecheck/build/E2E 或等待 CI，把这些当作 review gate，冻结或锁定 PR，为 Review 切换当前 checkout，直接修复、提交、推送、Approve、Request changes、Resolve thread 或 Merge |
| `re-review` | 验收同事后续改动是否逐条解决 PR 上已有的可执行 Review 问题 | 一个 fresh acceptance reviewer 从完整评论、review、inline thread 和提交历史建立问题清单，逐项验证当前代码与直接回归；证据闭合后自动发布一条带 head 指纹的普通 PR 评论 | 把 thread resolved、回复 fixed、绿 CI 或代码改过当作解决证明，扩展成无关的新一轮全量 Review，修改代码、Approve、Request changes、Resolve thread、持续监控或 Merge |
| `fix` | 一次性修复明确 bug、失败行为或 Review finding | 多个只读 sub-Agent 并行定位根因、契约和验证面，由一个写者完成范围内修复与针对性验证 | 多写者竞争修复、自动扩大为长期 Goal、未经明确要求的提交、推送、PR、部署或外部写入 |
| `converge` | 持续发现、修复并复查问题，直到目标范围内 finding 归零 | 建立 Goal 和 finding 台账，把用户定义的 Review、自动化测试、设备、Web、运行时、安全或性能证据通道尽可能拆给并行 sub-Agent，由一个写者修复 | 多修复写者竞争、未经明确要求的提交、推送、PR、部署、生产写入或对外消息 |
| `task-add` | 批量收录 bug、小改动、杂项或后续工作 | 多个只读 sub-Agent 拆分事项和截图证据，主 Agent 去重后单写 `.cyh-flow/tasks/YYYY-MM-DD.md` 并原样保存截图 | 子 Agent 修改应用代码、竞争写任务池、领取或处理任务、提交、推送或外部写入 |
| `task-run` | 多 Agent 独立领取并处理任务池 | 以 Markdown 状态为准原子领取不同任务，修改前执行确定性文件/资源冲突闸门，再完成本地修改和验证 | 抢占 `doing` 任务、绕过领取或冲突闸门直接处理、未经明确要求的交付或外部写入 |

九种模式全部采用与任务相称的 sub-Agent 拓扑：普通 `review`、`review auto` 和 `re-review` 固定一个 reviewer，`review deep` 才使用四路 specialist 与 fresh master，其他模式先拆依赖和可独立任务并使用最大有效并发；只有阶段确实不可再分或拆分成本明显超过收益时才由单 Agent 直接完成。并行不会扩大模式权限，多个写者不得碰重叠文件或 Git 状态，也不得同时操作同一浏览器、模拟器、设备、数据库、缓存、构建输出或外部环境。九种模式同时共享几条硬边界：永不 Merge PR；不擅自丢弃或覆盖用户工作；破坏性 Git 操作必须先说明精确目标和损失范围；源码检查、自动化测试、CI、部署运行时、UI/设备证据与业务验收分别报告，不能互相替代。

`converge` 中的“finding 归零”是一个可验证停止条件，不是只重复代码 Review：finding 可以来自普通单 reviewer、`review deep`、自动化检查、模拟器或真机流程、Web 流程、运行时日志、安全、性能和业务验收。证据通道的决定权属于用户，你可以要求“只 Review”“只测指定浏览器流程”“模拟器 + Web”，也可以在过程中增加、替换或移除通道；Agent 必须把变更记录为 Goal 证据契约的修订，不能拿其他证据替代，也不能擅自增加阻塞通道。只有当你没有指定或明确把选择权交给 Agent 时，Agent 才会先声明一个与风险相称的最小组合，建议项只有经你接受后才成为完成门槛。任一用户必需通道中的受支持 finding、失败或重大未验证项都会阻止 Goal 完成，最终修复后必须重跑被影响的必需通道。它不表示对软件做“绝对无 bug”的不可证明承诺。

顶层 `auto` 是这个证据选择规则的显式例外：显式调用 `cyh-flow auto` 就表示把选择权交给 Agent，并要求“所有适用的 Review 和测试”，其中 `review deep` 的四路代码审查与主复查固定必需，同时从项目文档、CI 配置、包脚本、构建文件和影响面推导单元、集成、E2E、类型、Lint、Build、契约、迁移、浏览器、模拟器、设备、安全、性能等适用通道。适用性由变更影响和项目契约决定，不由当前环境能否执行决定；当前授权内可安全执行的通道直接跑，适用但缺少环境或权限的通道会让流水线保持未完成并说明阻塞，不能悄悄跳过，也不会为了跑全而自行 push 触发远端 CI、修改外部环境或碰生产。

`review auto` 与顶层 `auto` 不同：它不实现或修复代码，只把普通单 reviewer 审查套在无人值守事件循环外层，不调用 deep 的四路与 Master。首轮 Review 前先启动 `skills/cyh-flow/scripts/review_watch.py`，由这个纯 Python 进程每约 30 秒通过 `gh` 查询 head SHA 和人工 Issue/Review/inline 评论，不轮询 Checks；它在安静期间不输出，只有检测到事件或连续失败才返回一条结构化 JSON，因此 GitHub 查询和差分本身不消耗 AI token，宿主若必须定期续接长运行进程则仍会有很小的句柄续等开销。每轮由 `review_prepare.py` 机械缓存一次原始 PR 内容与临时源码对象，一个 fresh reviewer 完成五轴检查，`review_publish.py` 一次完成评论指纹、查重、发布和回读。新的提交一定触发下一轮，人工讨论先唤醒 Agent 判断是否影响需求、范围、实现证据或 finding 状态；自己的带指纹评论和 bot 评论不会触发循环。只有最新完整轮次达到 `Review-ready` 且 watcher 没有未处理事件，或者用户明确说“结束/停止”，Goal 才结束；没有新动静、查询暂时失败或 Review 不完整都不算完成，CI pending 或失败只作为观察信息，不单独阻止 Review-ready。脚本只随承载它的执行进程存活，跨会话常驻仍需 Scheduled task、launchd、CI 或 webhook，Skill 不会谎称子进程已经变成后台服务。

`re-review` 是一次性验收模式，不启动 watcher，也不重新寻找与原 Review 无关的问题。它从 PR 的人工评论、formal review、inline thread 和用户明确给出的 finding 中去重建立完整问题清单，再逐项判断 `Resolved`、`Outstanding`、`Obsolete` 或 `Unverified`，并检查修复触及行为的直接回归。只有清单证据闭合后才自动发布；全部解决与仍有遗留都会回贴 PR，基线或关键证据不足的 `Incomplete` 不会发布误导性结论。发布使用独立且绑定当前 head 的 re-review marker，因此重复执行不会重复发同一结果，也不会与普通或 auto review 的评论指纹冲突。

## 安装

### Skill Manager

在 [Skill Manager](https://github.com/cyh-skill/skill-manager) 中导入本仓库 URL：

```text
https://github.com/cyh-skill/cyh-flow
```

这是一个高频基础工作流，通常适合选择“托管直装”；如果只想在少数任务中使用，也可以放进 Lazy 冷库，由 `skill-router` 按需加载。

### Codex 手动安装

仓库根目录同时承载 Claude 插件包装；Codex 只安装 `skills/cyh-flow/` 这个独立 Skill 目录，避免把插件名再次拼进界面调用名：

```bash
gh repo clone cyh-skill/cyh-flow ~/.local/share/cyh-flow
mkdir -p ~/.agents/skills
ln -s ~/.local/share/cyh-flow/skills/cyh-flow ~/.agents/skills/cyh-flow
```

更新已有安装：

```bash
git -C ~/.local/share/cyh-flow pull --ff-only
```

新开 Codex 会话后即可发现该 Skill。

### Claude Code 插件安装（推荐）

仓库提供 Claude Code 插件清单，插件直接加载与 Codex 共用的 `skills/cyh-flow/SKILL.md`，可在 Claude Code 中添加 marketplace 并安装：

```text
/plugin marketplace add cyh-skill/cyh-flow
/plugin install cyh-flow@cyh-flow
```

插件的规范调用名是 `/cyh-flow:cyh-flow`；不要依赖可能因其他插件而歧义的裸别名。开发本地 checkout 时可用 `claude --plugin-dir /absolute/path/to/cyh-flow` 加载，并在可用的 Claude Code CLI 中运行 `claude plugin validate /absolute/path/to/cyh-flow --strict`。

### Claude Code 个人 Skill

不使用插件系统时，也只把同一个独立 Skill 目录链接到个人 Skill 目录：

```bash
gh repo clone cyh-skill/cyh-flow ~/.local/share/cyh-flow
mkdir -p ~/.claude/skills
ln -s ~/.local/share/cyh-flow/skills/cyh-flow ~/.claude/skills/cyh-flow
```

个人 Skill 的调用名是 `/cyh-flow`。两个宿主共享 `skills/cyh-flow/SKILL.md`：Codex 通过同目录下的 `agents/openai.yaml` 在宿主层禁止隐式调用，Claude Code 读取同一入口中的显式调用契约和 `$ARGUMENTS`。为了保持 Skill 符合跨宿主 Agent Skills 格式，不在其中加入 Claude 专用 frontmatter。

## 使用

Codex 显式调用使用 `$cyh-flow`；它是 Skill 名称，不是 shell 命令，也不是 `/` 开头的 Codex 宿主命令：

```text
$cyh-flow plan 给结账流程增加批量确认，先分析影响并出方案

$cyh-flow build 按 Issue #123 实现，并运行相关测试；不要提交或推送

$cyh-flow build auto 按 docs/plans/checkout.md 执行方案，由 AI 自动决策，记录问题和决定供我之后 Review

$cyh-flow auto 按 docs/plans/checkout.md 无人值守完成实现，然后跑完所有适用 Review 和测试直到 finding 归零

$cyh-flow review PR #456，只做 review，不修改代码

$cyh-flow review deep PR #456，使用四路 specialist 和 fresh master 深度审查

$cyh-flow review auto https://github.com/acme/payments/pull/456，无人值守审查并把问题发到 PR

$cyh-flow re-review https://github.com/acme/payments/pull/456，验证同事是否解决全部 Review 问题并自动回贴 PR

$cyh-flow fix 修复 Review 发现的并发问题，并运行针对性回归测试

$cyh-flow converge 持续检查结账流程直到 finding 归零；证据通道：review deep、iOS 模拟器、结账 Web 流程

$cyh-flow task-add 把下面这批 bug 和小改动分析后收进任务池

$cyh-flow task-run 并发处理任务池里所有可执行事项，有问题集中问我
```

Claude Code 插件安装后使用规范命名空间，个人 Skill 安装则使用短名：

```text
/cyh-flow:cyh-flow plan 给结账流程增加批量确认，先分析影响并出方案
/cyh-flow:cyh-flow auto 按 docs/plans/checkout.md 完成实现与全证据收敛
/cyh-flow:cyh-flow review deep PR #456
/cyh-flow:cyh-flow review auto https://github.com/acme/payments/pull/456
/cyh-flow:cyh-flow re-review https://github.com/acme/payments/pull/456

# 仅限个人 Skill 安装
/cyh-flow review PR #456，只做 review，不修改代码
```

cyh-flow 的契约是仅显式调用：普通的自然语言 plan、build、auto、review、re-review、fix、converge、task-add 或 task-run 请求不应自动进入这套流程。Codex 需要用户输入 `$cyh-flow ...` 或主动选择该 Skill，并由 `skills/cyh-flow/agents/openai.yaml` 强制执行；Claude Code 插件加载同一个 `skills/cyh-flow/SKILL.md`，用户以 `/cyh-flow:cyh-flow ...` 调用。显式调用后，`re-review` 只验收已有 Review 问题并自动回贴一次，一次性修复明确问题属于 `fix`；只有明确要求跨轮复查和修复、模拟器或 Web 验收循环，或“直到 finding 归零”时才进入 `converge`；只有顶层 `cyh-flow auto` 会把 `build auto` 与全证据 `converge` 串起来。若一句话混合了多个模式，cyh-flow 会保留每个阶段的权限边界：方案不会自动进入实现，审查不会自动变成修复，task-add 不会自动处理刚收录的事项，任何本地实现或修复也不会自动进入交付。

## 双宿主能力映射

| 契约 | Codex | Claude Code | 兼容降级 |
| --- | --- | --- | --- |
| 显式入口 | `$cyh-flow ...` | 个人 Skill `/cyh-flow ...`；插件 `/cyh-flow:cyh-flow ...` | 文档中的 `cyh-flow` 表示当前宿主的对应入口 |
| Goal | 原生 create/get/update Goal API | 用户自行启用的 `/goal <condition>`：session-scoped、单 active、替换语义、基于 Stop hook | 两者不作 API 等价声明；可用时由 Task 工具记录当前阶段；没有持续执行循环时，`review auto` 必须明确 blocked，不能声称仍在后台监控 |
| 独立工作者 | Agent 与 addressable follow-up | 标准 `Agent`；只有用户已启用实验性 Agent Teams 时才使用 `SendMessage`/共享团队协调 | 普通 review、review auto 和 re-review 固定一个 reviewer；deep 无可寻址 follow-up 时先收齐四路 specialist，再启动 fresh master，无并发时保持隔离并顺序执行 |
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
- 除普通 `review`、`review auto` 和 `re-review` 明确固定一个 reviewer 外，各模式都优先把独立工作拆给 sub-Agent 并填满有效并发；协调者负责权限、依赖、冲突控制和结果整合，具体拓扑以各模式 reference 为准。
- 目标是满足真实需求与仓库约束的最优实现，不是最少行数或最小 diff；正确性、安全、数据完整性、兼容性等硬约束满足后，再综合复用程度、架构契合、清晰度、可测试性、可维护性、性能和变更范围作选择。
- 普通 Review 由一个 fresh reviewer 在同一遍里检查 correctness、readability/simplicity、architecture、security 和 performance，并把 Required 与 Optional/Nit 分开；`review auto` 重复同一单 reviewer 周期并用确定性 watcher 管理轻量事件游标；`re-review` 用一个 fresh acceptance reviewer 逐项验收既有问题并自动发布闭合结果。只有 `review deep` 才让 Codex correctness、Ponytail complexity、Differential security、Integration reliability 四路在隔离上下文中独立解释机械缓存的完整原始材料，再由 fresh master 统一证伪、判断责任边界和 P0-P3。四种 review 都不把临时缓存当作不可变快照或锁，不会自动 Approve、Request changes、Resolve thread 或 Merge。
- Plan 的最终答复必须给出统一需求方案文档路径及其就绪状态；最终答复先给结论，再说明证据、未完成验证和仍需用户授权的下一步。

## 方法来源与致谢

Review 的角色设计参考并重新适配了以下公开项目；这里集中记录方法来源和许可背景，运行时角色文件只保留完成审查所需的职责、证据标准、边界和输出契约，不会为了这些来源链接联网或下载额外提示词：

- 日常五轴 reviewer 参考 Addy Osmani 的 MIT 许可 [code-review-and-quality Skill](https://github.com/addyosmani/agent-skills/blob/d2c37ef6225dd8726cdd369a8030307f48592d26/skills/code-review-and-quality/SKILL.md)，压缩保留 correctness、readability/simplicity、architecture、security、performance、结构性修法、验证故事和依赖纪律。
- Codex correctness 参考 [OpenAI Codex review rubric](https://github.com/openai/codex/blob/81de4f251cfdaf32ecb85e2160ebfc11a562d44b/codex-rs/prompts/templates/review/rubric.md) 的可操作缺陷标准。
- Ponytail complexity 参考 Dietrich Gebert 的 [ponytail-review Skill](https://github.com/DietrichGebert/ponytail/blob/bd6176a9b33ab72594ff82e6f34f17b085f25565/skills/ponytail-review/SKILL.md) 的减法式复杂度视角。
- Differential security 参考 Trail of Bits 的 [differential-review Skill](https://github.com/trailofbits/skills/blob/4b1b74b181e81cbcaa8d3b68a0e4ed867165b972/plugins/differential-review/skills/differential-review/SKILL.md)；fresh master 的基线、可达性、影响面和证据纪律也受其启发。
- Integration reliability 参考 MIT 许可的 [`code-reviewer` agent](https://github.com/wshobson/agents/blob/8df77ecd46ae10c3373e6a4b91b29859ef6b560d/plugins/comprehensive-review/agents/code-reviewer.md)，它来自 [`comprehensive-review` 插件](https://github.com/wshobson/agents/tree/8df77ecd46ae10c3373e6a4b91b29859ef6b560d/plugins/comprehensive-review)。

## 仓库结构

```text
cyh-flow/
|-- LICENSE                  # MIT 开源许可证
|-- .claude-plugin/
|   |-- plugin.json          # Claude Code 插件清单
|   `-- marketplace.json     # 可直接添加的单插件 marketplace
|-- skills/
|   `-- cyh-flow/            # Codex 独立 Skill；界面调用名为 $cyh-flow
|       |-- SKILL.md         # 模式路由和共享边界
|       |-- agents/
|       |   `-- openai.yaml  # Codex UI 展示与默认提示词
|       |-- scripts/         # Review watcher、PR 工件与任务池工具
|       `-- references/      # 九种模式和 Review 角色协议
|-- tests/
|   |-- test_host_compat.py  # 双宿主 manifest、入口与链接契约
|   |-- test_review_prepare.py   # PR 原始材料与共享源码缓存
|   |-- test_review_artifacts.py # deep specialist/master 工件与 clean gate
|   |-- test_review_publish.py   # PR 评论查重、发布与回读
|   |-- test_review_watch.py # watcher 事件过滤、游标和唤醒协议
|   `-- test_task_pool.py    # 截图保留、并发领取和状态流转验证
`-- README.md
```

`skills/cyh-flow/SKILL.md` 是两端唯一规范入口，Claude 插件清单指向这个子目录，Codex 和个人 Skill 安装也只暴露该目录，因此 Codex 只显示 `$cyh-flow`，不会再拼成 `$cyh-flow:cyh-flow`；普通 review 只读取单 reviewer 协议，`review deep` 才读取四路与 Master 协议，避免把深审上下文带进日常审查。普通 `fix` 或 `converge` 只有在用户证据通道明确要求 `review deep` 时才继续读取深审协议，而顶层 `auto` 按阶段顺序读取 Build、Converge 和 deep review。调整模式规则时，应把共享约束留在 `SKILL.md`，把仅属于单一模式的细节留在对应 reference，并使用官方 `skill-creator` 校验独立 Skill、用测试校验两端 manifest、入口和相对链接；有真实 Claude Code CLI 的环境还应运行 `claude plugin validate . --strict`。

## 可见性与授权

本仓库采用 [MIT License](LICENSE) 开源；版权归 `cyh-skill` 所有，使用、复制、修改和分发时请遵守许可证中的版权与许可声明保留要求。
