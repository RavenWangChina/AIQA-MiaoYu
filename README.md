# AIQA-MiaoYu

> **© MiaoYu** · 2026年09月08日 · v2.2
> 个人测试方法论沉淀——基于 AI 智能体（Claude Code / Codex）的 QA 测试工作流体系与全栈开发流水线。经过真实项目全流程实战验证。

## 这是什么

一套「双环（测试环+知识环）× 一主多从 × 双通道对抗」的 AI 测试工作流，经过真实项目（智能音箱类控制系统：服务端 + Android/iOS 双端）从零建立到实际运转的全流程验证；以及它所基于的全栈全自动开发流水线（六环节双视角对抗）。

**v2.2 相比 v2.0 的进化**：
- **实战产出**：真实的模块考古卡片（login/search/core/app）、正向+逆向用例、缺陷分诊矩阵
- **自动化脚本**：基线门禁（baseline-gate.py）、度量汇总（metrics-rollup.py）
- **真机上线手册**：从模拟器到真机的完整过渡指南
- **32 个实战迭代模板**：经过真实使用检验并优化
- **知识沉淀**：多智能体速度知识、UI 自动化全景、双对抗试点经验

## 目录

| 路径 | 内容 |
|------|------|
| [qa-workflow/](qa-workflow/) | **测试工作流包 v2.2** |
| [qa-workflow/qa-knowledge/](qa-workflow/qa-knowledge/) | 知识环（实战产出）：索引/仓库注册/设备池/业务映射/模块卡片/用例库/BUG库/报告库/审计/凭据 |
| [qa-workflow/workflow/qa/](qa-workflow/workflow/qa/) | 工作流核心：编排协议/拆分规则/门禁脚本/度量脚本/32模板（templates-v2）/任务卡示例 |
| [qa-workflow/runbooks/](qa-workflow/runbooks/) | 操作手册：真机上线/智能体编排/LLM代理修复 |
| [qa-workflow/reports/](qa-workflow/reports/) | 实战测试报告与分诊矩阵 |
| [qa-workflow/qa-overview.md](qa-workflow/qa-overview.md) | 一页架构总览 + 10分钟上手指南 |
| [qa-workflow/.claude/agents/](qa-workflow/.claude/agents/) | 五个从对话定义（考古/正向/逆向/执行/报告） |
| [qa-workflow/CLAUDE.md](qa-workflow/CLAUDE.md) | 主对话编排宪法 |
| [qa-workflow/docs/部署手册.md](qa-workflow/docs/部署手册.md) | 五步部署到新机器 |
| [docs/2026-09-02-qa-test-workflow-design.md](docs/2026-09-02-qa-test-workflow-design.md) | 设计文档（spec 原文） |
| [全栈全自动开发工作流.md](全栈全自动开发工作流.md) | 六环节开发流水线完整文档 |
| [工作流复刻手册-给智能体.md](工作流复刻手册-给智能体.md) | 给任意智能体的环境复刻操作手册（已脱敏） |

## 核心设计原则

| 原则 | 说明 |
|------|------|
| **一主多从** | 主对话只编排（拆解/派发/合并/裁决），从会话只执行 |
| **双环驱动** | 测试环（接单→执行→报告）+ 知识环（认知→沉淀→反哺）|
| **双通道对抗** | 正向×逆向（实体隔离互盲）、断言×视觉、白盒×黑盒 |
| **两层解耦** | 会话=任务单元（动态）/ 工作区=资产（静态）|
| **三源入口** | 人工指令 / GIT 事件 / 缺陷管理系统状态变更 |
| **证据纪律** | 无证据=未完成；BLOCKED≠测试失败 |

## 快速上手

1. 拷 `qa-workflow/` 到目标机器工作目录
2. 读 `qa-workflow/qa-knowledge/00-索引.md` 恢复状态
3. 按 `qa-workflow/workflow/qa/task-split-rules-v1.md` 拆分任务
4. 用 `templates-v2/05a-任务卡.yaml` 建卡执行
5. 证据落 `results/<任务ID>/`，知识回写 `qa-knowledge/`

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| **v2.2** | 2026-09-08 | 实战迭代：真实用例/自动化脚本/真机手册/模板优化/多智能体知识 |
| v2.1 | 2026-09-04 | 模板扩充：00-03 域 24 个（12 基础 + 12 实战），契约测试 |
| v2.0 | 2026-09-02 | 初始方法论：12 模板/五从对话/编排宪法 |
