# Flutter 垂直切片 QA 工作流知识条目

## 可复用规则

- 正式仓库基线必须记录分支、完整 commit 和工作树状态；已有未提交变更不得被验证过程覆盖。
- 任何会生成 `.dart_tool`、锁文件或构建产物的命令，都在 `E:\[TARGET_APP]\artifacts\local-test\<任务ID>` 隔离副本执行，结果只归档到 `F:\[TARGET_APP]-Toolchain\results\<任务ID>`。
- Flutter CLI 运行前先做 SDK lockfile 的 Dart 写入探针；原生 shell 能写不代表 Dart/Flutter 运行时能写。
- L2 命令必须保留完整输出、退出码、时间和工具版本；同一环境错误阻断时，不将其误报为业务测试失败。
- 逆向注入必须独立隔离，至少覆盖缺失 Core、离线解析、无 Android 设备和非法任务状态；每项都要有状态、原因和恢复条件。
- 固定会话只有在统一探针状态为 `READY` 时才允许作为依赖；缺失探针时记录 `STARTUP_BLOCKED` 并降级到已批准临时代理。
- 固定任务因平台高需求失败后，优先向原任务发送恢复探针并等待 `active/inProgress`；不得重复创建任务或把 `active` 误报为 `READY`。
- ADB/Maestro 设备层必须先验证用户目录可写和 `adb devices` 的确定性退出码；无设备或目录权限问题只能标记环境阻塞，不能伪造 UI 通过。

## 本轮结论

Flutter SDK lockfile 与 Android 用户目录权限已修复；L2 已通过。L4 仍受 cmdline-tools/模拟器限制，固定会话恢复到 `active/inProgress` 但尚未返回 `READY`。

## 证据入口

`F:\[TARGET_APP]-Toolchain\results\TASK-20260903-001-flutter-vertical-workflow\summary.md`
