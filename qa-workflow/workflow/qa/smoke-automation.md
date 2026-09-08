# 定时冒烟（默认禁用纪律）
- 脚本: E:\[TARGET_APP]\scripts\test\smoke-runner.ps1（adb版）；Maestro Flow 版: .maestro\smoke_first.yaml（已验证通过，可逐步扩充断言）
- 启用: 人工运行 smoke-enable.ps1；禁用: smoke-disable.ps1
- 当前状态: 未启用
- Maestro 问题已解决：flow 头部与命令序列之间必须加 YAML 文档分隔符 `---`（此前误判为环境问题）
