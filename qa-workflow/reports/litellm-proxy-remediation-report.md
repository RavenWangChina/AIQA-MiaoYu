# LiteLLM 代理问题 2 修复报告

## 当前证据

- `GET /health/liveliness` 返回 `200`。
- `GET /health/readiness` 返回 `200`，状态为 `healthy`，数据库为 `connected`。
- `/health/readiness` 报告 LiteLLM 版本为 `1.82.1`，`cache` 为 `null`。
- 当前路由 `[company-]default` 的普通 Responses 请求成功。
- `store=true` 加 `previous_response_id` 的连续请求成功。
- `function_call` 加 `function_call_output` 的连续请求成功。

## 根因判断

客户端和代理的基础 Responses 状态续接目前可用；历史子会话错误主要由旧请求状态/高负载引起。多实例共享状态尚未成立，因为代理健康信息显示 `cache: null`。此外，LiteLLM `1.82.1` 低于官方 Responses 文档对 `encrypted_content_affinity` 要求的 `1.82.3` 最低版本。

## 管理员实施项

1. 先在维护窗口升级 LiteLLM 至不低于 `1.82.3`，并记录实际版本。
2. 提供高可用 Redis，设置 `REDIS_URL`，确认所有代理节点使用同一 Redis 命名空间。
3. 启用 `responses_api_deployment_check`、`encrypted_content_affinity`、`session_affinity` 和 `deployment_affinity`。
4. 启用后台健康检查和健康路由；设置失败计数、冷却时间、超时和有限重试。
5. 将 `[company-]default` 的回退目标绑定到已验证健康的独立模型组，不使用不存在或未探测的模型名。
6. 重启后确认 `/health/readiness` 的 `litellm_version` 已更新且 `cache` 不再为 `null`。

## 验收顺序

1. 单节点普通 Responses 请求。
2. 同一 `previous_response_id` 的连续请求。
3. `function_call` → `function_call_output` → 连续响应。
4. 两个代理节点之间交替发送第 2、3 项请求，确认状态和工具调用不中断。
5. 人工制造一次超时/认证失败，确认部署进入 cooldown，再由健康检查恢复。
6. 最后再逐个唤醒 Codex 专项会话；不要用历史卡住的任务做首次验收。

## 边界

本地已完成诊断和配置模板，未修改远端 LiteLLM、Redis、数据库或代理容器。远端升级、Redis 接入和重启必须由拥有代理基础设施权限的管理员执行。
