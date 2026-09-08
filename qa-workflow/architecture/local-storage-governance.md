# [TARGET_APP] 本地路径与文档归档规范

## 固定盘符职责

| 盘符 | 根目录 | 用途 | 禁止存放 |
| --- | --- | --- | --- |
| `E:` | `E:\[TARGET_APP]` | Git 工作树、测试脚本、项目级配置模板、可重建构建缓存 | IDE 安装包、生产数据、正式过程文档 |
| `F:` | `F:\[TARGET_APP]-Toolchain` | IDE 与 SDK、离线安装包、过程文档、测试结果、版本清单 | Git 工作树、生产数据、运行中数据库 |
| `G:` | `G:\[TARGET_APP]-Data` | 临时数据、脱敏数据库快照、测试运行数据、受控生产导入、可回收日志 | 源代码、工具安装、未加密敏感导出 |

所有项目使用 `[TARGET_APP]` 命名空间；不复用盘内既有的 `swan`、`db` 或临时目录。

## E 盘：代码与可重复运行资产

```text
E:\[TARGET_APP]\
  repos\
    mobile-native\        Android 与 iOS 检出
    flutter\              FlutterApp、Flutter Core、FlutterModule 检出
    server\               Server、Server-AI 检出
  scripts\
    bootstrap\            环境核验与初始化脚本
    test\                 跨项目测试入口
    maintenance\          只读检查、清理建议、备份编排
  config-templates\       不含密钥的 .env、Compose、运行配置模板
  cache\
    gradle\ pub\ npm\ maven\
  artifacts\
    build\                可重建构建产物
    local-test\           本地测试临时产物
```

仓库目录以 `项目名__分支` 命名，例如 `[company-]network_flutter_core__dev`。每次测试在 `E:\[TARGET_APP]\artifacts\local-test\<任务ID>` 写入可删除产物；长期证据归档到 F 盘。

## F 盘：工具链、过程与结果证据

```text
F:\[TARGET_APP]-Toolchain\
  apps\                  Android Studio、Flutter SDK、JDK、Docker Desktop 等安装位置
  sdks\                  Android SDK、Flutter 版本、离线工具链
  installers\            可验证来源的安装包与校验信息
  docs\
    architecture\         架构、版本矩阵、API 契约
    runbooks\             启动、故障、恢复、发布操作手册
    decisions\            ADR/关键决策记录
    meeting-notes\        需求与讨论纪要
  results\
    <任务ID>\             命令记录、测试报告、截图、日志摘录与结论
  manifests\
    environment\          工具版本、PATH/SDK 配置、设备清单
    repositories\         检出基线、远端、分支与 commit
    data\                 快照来源、脱敏版本、校验和、保留期
  archives\
    releases\             经确认需要保留的安装包/发布产物
    reports\              阶段报告与历史结果
```

安装 IDE 与 SDK 前，先在 `F:\[TARGET_APP]-Toolchain\manifests\environment` 记录版本、来源、校验和、安装日期和用途。每项任务结束在 `F:\[TARGET_APP]-Toolchain\results\<任务ID>` 留下可复查证据。

## G 盘：数据分级与生命周期

```text
G:\[TARGET_APP]-Data\
  incoming\              外部接收、尚未审计的数据
  temporary\             单次构建/导入的可回收中间数据
  test\
    database\             本地测试数据库卷、迁移结果、种子数据
    fixtures\             可公开或脱敏的测试样本
    device-captures\      设备/网络抓包；按权限与保留期管理
  snapshots\
    sanitized\            脱敏数据库快照及恢复说明
    production-controlled\ 受控生产数据副本，默认空目录
  exports\                经审批的结果导出
  quarantine\             待审计、待脱敏、不得被程序读取的数据
  logs\                   可归档的原始运行日志
```

数据标签：`public`、`internal`、`test`、`sanitized`、`production-controlled`。`production-controlled` 仅在用户明确批准来源、范围、脱敏方式、访问人和保留期后写入；不能被本地服务的默认配置自动加载。

## 命名与归档规则

- 任务 ID：`SWAN-YYYYMMDD-序号-主题`，例如 `TASK-20260901-001-env-audit`。
- 结果目录、日志、截图、数据库快照均以任务 ID 开头；日期使用 `YYYY-MM-DD`。
- 文档目录只保存 Markdown、PDF、图片与结构化清单；机密不写入文档、命令历史或 Git。
- 每个任务的结果目录至少包括 `summary.md`、`commands.txt`、`evidence/` 和 `risks.md`；没有执行的项目写明原因。
- 任何清理、覆盖、迁移、导入、生产数据拷贝、提交或推送均需主会话与用户按现有审批规则确认。

## 主会话记忆与派发规则

主会话以本文件、`[target-app]-orchestration.md`、`workflow-codex-agents.md` 和 F 盘 `manifests` 为持久事实来源。专项会话接收任务时必须带上：任务 ID、根目录、版本基线、允许操作、数据标签、结果目录和验收条件。

专项会话回报时必须提供：实际路径、实际 commit、工具版本、执行命令、证据目录、数据标签、阻塞项与下一步建议。主会话复核后更新对应 manifest，才可将结果作为下一任务的输入。
