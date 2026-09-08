# BUG 报告：BUG-20260904-004

- 任务：`TASK-20260904-005-search-execution`
- 分类：`broken`（运行时 ANR 候选，未形成 L2 业务断言）
- 模块：`[APP_PACKAGE]` 启动 / `MainActivity`
- 基线：App `dev@[COMMIT_HASH]`
- 现象：首次启动探针出现系统对话框 `[TARGET_APP] isn't responding`；随后 hierarchy 复核进入登录页，暂未稳定复现。
- 证据：`F:\[TARGET_APP]-Toolchain\results\TASK-20260904-005-search-execution\evidence\maestro-hierarchy.txt`、`anr-recheck.png`、`anr-recheck-hierarchy.txt`
- 结论：记录为间歇性 ANR 候选；不计入搜索 L2 失败，不得在未重复复现前提单。
- 后续：独立 ANR/性能任务复现，确认主线程堆栈后再决定提单。
