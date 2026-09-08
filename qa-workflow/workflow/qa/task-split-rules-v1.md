# 任务拆分规则 v1

版本：v1.0  
生效阶段：Phase1.0  
适用范围：[TARGET_APP] QA 工作流（Core、App 及后续模块）  
规则文档本身不触发测试、构建、提交或推送。

## 1. 标准化 Intake

所有来源先转换为统一 intake，再进入拆分。缺失字段不得猜测；标记为 `unknown` 并生成考古卡。

### 1.1 人工指令

必填字段：

| 字段 | 含义 |
|---|---|
| `intake_id` | `MAN-YYYYMMDD-序号` |
| `source_type` | `human` |
| `request_text` | 原始指令全文 |
| `requester` | 指令人/角色 |
| `received_at` | 接收时间（含时区） |
| `scope_modules` | 模块或仓库；未知时为 `unknown` |
| `target_levels` | L1/L2/L3/L4；未指定时为 `unknown` |
| `target_channels` | 正向、逆向或 `both`；未指定时为 `both` |
| `code_baseline` | 分支、commit 或工作树路径 |
| `data_label` | 数据分级；默认 `TEST-SYNTHETIC` |
| `constraints` | 是否只读、禁止提交、超时上限等 |
| `acceptance` | 可判定的完成条件 |

### 1.2 GIT 分支变更事件

必填字段：

| 字段 | 含义 |
|---|---|
| `intake_id` | `GIT-YYYYMMDD-仓库-commit` |
| `source_type` | `git_branch_event` |
| `provider` | GIT 服务标识 |
| `repository` | 仓库 URL/规范名 |
| `branch` | 变更分支 |
| `before_commit` / `after_commit` | 变更两端 commit |
| `changed_paths` | 文件路径列表或 diff 摘要 |
| `author` / `committer` | 变更元数据 |
| `event_at` | 事件时间（含时区） |
| `scope_modules` | 根据路径映射的模块；无法映射则 `unknown` |
| `target_levels` | 事件策略默认 `L1,L2`，可被策略覆盖 |
| `target_channels` | 默认 `both` |
| `data_label` | 默认 `TEST-SYNTHETIC`，不得带入生产数据 |
| `constraints` / `acceptance` | CI 门禁、构建限制与验收条件 |

### 1.3 缺陷管理系统已解决事件

必填字段：

| 字段 | 含义 |
|---|---|
| `intake_id` | `ZENTAO-YYYYMMDD-编号` |
| `source_type` | `issue-tracker_resolved` |
| `issue-tracker_id` | 缺陷管理系统 Bug/任务编号 |
| `title` / `resolution` | 原标题与解决说明 |
| `resolved_by` / `resolved_at` | 解决人及时间 |
| `affected_modules` | 受影响模块；未知则 `unknown` |
| `fix_commit` | 修复 commit/分支，缺失则 `unknown` |
| `repro_steps` / `expected` / `actual` | 复现、期望、实际结果 |
| `severity` / `priority` | 原工单等级 |
| `target_levels` | 由严重度映射，缺失时先考古 |
| `target_channels` | 默认 `both` |
| `data_label` | 默认 `TEST-SYNTHETIC` |
| `constraints` / `acceptance` | 回归范围、环境限制、关闭条件 |

## 2. 拆分算法

1. **规范化**：校验 intake 必填字段、脱敏、生成不可变 `intake_id`，记录原始来源位置。
2. **读取状态**：先读 `F:\[TARGET_APP]-Toolchain\docs\qa-knowledge\00-索引.md`，再读 `session-state.md` 与模块卡片；以索引中的模块基线和用例状态为准。
3. **建立维度笛卡尔积**：对每个 `模块 × 级别(L1-L4) × 双通道(正向/逆向)` 生成候选任务卡；未在 intake 指定的级别按事件策略补齐并显式记录。
4. **无卡先考古**：模块没有系统认知卡、基线或边界信息时，只生成 01/考古卡；考古卡完成前不得生成执行卡。
5. **05b 承载拆分**：所有候选卡集由 05b 拆分单承载，记录父 `intake_id`、模块、级别、通道、前置卡、数据标签、权限范围、工具需求和验收条件。
6. **用例优先**：执行卡必须依赖同模块、同级别、同通道的用例卡；缺用例时先生成用例卡，不允许执行卡越级代替用例设计。
7. **双通道完整性**：`both` 必须产生正向与逆向两条链；仅指定单通道时，05b 记录豁免原因和风险。
8. **去重与合并**：同一模块、级别、通道、基线和数据标签的多个三源事件可合并为一批，但保留所有来源 ID；不同基线不得合并。
9. **门禁输出**：每张卡必须写明 `READY`、`BLOCKED` 或 `WAIVED`，阻塞原因不得伪装成测试失败。

