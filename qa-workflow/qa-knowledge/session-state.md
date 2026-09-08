# Session State

更新时间：2026-09-07（晚，登录轮暂停点）
状态来源：外置状态回写（TEST-SYNTHETIC）

> ## ⏸ 当日收工断点（2026-09-07 深夜，最新断点，恢复时优先读本节）
> 1. **首片已派**（v1.1 分片）：新 executor 领 POS-002 + POS-004 + MERGE-02 三单元；它状态复核发现**上次登录实际已成功**（shared_prefs 真实 JWT userId=226、AppShell 已渲染用户数据），但 POS-002 关键断言无证据。
> 2. **主对话已裁决 A**：pm clear 完整重跑（授权销毁 userId=226 会话）→ 重过隐私同意（准备步）→ POS-002 全断言重跑（新收码点）。**pm clear 已执行**；强停时 App 画面疑为旧进程残影（"画面仍显示登录态首页"），明日开工先复核实际存储/窗口状态。
> 3. **设备已释放**：emu kill 收工，内存 0.9G→5.5G；00c 已回写关机（空闲）。明日开机 **Quick Boot 即可**（config 变更后冷启动已做过一次）。
> 4. **明日恢复序列**：开机预检（00c 硬规则：可用 ≥5G）→ 00c 登记占用 → Quick Boot 开机 → spawn 首片 executor（短信组收口 3 单元；号码明文 [PHONE] 届时会话内随片下发）→ 复核 App 实际状态 → 隐私同意准备步 → POS-002 收码点（用户回读）→ 片间 SendMessage 续派同一 executor → 全部 ⏳ 单元收口 → qa-reporter → 主对话复核三问 → 缺陷管理系统提单检查点。
> 5. 风险备忘：宿主内存紧张时段（<5G 可用）不得开工；设备命令一律 30s 超时 + 弃片条款兜底。

> ## ⚡ 框架 v1.1 变更通知（登录会话恢复时必读）
> 用户已暂停登录轮做框架调整，以下规则**立即生效**，恢复执行时按新规则跑：
> 1. **分片执行**：executor 每次只领 ≤3 个执行单元，片间回报红绿灯，主对话循环续派（宪法"分片调度"）。
> 2. **设备命令强制超时**：adb/maestro/uiautomator 全部带 30s 超时，超时标 `BLOCKED(tool-timeout)` 转下一步，禁止干等。
> 3. **可见性**：UI 用例执行前确认模拟器有窗 + 开 scrcpy 镜像；每片开跑即分段录屏（180s）。
> 4. **人工中断点协议**：任务卡 `human_interruption_points` 预声明；执行中遇到即停下回报，主对话向用户收集后续派；人工输入尽量派发前收齐。
> 5. **Maestro 防 flaky 规范**已入 `02-L2功能.yaml` automation_guidance（text>id 选择器、轮询断言禁 sleep、retryTapIfNoChange）——新写/重写自动化步骤时遵循。
> 6. **分片升级 v1.2·恢复续跑**：同一批次内 spawn 首片后，后续片用 SendMessage 恢复同一 executor（上下文保留）；恢复时先重读 progress.md 对齐磁盘。progress.md 是事实源。
> 7. **提速预调**：每个执行会话首个 UI 用例前先跑 `E:\[TARGET_APP]\scripts\device-speed-prep.ps1`（关闭系统动画+保持唤醒）；模拟器开机默认 Quick Boot，仅配置变更后冷启动一次。
>
> 恢复登录轮时：按下方断点续跑，重派 executor 从 POS-002 起，**首片建议 = 短信组收口 3 单元**（收码优先用 acct-[app-]mobile 短信回读，避免人工等待）。

## 2026-09-07 登录模块轮（TASK-20260907-001~005）——用户暂停做框架调整，断点如下

