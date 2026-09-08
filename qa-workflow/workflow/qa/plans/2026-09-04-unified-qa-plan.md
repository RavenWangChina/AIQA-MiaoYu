# [公司] QA 工作流统一实施方案（rev2，经对抗审查修订）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把现有"单轮测试孤岛"升级为完整 QA 体系：双环转正（对抗+知识）、GIT/缺陷管理系统事件接口、覆盖面扩展、运营固化。

**Architecture:** 会话=任务单元（动态）/工作区=资产（静态）两层解耦；外部协调通道（Claude@SSH）充当会话调度器，Codex 主对话为唯一编排中枢；三源入口（人工/定时/事件）统一驱动；知识资产本地 git 仓+远端备份。

**Tech Stack:** Codex exec resume（主对话注入）/ Tailscale+SSH / [GIT_SERVER] / issue-tracker-cli MCP / Maestro+AVD / 模板体系 v2

**Spec:** 差距分析 A-L 十二类（qa-framework-gap-analysis）+ 模板 v2（已批）+ 实战样本 TASK-20260904-001/002 + 对抗审查 rev2 修订

## Global Constraints

- 只注入主对话 `01a05af8-ca6e-7b63-bab5-4d64993067b6`，不新建**交互**会话。**会话形态定义（明文规则）**：exec 单轮、无人值守、自动退出、产物落盘 = 任务单元会话（**允许**，如 001/002 临时从会话、定时冒烟）；桌面/TUI 可交互形态 = 交互会话（**禁止**新建）
- **注入前锁探测为标准步骤**：每次注入前 `Get-Process codex` 检测——有桌面进程持锁则写 `F:\...\alerts\` 等待/通知用户关闭；**杀 codex 进程是需用户明确确认的显式例外**（会杀掉用户正在用的桌面会话），不得作为静默兜底
- codex exec 必带 `--skip-git-repo-check -m [MODEL]`；跨盘任务加 `-c sandbox_mode="danger-full-access"`
- **工具链互斥**：flutter analyze/test/pub get 等命令同刻仅一个会话执行（cache 锁实锤过挂死）；并行仅限纯设计/纯读类任务。若并行会话报 sqlite busy 则降为错峰
- 路径治理：E:\[TARGET_APP]=代码与脚本（scripts/{bootstrap,test,maintenance} 合法）/ F:\[TARGET_APP]-Toolchain=工具+过程文档+结果 / G:\[TARGET_APP]-Data=数据；不碰旧命名空间
- 证据纪律：无证据=未完成；BLOCKED≠测试失败；每任务产出 summary/commands/evidence/risks 四件套
- 已持久化环境变量（PUB_CACHE/GRADLE_USER_HOME/ANDROID_HOME/ANDROID_SDK_ROOT/ANDROID_USER_HOME + flutter PATH）为既定事实
- 修改 Codex 工作区结构前经主对话确认；知识资产可入 GIT，>1MB evidence 日志不入仓
- **alerts 闭环**：alerts/ 文件名带日期；外部通道每次注入主对话前顺带检查并转发未处理告警

---

## Phase 0：止血与奠基（当天完成）

### Task 0.1 凭据治理（I5）

**Owner:** 用户生成 token + 外部通道落配置
**Files:** Create: `F:\[TARGET_APP]-Toolchain\config\credentials.yaml`（05g 模板，只存别名与位置不存明文）

- [ ] 用户在 [GIT_SERVER] 生成访问令牌：**`read_api` + `write_repository`**（轮询用读、无形资产仓推送用写；若安全政策不允许写权限，则降级 read_api 且"推远端"转挂账离机备份）
- [ ] token 写入用户级环境变量 `HIVI_GITLAB_TOKEN`；密码型凭据从 memory 记录移除（改记"已入 env"）
- [ ] 创建 credentials.yaml（别名/存储位置/用途；含 GITLAB_TOKEN、ZENTAO_TOKEN 预留位、OPENAI_API_KEY 已存在标注）
- [ ] 验收：环境变量非空；credentials.yaml 无任何明文

### Task 0.2 无形资产仓初始化（F3/L3）

**Owner:** 外部通道（SSH）
**Files:** Init: `F:\[TARGET_APP]-Toolchain\docs\`（仓根=docs 区）

- [ ] `git init` 于 docs 区；`.gitignore` 排除 `*.log` 与大文件
- [ ] 首个 commit：workflow/qa 协议文档 + runbooks + reports；**002 分诊矩阵等 results 下的 md 复制入 `docs\reports\` 归档副本**（原位置保留，仓不覆盖 results）
- [ ] 推远端子任务：[GIT_SERVER] 建私有仓 `[target-app]/qa-assets`（需用户/IT 操作）→ push；**token 无写权限或仓未批时：挂账离机备份（每周 zip docs 仓到 G 盘之外介质）**
- [ ] 验收：本地 `git log` 有记录且 status 干净；远端推送成功或离机备份已挂账

### Task 0.3 模板 v2 首批部署（A1/K/A2）——00-05 域 29 个

**Owner:** 外部通道写文件 + 主对话确认
**Files:** Create: `F:\[TARGET_APP]-Toolchain\docs\workflow\qa\templates-v2\`

- [ ] 注入主对话确认 templates-v2 位置 + qa-knowledge 落地路径
- [ ] 部署 **29 个模板**（首批全域 00-05；04 域 4 个随 Phase 4）：
  00 域 3：00-索引 / 00b 仓库注册表 / 00c 设备池清单
  01 域 4：架构总览 / 模块卡片（基线绑定+过期检测） / 接口清单 / 01d 环境依赖卡
  02 域 11：L1/L2/L3/L4（设计方法字段+双通道标注） / 02e 性能 / 02f 稳定性 / 02g 兼容矩阵 / 02h 安全 / 02i 升级迁移 / 02j 设备在环 / 02k 逆向对抗矩阵
  03 域 4：BUG 报告（failed/broken 二分+缺陷管理系统单号位） / 模式库 / 03c BUG 状态跟踪表（含流转规则：新建→复核→已提单→待验证→关闭/打回） / 03d flaky 登记表
  05 域 7：05a 任务卡（**内嵌五角色边界 variant 字段——承接 A2**：考古/正向/逆向/执行/报告各自的职责与禁令随卡下发） / 05b 拆分单 / 05c 新仓接入检查单 / 05d 准入检查单 / 05e 回归触发登记 / 05f 审计日志 / 05g 凭据清单
- [ ] 用 001/002 实战数据实例化首批知识卡：模块卡片×2（绑定基线 commit）、BUG 报告×3（002 矩阵 A 类代表）、00-索引首版
- [ ] commit 入仓
- [ ] 验收：29 文件存在；00-索引反映 001/002 状态；主对话回报确认结构可用（确认内容含：任务卡角色字段可用性）

### Task 0.4 主对话状态外置（恢复可靠性——注意：不减每轮 token 成本，见风险表）

- [ ] 注入指令：每轮任务结束回写 ①00-索引状态行 ②session-state.md（当前任务/下一步/未决）
- [ ] 验收：本轮回报含 session-state.md 首次写入

---

## Phase 1：双环转正（1-2 天）

### Task 1.0 拆分规则 v1（F2）

- [ ] 主对话产出拆分规则 v1 文档（入 docs\workflow\qa\）：输入任务→模块×级别×双通道→任务卡集；考古先行；执行依赖用例；并行度=工具链互斥约束下的最大 2；与 00-索引联动（无卡片模块先考古）
- [ ] 验收：规则文档落盘 + 用"对 Core 执行一轮 L2 验证"这个已验证场景回放推演一次拆分结果合理

### Task 1.1 业务测试要求映射（E 盲区 3——用户定义的"完善方案第一步"）

**Owner:** 外部通道读文档 + 用户确认映射结论
**Files:** Create: `F:\[TARGET_APP]-Toolchain\docs\qa-knowledge\00d-业务要求映射表.md`

- [ ] 读用户桌面《App测试清单》《关联歌单_TDD_ATDD风格测试用例文档》等业务文档（xlsx/xmind 由外部通道解析或请用户导出 md）
- [ ] 逐条映射：业务条目 → 框架环节/级别/模板/工具 → 覆盖 or 缺口
- [ ] 缺口清单报用户裁决（哪些进 Phase 3 排期、哪些挂账）
- [ ] 验收：映射表落盘且用户已裁决缺口归属

### Task 1.2 会话/工作区解耦 + 真实双对抗试点（G1/G2/H1）

**Owner:** 外部通道调度 + Codex 执行
**Files:** Create: `F:\...\results\TASK-20260904-003-dual-adversarial\`（或下一日任务号）

- [ ] 注入主对话：选小模块（配网或登录），按拆分规则 v1 出三张任务卡（05a 模板，各含角色边界 variant）；正向卡与逆向卡**互不包含对方产物路径**
- [ ] 外部通道 spawn 三个独立任务单元会话：**考古先行完成**；正/逆向中纯设计部分可并行，**涉及 flutter 命令的错峰串行**（工具链互斥约束）
- [ ] 注入主对话合并去重：覆盖缺口+分歧点 → 停下报用户
- [ ] 验收：三会话产物目录齐全；**互盲验证=抽检两卡互不含对方产物路径+产物无对方中间文件引用**（时间戳仅证并行）；用户裁决记录在案

### Task 1.3 知识环回写首例

- [ ] 主对话回写模块卡片/L2 合并用例/新模式（若有），更新 00-索引；commit
- [ ] 验收：00-索引 diff 可见增量

---

## Phase 2：外部接口（2-3 天）

### Task 2.1 GIT 事件入口 v1（F3）

**Owner:** 外部通道
**Files:** Create: `E:\[TARGET_APP]\scripts\maintenance\git-poll.ps1` + 计划任务

- [ ] git-poll.ps1：GitLab API（projects by group + commits by ref）比对 `F:\...\manifests\repositories\git-poll-state.json`，变更写 `git-events.jsonl`
- [ ] 计划任务每 30min；**事件→注入的转发按全局锁探测步骤执行**（用户占用主对话时写 alerts 顺延）
- [ ] 变更事件注入主对话："按**拆分规则 v1**（Task 1.0 产出）出任务卡"
- [ ] 验收：手动 poll 产 git-events.jsonl 记录；模拟变更触发一次任务卡生成

### Task 2.2 缺陷管理系统接入 + 状态轮询触发器（F4/J6）

**Owner:** 用户提供信息 + 外部通道安装 + Codex 接流程
**Files:** Install: issue-tracker-cli；Create: 03c 状态跟踪表实例 + `E:\[TARGET_APP]\scripts\maintenance\zen-poll.ps1`

- [ ] 用户确认缺陷管理系统版本/地址；生成 ZENTAO_TOKEN
- [ ] `npm i -g issue-tracker-cli`（老版换 issue-tracker-v1-mcp）→ `issue-tracker add-mcp`
- [ ] **zen-poll.ps1**：每 30min 经 MCP/CLI 查"状态=已解决且指派=我"，比对 03c 跟踪表 → 新变化写 git-events 同级的 `zen-events.jsonl` 并按回归触发登记（05e）生成验证任务卡
- [ ] 从 002 矩阵选 3-5 代表缺陷，经用户复核提首批 BUG 单
- [ ] 验收：MCP 拉到真实工单；**一次模拟状态变更走完 zen-poll→05e 登记→验证任务卡生成**；首批单在 03c 表可查

### Task 2.3 新仓接入 SOP 试用（H1/H2）

- [ ] 拿 server 或 mobile-native 仓走 00b 登记+05c 六步（登记→冻结→AGENTS.md 模板→目录→考古→冒烟）
- [ ] 记录实际耗时（目标 ≤半天）；SOP 修订
- [ ] 验收：新仓有模块卡片+一次冒烟证据

---

## Phase 3：覆盖面扩展（滚动推进）

### Task 3.1 App 优先 L4 试点（不等 Core 修复）

- [ ] App `flutter build apk --debug`（隔离副本，记录缓存路径+APK sha256）
- [ ] 模拟器安装 + Maestro Flow（登录或首页 accessibility 断言）
- [ ] 验收：APK+哈希；Flow 截图+hierarchy 证据

### Task 3.2 L1 冒烟集成文化（Task 4.1 显式前置）

- [ ] 从 1.1 业务映射表已覆盖条目 + Maestro 已验证 Flow 中沉淀 App 冒烟集：≥5 条（启动/登录/首页核心元素/一条业务路径/退出），每条带稳定选择器，Maestro tag `smoke`
- [ ] 冒烟集入无形资产仓（.maestro/ 目录 + config.yaml includeTags: smoke）
- [ ] 验收：本地一次全量冒烟跑通并出报告（红绿不论，产物齐全）

### Task 3.3 工具按需安装

- [ ] 首批：Allure + faker + **pixelmatch（视觉对比，G2 断言×视觉通道起步——截图 diff 脚本并入 Maestro Flow 后处理）**
- [ ] k6/Schemathesis/Fastbot/Toxiproxy/ZAP：到对应轮次再装
- [ ] 验收：三个工具版本命令可用；pixelmatch 对两张测试截图产出 diff 图

### Task 3.4 修复验证流启动（B4/F4）

- [ ] CORE-T1 提单（经 2.2 通道）；**验证触发走 zen-poll 自动登记（05e）**，不靠人肉盯
- [ ] 开发修复后：验证轮（重跑受影响测试）→ 回归判定 → 关闭/打回
- [ ] 验收：至少一张单走完 状态变更→自动触发→验证→关闭 全程

### Task 3.5 设备策略与池（F1/J2）

- [ ] `adb devices` 盘点真机；00c 实例化（含能力保真度标签）
- [ ] **测试类型→设备映射表**（L1/L2 无设备；L3 UI 模拟器、蓝牙/音频/网络切换真机；L4 真机优先）入 00c
- [ ] **差异归档规则**：模拟器过+真机挂的案例记入模式库（进知识环）
- [ ] AVD 占用规则：同刻 1 任务；**定时任务遇 AVD 被占则顺延并在 alerts 记录**
- [ ] 验收：00c 三件齐（清单/映射/占用记录）

---

## Phase 4：运营固化（持续）

### Task 4.1 定时冒烟（J4）——两步走

- [ ] **第一步（手动）**：冒烟脚本（起 AVD→加载 ANDROID_HOME/PATH→codex exec 独立任务单元会话跑冒烟集→产物落当日 results→关 AVD）本地手动跑通 3 次
- [ ] **第二步（挂计划）**：schtasks 每日 08:30；失败写 alerts（文件名带日期）
- [ ] 验收（**"稳定"定义**）：连续 3 天**每日产出冒烟报告**（红绿不论）；红则 alerts 闭环生效（下次注入转发）

### Task 4.2 度量与周期报告（I1）

- [ ] 周期汇报模板指标字段启用：通过率/BUG 密度/覆盖率/回归时长/逃逸率
- [ ] 双周报首版：**有数据源指标填实值；无数据源指标标 N/A+补数计划**（逃逸率待线上反馈通道、覆盖率待采集机制——均挂账）
- [ ] 验收：首份双周报且 N/A 项均有补数计划

### Task 4.3 审计与哈希（J1）

- [ ] 05f 启用：每任务 append（时间/会话/任务/证据路径+sha256）
- [ ] 验收：**启用后**的任意任务可从审计行查到证据哈希（不溯及既往）

### Task 4.4 框架总说明书 + 迁移演练（小项⑤ + 上下文上限预案）

- [ ] 一页架构图（三源入口/双环/解耦/E-F-G）+ 上手指南
- [ ] **迁移演练**：新开任务单元会话按说明书走通"注入命令模板+从 00-索引/session-state 恢复状态"全流程——**禁止触碰既有 threads 数据**
- [ ] 验收：演练会话能正确复述当前项目状态（以 session-state 为源）

---

## 挂账清单（条件不具备或未排期，非消失）

iOS 线（需 Mac/WDA）；音频客观工具选型（02j 字段位已留）；生产数据脱敏进场（I2 子项）；团队化（J8）；AI 服务测试线（L1——Server-AI 入范围时立专项）；**J5 对外正式报告流（docx/签批——下次试产验收前启用）**；**J7 准入/准出两端（开发流程配合后启用）**；**L2 token 成本预算（先记账后预算，见风险表）**；**I3 flaky 消化策略全量版（03d 登记表已部署，隔离/重跑策略随对抗轮次细化）**；**F3 的 MR 修复闭环 GIT 侧（fix 分支/MR/合并流——开发协作流程确认后启用）**；**离机备份（若 0.2 远端推送未获批）**；**E 类专项执行轮次（性能/安全/兼容等——模板已备，按业务映射表裁决排期）**。

## 风险与缓解（rev2：上下文风险拆三行）

| 风险 | 缓解（如实标注有效性） |
|---|---|
| 主对话上下文膨胀——**恢复可靠性** | Task 0.4 状态外置：**有效**（下轮恢复不依赖模型记忆） |
| 主对话上下文膨胀——**token 成本** | 0.4 **不减少**每轮全量计费成本。缓解=记账：每轮注入记录 token 增量（会话头 tokens used 已有），Phase 0-4 预计注入 ~25 轮，累计成本入 L2 挂账监控 |
| 主对话上下文膨胀——**上限撞墙** | **定量阈值：tokens used > 15M 或连续 2 次注入失败 → 触发迁移提议**（新主对话+00-索引/session-state 引导继承，Task 4.4 已演练），迁移需用户批准 |
| LiteLLM 单点 | 注入重试+错峰；Phase 2 后 BUG 单在缺陷管理系统（记录幸存，**执行仍会停**——如实：缓解有限，管理员级修复见 litellm 报告） |
| 用户审批排队 | 缺口/定级攒批裁决；不可逆动作单件确认 |
| 写锁冲突 | 注入前锁探测标准步骤；事件注入遇占用写 alerts 顺延；杀进程=用户确认例外 |

## 执行分工总则

外部通道（Claude@SSH）：环境/工具/文件/git/调度/锁探测。Codex 主对话：协议内业务（任务卡/分诊/报告/知识回写/拆分规则）。用户：token 与权限、远端仓审批、覆盖缺口与定级裁决、不可逆动作、杀进程例外确认。
