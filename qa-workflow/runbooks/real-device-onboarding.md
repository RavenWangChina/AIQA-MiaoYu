# 实机（Android）接入 SOP

> 目标：实机接入后 30 分钟内完成登记，可承接 L3 蓝牙/音频/网络切换、L4 探索、性能测试。
> 设备到达前所有步骤可预检；到达当天按顺序执行即可。

## 1. 用户侧预置（设备接入前，人工 5 分钟）

1. 设置 → 关于手机 → 连续点击"版本号"7 次，开启开发者选项
2. 开发者选项 → 开启 **USB 调试**（Android 11+ 同时开启 **无线调试**）
3. （可选但推荐）开发者选项 → 开启"不锁定屏幕"，测试期间保持亮屏唤醒
4. 若测第三方登录相关场景：提前人工登录对应第三方 App（登录态预置，人机交接）

## 2. 连接与登记（设备到达当天，AI 执行）

```powershell
# USB 方式：数据线连接后
adb devices                      # 确认设备出现（状态 device 而非 unauthorized）

# 无线方式（Android 11+，推荐，脱离数据线）：
# 手机端：开发者选项 → 无线调试 → 配对码
adb pair <手机IP>:<配对端口>      # 输入手机显示的 6 位配对码
adb connect <手机IP>:<连接端口>
```

连接成功后采集登记信息（直接抄进 00c 设备池清单）：

```powershell
adb shell getprop ro.product.model          # 机型
adb shell getprop ro.build.version.release  # Android 版本
adb shell getprop ro.build.version.sdk      # API level
adb shell wm size; adb shell wm density     # 分辨率/密度
adb shell getprop ro.hardware               # 芯片平台
```

## 3. 能力保真度实测（登记必填）

| 项 | 方法 | 判定 |
|----|------|------|
| 音频 | 播放一段测试音频，`adb shell dumpsys audio` 无异常 | 可用/降级 |
| 蓝牙 | `adb shell dumpsys bluetooth_manager` 状态 Enabled；有 BLE 外设则试连一次 | 可用/缺失 |
| 传感器 | `adb shell dumpsys sensorservice` 列表非空 | 可用 |
| GPU | `adb shell dumpsys SurfaceFlinger \| grep GLES` 确认硬件 GPU | 可用 |
| 后台限制 | 厂商 ROM（MIUI/EMUI 等）检查电池优化白名单是否需要手动放行 [APP_PACKAGE] | 记录特殊项 |

## 4. 登记与准入

1. 在 `docs/qa-knowledge/00c-设备池清单.md` 设备清单**新增一行**：回填 adb 标识、能力保真度、状态置"空闲"
2. 基线核对：确认实机可安装的 App 版本与当前测试基线（App `dev@4d1ed7b1`）一致，不一致先报主对话裁决
3. 准入后即可承接：L3 蓝牙/音频/网络切换、L4 探索、性能/流畅度（映射表见 00c）

## 5. 占用纪律（与 AVD 同规则）

- 开工登记占用（任务 ID），收工回写释放
- **2026-09-07 事故教训**：多会话开工前必须先查 00c 占用表，AVD 同刻只允许 1 任务
- 实机被测试占用时，其他会话不得执行 adb install/uninstall 等破坏登录态的操作

## 6. 首轮验证（接入当天建议）

- 安装基线 APK → 冷启动 → 确认登录页可达（对照 BUG-20260904-004 的 ANR 现象在真机是否复现，作为 P-003 模式的真机对照样本）
- 结果记入 `results/<task_id>/evidence/`，若真机无 ANR 而模拟器有 → device-divergence 入模式库