- **进度**：001 考古完成（模块卡片-login.md）→ 002/003 双从用例完成（正向 14 + 逆向 33 含 NEG-TOKEN-003）→ 004 合并（40 执行单元 + 6 跨通道合并，产物 `results/TASK-20260907-004-login-merged/`）→ 005 执行 PARTIAL：🟢2（POS-001、NEG-PRIV-002）/ 🔴1（NEG-PRIV-001 不同意不退出，suspected-defect）/ 🟡18（credential-required 4、tool 8、env 7）/ ⏳19。执行从已停，App 疑似掉桌面（恢复时先复核）。
- **用户三项裁决**：① 全量推进（前置缺失记 BLOCKED 不等齐）；② G3 token TTL 本轮补用例（NEG-TOKEN-003 已补）；③ 执行过程录屏（adb screenrecord，单段 180s，落 evidence）。
- **用户两次纠错（已固化）**：① token 失效类用例硬前置=先真实登录建立有效会话再注入/篡改，空 token 态重现无效记 BLOCKED（NEG-SESS-001~005、NEG-TOKEN-001~003 precondition 已修订）；② （隐含）验证码时效管理——旧码作废须重发。
- **环境事件**：宿主机 OOM（用户已清理）致模拟器 SystemUI ANR → QEMU 崩溃退出 2 次 + 渲染故障 1 次；已冷启动 [app-]qa（-no-snapshot-load）并健康检查全绿。ADB UI dump/输入挂起有前科（005 轮亦发生），唤醒-观察哨-强停重派的处置链路已验证有效。
- **凭据变更**：05g 新增别名 acct-[app-]mobile（短信回读，明文仅主对话会话内传递，不入库不入仓）；acct-qq-music 明文仍未确认；`G:\[TARGET_APP]-Data\test\credentials\` 目录不存在。
- **恢复入口**：读 005 执行任务卡 `plans/007-login-cards/007-card-executor.yaml` + `results/TASK-20260907-005-login-execution/progress.md`（40 单元红绿灯 + BLOCKED 清单 + 纠错记录全在）→ 重派 qa-executor 从 POS-002 收码点续跑（号码明文需主对话会话内传递）→ 顺序：短信组收口 → 会话/token 组（按新前置）→ NEG-ANR-001 最后 → qa-reporter。
- **环境验证遗留**：TASK-20260907-000 已验证测试服 `http://[TRACKER_IP]/api` 发码+登录契约；JWT 有效期整 10 年（exp=iat+315360000s）作安全议题随报告上報。

## 2026-09-07 Claude Code 迁移部署

