# 多智能体编排与 UI 自动化提速知识（2026-09-07 第二轮联网学习）

> 来源：Anthropic 工程博客（多智能体研究系统）、Claude Code 官方文档（subagents）、Android 官方文档（emulator 命令行）、Maestro 官方文档。服务于框架 v1.1→v1.2 的演进依据。

## 一、主从调度（orchestrator-worker）可复用规则

来自 Anthropic 多智能体系统工程经验：

1. **委派四要素**：任务描述必须含 目标 / 输出格式 / 可用工具指引 / 边界——缺失会导致从对话误解或重复劳动。我们的 05a 任务卡已覆盖，继续坚持。
2. **规模按复杂度伸缩**：简单核验 1 从 3-10 次工具调用；对比类 2-4 从；只有复杂研究才 10+。防过度投入。宪法"并发 ≤3"与此一致。
3. **失败恢复 = 从断点续跑，不整体重来**：配合 progress.md 红绿灯 + 05f 审计，卡在哪从哪续。
4. **产物落盘 + 轻量引用回传**：多级传递会失真且耗 token，我们的"产物落知识库、回传摘要+路径"正是官方同款设计。
5. **终态评估而非过程核对**：复核从对话看结果与证据，不苛求步骤路径一致。
6. **何时不用多智能体**：步骤强依赖、需共享上下文的任务留在主对话（官方点名多数编码任务如此）——对应我们：单文件小修不派考古从。
7. 多智能体 token 成本约为单对话 15×：**分片制也是成本闸门**，每片 ≤3 单元天然限制了单从膨胀。

## 二、Claude Code 子代理机制要点（直接影响 v1.2）

1. **⭐ 分片 + 恢复（resume）组合**：`SendMessage` 可恢复已完成的子代理并**保留其全部上下文**——比每片新开执行从更优：设备状态认知、locator 试错结论、账号会话态在片间不丢。规则：**每批次 spawn 一个执行从跑首片，后续片用 SendMessage 恢复同一执行从**；progress.md 仍是磁盘事实源（防会话重启丢上下文）。
2. **maxTurns**：可为执行从设回合上限，触顶输出标记 partial、可恢复续跑——天然防失控。
3. **memory: project**：子代理可带持久记忆（推荐模式"先查记忆、完成后更新"）——执行从可跨轮记住 locator 经验、设备怪癖。已为 qa-executor 启用。
4. 并发上限默认 20、嵌套深度 3：我们的 ≤3 并发在安全区。
5. 子代理转录独立保存于 `~/.claude/projects/<project>/<sessionId>/subagents/`——事后审计可用（05f 的机器侧补充）。
6. agent 文件改动即时生效（监听 agents 目录），无需重启。

## 三、UI 自动化提速清单（按收益排序）

| 提速项 | 方法 | 预期收益 | 状态 |
|--------|------|----------|------|
| **关闭系统动画** | `adb shell settings put global window_animation_scale/transition_animation_scale/animator_duration_scale 0.0` | UI 自动化最大单项提速（官方 Cloud disableAnimations 的本地等价） | ✅ 脚本 `E:\[TARGET_APP]\scripts\device-speed-prep.ps1`，执行从每片开跑前执行 |
| **Quick Boot 快照启动** | 不加 `-no-snapshot*` 直接启动 | 冷启动 5 分钟 → 秒级恢复 | 已配（forceFastBoot=yes），开机规范更新 |
| **轮询断言代替 sleep** | Maestro `assertVisible` 自带等待 | 每步省 1-5s 固定等待 | 已入 02-L2 模板 |
| **本地分片并行** | `maestro test --shard-split N`（多设备时切分套件） | N 台设备近 N 倍 | 宿主机 15.7G 暂只跑 1 台模拟器，实机到位后可 1模拟器+1真机并行 |
| **无头跑批** | 批量/夜间用 `-no-window -no-audio -no-boot-anim`（窗口合成开销归零） | 交互轮不适用（要可见性），仅跑批 | 已入 00c 规范 |
| **保持唤醒** | `svc power stayon true` | 防中途锁屏打断 | ✅ 并入 speed-prep 脚本 |
| YADB 快速输入 | Midscene 栈的输入优化组件 | 文本输入提速 | 观望（Midscene 试点时一并验证） |

## 四、与宪法/模板的联动（本轮已落地）

- 宪法"分片调度"升级为 **spawn 首片 + SendMessage 恢复续片** 协议
- qa-executor：启用 `memory: project` 持久记忆；每片开跑前执行 speed-prep 脚本
- 模拟器开机规范：默认 Quick Boot，仅配置变更后冷启动一次

## 来源

- [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/built-multi-agent-research-system)
- [Claude Code Docs: Subagents](https://code.claude.com/docs/en/sub-agents)
- [Android Emulator 命令行](https://developer.android.com/studio/run/emulator-commandline)
- [Maestro 文档（ask 接口）](https://docs.maestro.dev/)
