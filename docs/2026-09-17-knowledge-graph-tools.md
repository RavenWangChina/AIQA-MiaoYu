# 知识图谱工具选型与实战记录

> 2026-09-17 · 为「项目知识地图 / 功能域可视化 / 建站素材」调研的知识图谱类工具全景
> 结论先行:**CodeGraph(日常问答机)+ graphify(周期体检仪)双图谱并行**,其余评估后未采用

## 一、主力双图谱(已装已实战)

### CodeGraph — agent 的日常问答机

- 仓库:github.com/colbymchenry/codegraph(Rust 内核,npm `@colbymchenry/codegraph`)
- 定位:代码知识图谱。一次 `explore` 调用 = 相关符号源码 + 调用路径(含 grep 追不到的动态分发)+ 改动影响面(blast radius)
- 实测:建图秒级(约 200 文件 / 4200 节点 1.4s)、免费、纯代码、查询秒回
- 用法:查询**点名符号/文件名**效果最佳;有 `.codegraph/` 目录的仓优先用它替代 grep/读文件
- 已知代价:重 explore 会话驻留上下文偏高(官方实测 +80%),小窗口长会话注意提前压缩

### graphify — 人的地图

- 仓库:github.com/Graphify-Labs/graphify(Python,`uv tool install "graphifyy[leiden]"` + skill)
- 定位:项目知识地图。代码(tree-sitter 确定性 AST)+ 文档 + 图像进同一张图,Leiden 社区检测、god nodes、模块健康度、意外连接
- 实测(约 200 文件试点仓):AST 秒级;文档/图像语义提取需 subagent 并行(10 个 chunk 约 20 分钟);产出 **4,759 节点 / 7,382 边 / 271 社区**(社区经批量命名后全部中文可读),graph.html(交互力导向图)/graph.svg/graph.json 三态输出
- 用法:`--update` 增量(语义缓存,未变更文档零成本);建站/汇报素材首选 graph.json
- 已知坑:install 会往 CLAUDE.md 尾部追加无 marker 段(装后检查清理);部分数据库方言需 `graphifyy[sql]` 可选件

### 双图谱分工(定稿)

| | CodeGraph | graphify |
|---|---|---|
| 节奏 | 每次开发会话 | 按里程碑/周期 |
| 速度 | 秒级 | 分钟级(语义提取) |
| 覆盖 | 纯代码 | 代码+文档+图像 |
| 产出 | agent 消费的上下文 | 人看的地图+健康度+可视化 |
| 角色 | **手术导航**(影响面/调用链) | **体检报告**(该拆什么/文档缺口) |

交替工作流:**graphify 发现病灶(低内聚社区)→ CodeGraph 拿 blast radius 做手术导航 → graphify 重跑复查内聚度**。

## 二、评估后未采用(记录原因,防止重复调研)

| 项目 | 定位 | 未采用原因 |
|------|------|-----------|
| ruflo(ruvnet) | agent meta-harness,内含 knowledge-graph 插件与 RuVector(Graph RAG 库) | 全量安装为接管级侵入(改写 CLAUDE.md + 大量 hooks + daemon);仅摘其 cost-tracker 单点组件使用 |
| pro-workflow(rohitg00) | SQLite+FTS5 自纠错记忆 + 自动生长研究 wiki | 概念最佳但 37 hook 脚本 × 24 事件接管级;与既有文件式记忆体系冲突 |
| ECC(affaan-m) | 260k⭐ 大而全 harness | 同 ruflo 类,定调不引入接管式框架 |

## 三、配套生态

| 工具 | 与图谱的关系 |
|------|-------------|
| crawl4ai(unclecode) | 批量网页 → 干净 Markdown(实测去噪约 48%);作为 graphify `add` 的数据源,把外部资料并入知识图 |
| punkpeye/awesome-mcp-servers(95k⭐)、Awesome-MCP-ZH(7.7k⭐) | MCP 服务器目录,检索类/图谱类服务选型先翻它 |

## 四、经验沉淀

- 语义提取的 subagent 分发:按目录分组切 chunk(20-25 文件/组,图像独占),一份计划文件让各 subagent 自取清单,避免长 prompt 转抄出错
- 社区命名:聚类结果先出 top 命名,其余批量派 subagent 按成员符号模式命名(如 `前端·草稿页`/`服务端·数据库层`),重导出即得全中文可读地图
- playwright 浏览器内核装不上(CDN 不通假死):组网内已装机器物理拷贝 `ms-playwright` 目录,版本号对上即用
- 接入纪律:外部工具改写宪法/工作流文档仅限 marker 段且装后 diff 人审;新仓建图 = 用户决定