- 平台迁移：工作流载体由 Codex 迁移至 Claude Code（VS Code 扩展，主入口）。AIQA-MiaoYu 上游（[PERSONAL_PC]WangChina/AIQA-MiaoYu）克隆归档于 `F:\[TARGET_APP]-Toolchain\archives\aiqa-miaoyu-upstream\`。
- 已部署：主对话宪法 `F:\[TARGET_APP]-Toolchain\CLAUDE.md`（上游宪法 + 本地治理合并，路径指向 `docs/qa-knowledge/` 与 `templates-v2/`）；五个从对话 `.claude\agents\qa-{archaeologist,case-positive,case-negative,executor,reporter}.md`（各含本地知识库路径锚点）。
- **全局化改造（按用户 VS Code 插件主入口习惯）**：五从对话同时部署到全局 `C:\Users\swan\.claude\agents\`（含绝对根锚点，任意工作目录可用）；全局记忆 `C:\Users\swan\.claude\CLAUDE.md` 建立 QA 工作路由（开工先读宪法与 session-state，含 E/F/G 分层与环境事实）。F 盘部署保留，作为以该目录为工作区时的原生加载。
- 已实例化：`03-BUG库/模式库.md`（P-001 契约不同步 / P-002 嵌套包依赖边界 / P-003 启动时序 ANR，种子来自 001-004 号 BUG）。
- 已注册：缺陷管理系统 MCP 至 Claude Code（`~/.claude/settings.json`，npx issue-tracker-cli mcp）；**Git MCP 已连通**（`F:\[TARGET_APP]-Toolchain\mcp-server-git\venv\Scripts\mcp-server-git.exe`，mcp-git 1.29.1，12 工具，2026-09-07 注册并实测 git_status 通过；Codex 时期的握手 BLOCKED 确认为 Codex 侧问题，服务本身无故障）。相关仓库已加 git safe.directory 白名单（F:\[TARGET_APP]-Toolchain\docs、archives、E:\[TARGET_APP]\repos 下 7 个检出）。
- Maestro 确认已在用户 PATH（此前 session-state 记录过时，更正）。
- 部署自检：`docs/workflow/qa/selfcheck-claude-deploy.py` 全绿（0 失败 0 警告，2026-09-07）。
- 更正记录：Codex 的 memories_1.sqlite 为空，历史状态全部以本文件与 docs 文档为准；Codex 侧固定/临时会话链路问题不再跟踪（Claude Code subagent 无此问题）。
- 下一步候选：新会话冷启动验证（复述八步编排+三类检查点）；缺陷管理系统 MCP 连通验证（拉一条真实工单）；然后承接遗留项（ANR 复现、Phase2 intake SOP、模块17 locator contract 闭合）。

- 证据采集工具链补全（2026-09-07）：qa-executor 定义（F 盘+全局）固化证据命令速查（screencap / screenrecord / scrcpy --record / maestro record / logcat+dropbox），BUG 复现纪律"先开录屏再复现"；scrcpy 4.1 经 winget 装机（当前进程 PATH 未刷新，新 shell 生效）；BUG 报告模板本就含"截图/日志/录屏路径"字段，报告层无需改动。

## 2026-09-07 框架审计与九项完善（主对话·运维会话）

- 审计结论（用户确认）：高风险 3 项（03c BUG 状态机 / 05e 回归触发 / intake 三源）**先经流程测试验证再完善**——流程测试方案：缺陷管理系统 MCP 活动后走一次完整 BUG 生命周期演练（本地 BUG → 提单测试产品 → 状态回流 → 回归触发 → 关闭）。
- 已完善：④严重级改 S1-S4（模板+命名规范，与测试级别 L1-L4 严格区分；存量报告不回改）；⑤`metrics-rollup.py` 自动汇总并写入 00-索引 度量看板（METRICS 标记块）；⑧`baseline-gate.py` 基线/证据门禁（已实测，正确拦截 005 缺 summary.yaml）；⑨05f 审计日志实例化并写入宪法第 8 步；⑩03d flaky 表实例；⑪接口清单/架构总览骨架实例；⑫05g 凭据清单实例（缺陷管理系统密码明文于 settings.json 登记为已接受风险，建议换 token）。
- 证据采集补全：qa-executor（双份）固化证据命令速查（screencap/screenrecord/scrcpy --record/maestro record/logcat+dropbox），纪律"BUG 复现先开录屏再复现"；scrcpy 4.1 已装。
- 待办（流程测试后）：03c/05e/intake 完善；音频客观指标与视觉断言（Midscene）工具选型需用户参与决策。

## 2026-09-07 TASK-20260907-002-avd-repair（虚拟机修复 + 实机准备）

- [app-]qa AVD 配置修复：GPU disabled→host、RAM 4G、heap 256M、1080×1920@420dpi（原 320×640 软渲染配置严重不达标，是 ANR 重大嫌疑；备份在 results/TASK-20260907-002-avd-repair/config.ini.bak）。
- **占用事故**：本任务与登录测试会话双驱动 emulator-5554，13:15-13:18 爆发 19 条系统级 ANR（system_server 阻塞 15s），判定为争抢产物不计业务失败；探测方已退避。**规则生效：两会话开工前必须先查 00c 占用表**。
- 新增实例：`docs/qa-knowledge/00c-设备池清单.md`（设备台账 + 占用规则 + 事故表 + [app-]qa 修复后参数）。
- 新增文档：`docs/runbooks/real-device-onboarding.md`（实机接入 SOP：预置/连接/保真度实测/登记/占用纪律/首轮验证）。实机预计 2026-09-08/09 到达，已在设备池预登记"待接入"。
- adb platform-tools 已入用户 PATH。
- 待复核：AVD 修复对 ANR 的实际效果需在设备池空闲窗口做单任务启动探针；GPU host 若渲染异常回退 swiftshader_indirect。

## 2026-09-07 TASK-20260907-001-login-archaeology（qa-archaeologist）

- 登录模块只读考古完成：基线 App `dev@4d1ed7b` / Core `dev@402853ab`（实测确认，与任务卡一致）。
- 产出：`01-系统认知/模块卡片-login.md`（接口契约、token 三处存储、无 refresh、登出 4 触发点、11 已知坑、5 未决）；证据 `results/TASK-20260907-001-login-archaeology/`。
- 未修改源码/用例库/BUG库；00-索引.md 模块清单已更新（卡片 4 张）。
- 关键未决：区号接口为外部 MXNZP 依赖（硬编码凭据）；token 明文 SharedPreferences 且冷启动不校验；扫码登录（pad）是否纳入 login 用例范围待主对话裁决。

## 当前状态快照（2026-09-04 Codex 时期，待迁移后复核）

- 当前阶段：Phase1.3 收口完成，进入 Phase2 intake polling/SOP 与 Phase3 执行准备；本轮完成 MCP/Git 状态核验，仅更新文档，不执行测试、不修改业务源码。
- 模板规划：`F:\[TARGET_APP]-Toolchain\docs\workflow\qa\templates-v2\` 作为 QA 模板域，承载首批 29 个模板（00-05）；路径符合知识环规划。
- 知识库根：`F:\[TARGET_APP]-Toolchain\docs\qa-knowledge\`；已存在 `flutter-vertical-workflow-20260903.md`。
- 角色边界：05a 任务卡内嵌考古/正向/逆向/执行/报告五角色 variant，可承接专项任务职责与禁令，确认采用。
- 最近完成：`TASK-20260904-002-core-defect-triage` 只读分诊矩阵已归档。
- 本轮完成：`F:\[TARGET_APP]-Toolchain\docs\workflow\qa\task-split-rules-v1.md`，定义三源 intake、05b 拆分、L1-L4 双通道、依赖拓扑与并行约束。
- 本轮完成：模块17搜索的考古、正向、逆向三张独立任务卡；正向/逆向卡互盲，分别遵循 02-L2 与 02k 字段。
- 本轮完成：模块17搜索合并清单 `F:\[TARGET_APP]-Toolchain\results\TASK-20260904-003-search-merged\merged-cases.yaml` 与覆盖缺口 `coverage-gaps.md`；保留 14 个 case ID 与三源产物路径。
- 本轮摘要：`F:\[TARGET_APP]-Toolchain\results\TASK-20260904-003-search-merged\summary.yaml`，状态为 `merged_not_executed`；locator contract 仍待确认。
- 本轮决策：`TASK-20260904-003-DEC-001` 将模块17 `NEG-CONCURRENCY-001` 的执行策略固化为 `latest-wins`；运行证据待 Phase3。
- MCP 状态（2026-09-04）：配置文件登记 7 个服务（含 `git`、`git_core`）；Git MCP 可执行文件存在，但当前会话未暴露可调用的 Git MCP 工具，判定为 `BLOCKED`（握手/工具暴露层）。
- Git CLI 状态：`[COMPANY] Network-FlutterApp` `dev` HEAD 已确认为 `[COMMIT_HASH]`；工作树保留既有 `analysis_options.yaml`、`pubspec.lock` 修改。该状态不受 Git MCP 阻塞影响。
- 最近验证基线：Core `dev` @ `[COMMIT_HASH]`；App `dev` @ `[COMMIT_HASH]`。
- 质量门禁：App L1/L2 已通过；Core 仍有 328 条 analyzer diagnostics、43 个测试失败，Core APK/全链路门禁保持阻塞。
- 会话通道：固定会话链路问题仍暂缓，当前按临时任务通道执行；不将会话基础设施问题归类为业务测试失败。
- 路径约定：`E:\[TARGET_APP]` 为代码与脚本根；`F:\[TARGET_APP]-Toolchain` 为工具、文档与结果根；`G:\[TARGET_APP]-Data` 为临时/生产/过程数据根。

## 待办

- `TASK-20260904-005-search-execution`：模块17搜索 L2 双通道执行当前 `BLOCKED`（`device-required`）。`adb devices`、包/Activity 检查通过；ADB UI dump 曾挂起，Maestro hierarchy 探针捕获 `[TARGET_APP] isn't responding` ANR 对话框，搜索页面不可达。Maestro 位于 `C:\Users\swan\maestro\bin\maestro.bat` 但未入 PATH。证据：`F:\[TARGET_APP]-Toolchain\results\TASK-20260904-005-search-execution\`。
- 下一步（依赖解除后）：恢复 ADB UI shell/截图链路，定位搜索入口并关闭 `locator_contract`；确认 Maestro CLI 后执行 6 个正向 + 8 个逆向 L2 case。不得将本次环境阻塞登记为业务 BUG。
- 005 复核补充：`evidence/anr-recheck.png` 已保存；Maestro hierarchy 现可达登录页（仅登录 locator），搜索 locator contract 仍未确认。14 个 L2 case 均 `BLOCKED`，进度见 `results/TASK-20260904-005-search-execution/progress.md`。新增 ANR 候选记录 `03-BUG库/BUG-20260904-004-app-anr-candidate.md`，不计入业务失败。

1. 外部部署并校验 `templates-v2` 首批 29 个模板及其版本元数据。
2. Phase2 建立 `git-poll`、`zen-poll` 与人工 intake SOP，并将事件转换为标准化 intake。
3. 先闭合模块17正向 `locator_contract`，再审批执行环境与合并清单。
4. Phase3 分别调度正向/逆向执行卡，使用独立证据目录与 Flutter 全局互斥；优先验证 `latest-wins`。
5. 将 05a 五角色边界随执行任务卡下发，并在后续任务卡中记录实际 variant。
6. Phase3 处理覆盖缺口 G3/G4/G5/G6/G8；Core 仍按 `CORE-T1` 至 `CORE-T6` 依赖顺序推进。
7. 每轮结束回写本文件与 `00-索引.md`，记录当前任务、下一步、未决事项和各库状态。

## 未决事项

- 固定会话链路何时恢复，以及是否继续使用临时从对话通道。
- Core 43 个失败项中平台 stub 与时序项的最终归因，需在修复任务中隔离复现。
- 模板 v2 外部部署完成时间及其首个可用版本号。
- Git MCP 握手恢复时间；恢复前使用本地 Git CLI 做只读仓库操作，不宣称 Git MCP 已连通。
