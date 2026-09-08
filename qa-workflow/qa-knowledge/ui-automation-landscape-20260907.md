# UI 自动化测试领域知识（2026-09-07 联网学习沉淀）

> 来源：Maestro 官方文档、Midscene 官方仓库、Patrol 官网（链接见文末）。服务于本工作流 L1-L4 分层与双通道设计。

## 一、工具格局与本工作流的分层映射

| 层 | 工具 | 定位 | 采纳建议 |
|----|------|------|----------|
| L1/L2 源码级（白盒） | **Patrol 4.x** | flutter `integration_test` 增强：纯 Dart 处理**原生交互**（权限弹窗/系统通知/WebView/开关 Wi-Fi），测试全隔离、分片执行、Hot Restart，带 DevTools 扩展看原生视图树 | FlutterApp 原生交互场景首选；需在 App 仓加 dev 依赖 |
| L2/L3 UI 黑盒 | **Maestro 2.10**（已装） | YAML 流程驱动，架构无关，模拟真人交互；嵌套 Flow/循环/条件/Hook/JS 扩展；Studio 可视化编排 | 主力执行工具；用例即脚本（正向从可直接产出 YAML） |
| 视觉断言通道 | **Midscene**（候选，MIT） | 截图驱动的 GUI Agent：`aiAssert` 自然语言视觉断言（颜色/高亮/布局/原生界面）、`aiQuery` 结构化提取；Android 底层走 **scrcpy + appium-adb + YADB**（与我们已装的栈同源）；同套 API 覆盖 Android/iOS/HarmonyOS | **补双通道"视觉腿"的最佳候选**；模型可自托管（见下），可接本地 LiteLLM 代理 |
| 复杂原生/深度矩阵 | Appium 2.x | 生态最大（多语言/驱动插件化），混合应用与复杂手势 | 备选，不为用而用（防过度工程） |

## 二、Maestro 官方防 flaky 规范（写用例必读）

1. **选择器优先级**：稳定文本 `text` > 资源 `id`（图标/本地化/动态 UI 用） > 关系选择器（`below/childOf` 等） > 状态条件（`enabled: true`，Maestro 自动等待） > `index` 兜底。**不推荐坐标**。
2. **轮询断言代替 sleep**："Golden rule"——该出现/消失的东西用 `assertVisible` / `assertNotVisible`，命令自带轮询，禁止写死等待。
3. **有动画先 `waitForAnimationToEnd`**；长网络操作用 `extendedWaitUntil` 设真实超时。
4. **幽灵点击**：`tapOn` 加 `retryTapIfNoChange: true`。
5. 推荐模式：`tapOn: {text: X, enabled: true}` + `assertVisible: 结果` 组合，全程无固定 sleep。
6. locator contract 约定（对齐 005 任务）：优先 text/id 语义锚，坐标只做最后手段——给开发的提测要求应包含关键按钮的 resource-id 可用性。

## 三、Midscene 模型方案（对本地环境的适配性）

- 官方支持模型：**Qwen3.x、Doubao-Seed-2.1、GLM-4.6V、gemini-3.5-flash、UI-TARS**（含可自托管开源选项）
- 本地有 LiteLLM 代理（[PROXY_IP]:4000）——VLM 调用可路由到 Qwen/GLM 系，无需出海 API；截图方式不传大 DOM，成本可控（官方示例 60 任务 $0.59）
- `@midscene/test`（Beta）为 YAML 声明式 E2E，与 Maestro 用例风格接近
- AndroidWorld 基准 Pass@1 93.1%（Gemini-3.5-Flash），能力成熟度可用

## 四、遗留衔接

- 双通道"视觉腿"缺工具（审计#6）→ Midscene 是首选方案，**待用户决策后装机试点**
- 模拟器流畅度 → Quick Boot 快照启动 + 批量跑用 `-no-window`（00c 已录）
- Flutter 白盒原生交互（审计未列的增强点）→ Patrol 可在 Core 门禁解除后于 App 仓试点，用于权限弹窗/通知类 L3 场景（这类场景 Maestro 天然吃力）

## 来源

- [Maestro 文档](https://docs.maestro.dev/)（含命令参考 ask 接口）
- [Midscene GitHub](https://github.com/web-infra-dev/midscene)（midscenejs.com）
- [Patrol 官网](https://patrol.leancode.co/)
