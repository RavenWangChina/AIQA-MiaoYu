# Codex QA Workflow Adaptation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 AIQA-MiaoYu 的双环 QA 方法论适配为 [TARGET_APP] 当前 Codex 主会话治理协议，并提供可执行的任务卡与本地路径/证据自检。

**Architecture:** 保留测试环与知识环、L1-L4 分级、正向/逆向对抗和证据链；由当前主会话统一调度专项任务。Codex 角色定义使用任务卡和职责协议表达，不复制 Claude 专用 agent、模型、网关或权限配置。自检脚本只读验证协议、路径规则和结果目录契约。

**Tech Stack:** Markdown、YAML、PowerShell 7+（兼容 Windows PowerShell 5.1 的核心语法）。

**Spec:** `docs/superpowers/specs/2026-09-02-codex-qa-workflow-adaptation-design.md`

## Global Constraints

- 代码仅允许位于 `E:\[TARGET_APP]`；工具、过程文档和结果位于 `F:\[TARGET_APP]-Toolchain`；分级数据位于 `G:\[TARGET_APP]-Data`。
- 任务必须声明任务 ID、项目基线、允许操作、数据标签、结果目录和验收条件。
- 专项任务不得提交、推送、修改权限、连接生产资源或写入共享配置。
- 没有可复查证据时，状态只能为“待验证”。
- 本阶段不修改远端仓库，不安装模型、网关或全局插件。

---

### Task 1: 持久化适配设计

**Files:**
- Create: `docs/superpowers/specs/2026-09-02-codex-qa-workflow-adaptation-design.md`

- [ ] **Step 1: 写设计文档**

记录组件边界、双环数据流、五类专项任务映射、并发写入策略、错误状态和验证标准。

- [ ] **Step 2: 自审设计文档**

检查是否包含路径、权限、证据、失败回退和不复制 Claude 配置的明确约束。

### Task 2: Codex 编排协议与任务卡

**Files:**
- Create: `codex-qa-orchestration.md`
- Create: `templates/qa-task-card.yaml`

- [ ] **Step 1: 定义主会话与五类专项职责**

将考古、正向用例、逆向用例、执行、报告映射为 Codex 任务协议，规定输入、输出、禁止项和回报格式。

- [ ] **Step 2: 定义任务卡字段**

任务卡必须包含 `task_id`、`project`、`baseline`、`scope`、`allowed_operations`、`data_label`、`result_dir`、`acceptance`、`prohibited_operations`。

### Task 3: 本地治理自检

**Files:**
- Create: `scripts/qa-selfcheck.ps1`

- [ ] **Step 1: 编写失败条件清单**

脚本检查协议文件、任务卡字段、路径前缀和结果目录必备文件约束；错误时返回非零退出码。

- [ ] **Step 2: 运行自检确认失败**

使用临时缺失文件或非法路径样例验证脚本能拒绝不合规输入。

- [ ] **Step 3: 完成最小实现**

加入只读检查、清晰错误输出和成功摘要，不创建或删除用户目录。

- [ ] **Step 4: 运行自检确认通过**

对当前工作区的协议文件和模板执行完整检查，并保存命令输出。

### Task 4: 结果与后续接入

**Files:**
- Modify: `[target-app]-orchestration.md`
- Modify: `local-storage-governance.md`

- [ ] **Step 1: 增补 AIQA 适配入口**

只增加引用和路径映射，不改变现有主会话职责、并发上限和审批点。

- [ ] **Step 2: 运行全量治理自检**

确认新增协议与现有六环节、E/F/G 分盘规则和 Git MCP 配置没有冲突。