## 3. 依赖图与并行度

### 3.1 拓扑序

```text
Intake
  ↓
考古卡（模块/基线/边界）
  ↓
用例卡（L1-L4 × 正向/逆向）
  ↓
执行卡（工具调用与证据采集）
  ↓
报告卡（结论、BUG 底稿、风险与回写）
```

同一模块同一维度必须遵守该顺序；报告卡只能消费已完成执行卡的证据。

### 3.2 并行约束

- **工具链互斥**：Flutter 类命令（`pub get`、`analyze`、`test`、`build`）同一时刻全局最多 1 个；不同工具链可并行，但共享缓存写操作需显式隔离。
- **模块隔离**：不同模块在考古/用例阶段可并行；同模块的执行卡按依赖拓扑串行。
- **通道隔离**：正向与逆向可并行，前提是使用独立临时数据、结果目录和设备/模拟器会话。
- **三源合批**：人工指令、GIT 事件、缺陷管理系统已解决事件只有在模块、基线、级别、通道、数据标签一致时才可合并；合批卡保留来源集合和冲突检查结果。
- **状态锁**：一轮结束先写 `00-索引.md` 与 `session-state.md`，下一轮才可消费新的基线状态。

## 4. 回放校验

### 4.1 场景 A：`对 Core 执行 L2 验证`

从人工指令规范化：`source_type=human`、`scope_modules=[company-]network_flutter_core`、`target_levels=L2`、`target_channels=both`（默认）、`data_label=TEST-SYNTHETIC`。

当前索引显示 Core 有模块卡但“无用例（仓库自带测试已执行）”，因此 05b 应生成：

1. `CORE-L2-ARCH-BOTH`：考古/基线与边界确认卡（若沿用当前模块卡，可标记为复核卡）。
2. `CORE-L2-UC-FWD`：L2 正向用例卡。
3. `CORE-L2-UC-REV`：L2 逆向/异常用例卡。
4. `CORE-L2-EXEC-FWD`：正向执行卡，依赖 `CORE-L2-UC-FWD`。
5. `CORE-L2-EXEC-REV`：逆向执行卡，依赖 `CORE-L2-UC-REV`。
6. `CORE-L2-REPORT`：汇总报告卡，依赖两张执行卡并回写知识库。

若本轮只授权只读分诊，执行卡状态为 `BLOCKED`，不得将已知 Core 失败误报为执行成功。

### 4.2 场景 B：`App 分支有新 commit`

从 GIT 事件规范化：`source_type=git_branch_event`、模块映射为 `[COMPANY] Network-FlutterApp`、`target_levels=L1,L2`（默认）、`target_channels=both`。

每个级别均生成正/逆向用例与执行链；若 App 已有考古卡，可复用并做基线复核：

1. `APP-L1-ARCH-REBASE`、`APP-L2-ARCH-REBASE`：分别确认新 commit 与模块卡基线差异。
2. `APP-L1-UC-FWD/REV`、`APP-L2-UC-FWD/REV`：四张用例卡。
3. `APP-L1-EXEC-FWD/REV`、`APP-L2-EXEC-FWD/REV`：四张执行卡，各自依赖对应用例卡；Flutter 命令由全局互斥调度器串行。
4. `APP-L1-REPORT`、`APP-L2-REPORT`：两张级别报告卡；最终可由批次报告卡合并。

若 diff 无法映射到模块或基线缺失，先暂停执行链，追加考古卡并将后续卡标记 `BLOCKED`。

## 5. 05b 拆分单最小字段

`split_id`、`parent_intake_ids[]`、`module`、`level`、`channel`、`variant`、`card_type`、`depends_on[]`、`baseline`、`data_label`、`permission_scope`、`toolchain_lock`、`status`、`acceptance`、`evidence_dir`、`next_card`、`blockers`、`risks`。

05a 任务卡的 `variant` 必须随卡下发五角色边界：考古、正向、逆向、执行、报告；每个角色同时携带职责和禁令，禁止跨角色越权修改或宣称完成。

## 6. 版本与回写

- 规则变更升级版本号，不覆盖历史任务卡的规则快照。
- 每轮结束回写 `F:\[TARGET_APP]-Toolchain\docs\qa-knowledge\00-索引.md` 与 `session-state.md`。
- 本规则只定义拆分与调度，不授权提交、推送、生产访问或业务源码修改。
