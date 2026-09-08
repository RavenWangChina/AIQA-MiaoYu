# 全栈开发流水线（Codex 版）

此文件是 Codex 的全局开发工作流。它不配置模型、网关、API 密钥、账号或自动绕过安全确认；这些设置由 Codex 运行环境和用户单独管理。

## 适用范围

- 对新功能、行为变更、组件新增、缺陷修复和重构，依次执行下列六个环节。
- 纯文档编辑、调研回答或用户明确要求跳过某阶段时，可采用相称的精简流程，并说明省略的环节。
- 项目内 `AGENTS.md` 的更具体约束优先；系统的安全、审批与权限策略始终优先于本文件。

## 六环节流水线

| 环节 | 固定方法 | 完成条件 |
| --- | --- | --- |
| 1. 需求挖掘 | 用 `superpowers:brainstorming` 从工程角度梳理边界、失败路径和数据流；用 `product-design:user-context` 或 `product-design:research` 从用户、价值与优先级交叉检验。 | 两个视角的结论一致，或分歧已由用户裁决。 |
| 2. 方案设计 | 用 `superpowers:writing-plans` 形成可持久保存的分步计划：目标文件、改动、验证方式。让独立子代理审查计划的调用方、边界、依赖顺序和测试缺口。 | 每条审查意见均记录采纳方式，或写明不采纳的技术理由。 |
| 3. 执行 | 用 `superpowers:test-driven-development` 遵循红→绿→重构；用 `superpowers:subagent-driven-development` 按计划拆分执行。无依赖工作可用 `superpowers:dispatching-parallel-agents` 并行。 | 每个子任务有先失败、后通过的测试证据，或明确说明为何不可测试。 |
| 4. 审查 | 用 `superpowers:requesting-code-review` 和 `codex review` 审查本地 diff；再用 `coderabbit:coderabbit-review` 进行独立复审。 | 两条审查通道均无未处理的阻塞问题；对意见先验证，再用 `superpowers:receiving-code-review` 处理。 |
| 5. 验证 | 用 `superpowers:verification-before-completion` 获取可复查证据。后端改动运行项目测试；UI 改动用 Browser/Chrome 工具实际操作并保留截图。 | 呈现真实命令输出或截图；没有证据不得宣称完成。 |
| 6. 提交 | 使用现有提交历史决定提交信息风格。 | 仅在用户明确要求 `commit`、提交、推送或创建合并请求时执行。 |

## 检查点

只在以下情况暂停并请用户决定：

1. 需求分歧：工程与产品视角对范围、优先级或行为得出不同结论。列出各自理由，不自行取舍。
2. 方案级取舍：架构二选一、引入生产依赖、改变公共接口或数据迁移。给出推荐与权衡。
3. 不可逆或外部动作：提交、推送、创建合并请求、发送消息、修改权限、删除或覆盖重要数据。说明目标并取得明确确认。

在这些检查点以外，阅读代码、写测试、实现、运行验证和汇报进展应主动推进；但仍遵守 Codex 的系统级安全和审批要求。

## 质量纪律

- 发现缺陷时先用 `superpowers:systematic-debugging` 定位根因；修复应放在所有调用方共同经过的层，而非只掩盖报错路径。
- 计划、关键决策、审查处理和验证证据应保存在项目文档或任务输出中，不依赖跨会话记忆。
- 每次声明完成时，列出改动、验证证据和仍存在的限制；不要以推测替代执行结果。
- 安全敏感变更或专门安全审查，使用 `codex-security:security-scan` 或 `codex-security:security-diff-scan`。
- 产品与前端工作可按需使用 `product-design`、`build-web-apps` 和 Browser 插件；不要为了使用插件而扩大任务范围。

## 开发自动化验证层

- **Web UI**：先用 Browser 做探索与人工可见确认；需要可重复的开发验证或回归检查时，用 `playwright-dev` MCP。优先角色、标签和稳定的测试 ID，不用坐标或仅依赖截图。
- **Mobile UI**：有 Android 模拟器、iOS 模拟器或支持的移动 Web 目标时，用 `maestro` MCP 检查界面并生成/维护 YAML Flow。CI 只运行确定性的 YAML，不在 CI 中调用模型。
- **桌面 GUI**：Codex Computer Use 与 UI-TARS 只用于用户明确提出的桌面界面任务。它们是视觉探索与兜底工具，不进入默认开发验收；使用前确认目标窗口和允许的动作。
- `awesome-computer-use` 是选型目录而非依赖。除非某个项目的明确需求和隔离策略已经确定，不从其中批量安装桌面控制框架。
- 没有可用模拟器、账户或测试数据时，完成其他可用验证并在交付说明中明确缺口；不得把“无法运行 UI 自动化”表述为“已验证”。
