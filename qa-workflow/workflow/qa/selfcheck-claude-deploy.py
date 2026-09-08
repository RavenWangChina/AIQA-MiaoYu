# -*- coding: utf-8 -*-
"""[TARGET_APP] QA 工作流 · Claude Code 部署自检。
用法：python docs/workflow/qa/selfcheck-claude-deploy.py（在 F:\\[TARGET_APP]-Toolchain 执行亦可）
退出码：0=全部通过；1=有缺失。"""
import os
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(r"F:\[TARGET_APP]-Toolchain")
AGENTS = ["qa-archaeologist", "qa-case-positive", "qa-case-negative", "qa-executor", "qa-reporter"]
TEMPLATES = [
    "00-索引.md", "00b-仓库注册表.md", "00c-设备池清单.md",
    "01-接口清单.md", "01-架构总览.md", "01-模块卡片.md", "01d-环境依赖卡.md",
    "02-L1冒烟.yaml", "02-L2功能.yaml", "02-L3场景.yaml", "02-L4探索.md",
    "02e-性能用例.yaml", "02f-稳定性场景.yaml", "02g-兼容矩阵.yaml", "02h-安全用例.yaml",
    "02i-升级迁移用例.yaml", "02j-设备在环用例.yaml", "02k-逆向对抗矩阵.yaml",
    "03-BUG报告.md", "03-模式库.md", "03c-BUG状态跟踪表.md", "03d-flaky登记表.md",
    "05a-任务卡.yaml", "05b-任务拆分单.md", "05c-新仓接入检查单.md",
    "05d-准入检查单.md", "05e-回归触发登记.md", "05f-审计日志.md", "05g-凭据清单.md",
]
CONSTITUTION_SECTIONS = ["你是主对话", "标准编排", "任务卡纪律", "检查点规则", "证据纪律", "从对话管理", "目录地图"]

errors, warnings = [], []

def check(cond, msg, warn=False):
    if not cond:
        (warnings if warn else errors).append(msg)

# 1. 宪法
claude_md = ROOT / "CLAUDE.md"
check(claude_md.is_file(), "CLAUDE.md 不存在")
if claude_md.is_file():
    text = claude_md.read_text(encoding="utf-8")
    for s in CONSTITUTION_SECTIONS:
        check(s in text, f"CLAUDE.md 缺少章节关键词：{s}")
    check("docs/qa-knowledge" in text, "CLAUDE.md 未指向本地知识库路径")

# 2. 五个从对话
for a in AGENTS:
    p = ROOT / ".claude" / "agents" / f"{a}.md"
    check(p.is_file(), f"从对话定义缺失：{p}")
    if p.is_file():
        head = p.read_text(encoding="utf-8")[:400]
        check("name: " in head and "tools: " in head, f"{a}.md frontmatter 不完整")
        check("docs/qa-knowledge" in p.read_text(encoding="utf-8"), f"{a}.md 未锚定本地知识库路径")

# 3. 模板 v2（29 个）
troot = ROOT / "docs" / "workflow" / "qa" / "templates-v2"
for t in TEMPLATES:
    check((troot / t).is_file(), f"模板缺失：{t}")

# 4. 知识库实例
kb = ROOT / "docs" / "qa-knowledge"
for f in ["00-索引.md", "session-state.md", "03-BUG库/模式库.md",
          "01-系统认知/模块卡片-app.md", "01-系统认知/模块卡片-core.md", "01-系统认知/模块卡片-search.md",
          "04-报告库/周期汇报-20260904-首版.md"]:
    check((kb / f).is_file(), f"知识库文件缺失：{f}")
check((kb / "03-BUG库" / "模式库.md").is_file() and "P-001" in (kb / "03-BUG库" / "模式库.md").read_text(encoding="utf-8"),
      "模式库.md 未实例化（应含 P-001 起的条目）")

# 5. 结果目录与任务产物
for d in ["results/TASK-20260904-001-flutter-l1l2", "results/TASK-20260904-003-search-merged",
          "results/TASK-20260904-005-search-execution"]:
    check((ROOT / d).is_dir(), f"结果目录缺失：{d}", warn=True)

# 6. 工具链
for tool, ver_arg in [("k6", "version"), ("allure", "--version"), ("issue-tracker", "version")]:
    check(shutil.which(tool) is not None, f"工具不在 PATH：{tool}", warn=True)
check(shutil.which("maestro") is not None or (Path.home() / "maestro" / "bin" / "maestro.bat").is_file(),
      "Maestro 不可用", warn=True)
_scrcpy_hits = list(Path.home().glob("AppData/Local/Microsoft/WinGet/Packages/Genymobile.scrcpy*/**/scrcpy.exe")) if (Path.home() / "AppData/Local/Microsoft/WinGet/Packages").is_dir() else []
check(shutil.which("scrcpy") is not None or _scrcpy_hits, "scrcpy 不可用（PC 端录屏/镜像证据工具）", warn=True)
check(Path("F:/[TARGET_APP]-Toolchain/sdks/android-sdk/platform-tools/adb.exe").is_file(), "adb.exe 缺失", warn=True)
check("maestro" in os.environ.get("Path", "").lower() or
      any("maestro" in p.lower() for p in os.environ.get("Path", "").split(";")),
      "Maestro 未入当前进程 PATH（新开的 Claude Code 会话会生效）", warn=True)

# 7. 缺陷管理系统 MCP
settings = Path.home() / ".claude" / "settings.json"
check(settings.is_file(), "~/.claude/settings.json 不存在")
if settings.is_file():
    stext = settings.read_text(encoding="utf-8")
    check("issue-tracker-cli" in stext, "缺陷管理系统 MCP 未注册到 Claude Code")
    check('"git"' in stext, "Git MCP 未注册到 Claude Code")
git_exe = Path(r"F:\[TARGET_APP]-Toolchain\mcp-server-git\venv\Scripts\mcp-server-git.exe")
check(git_exe.is_file(), "mcp-server-git.exe 不存在")
check(bool(os.environ.get("ZENTAO_URL")), "ZENTAO_URL 环境变量未设置", warn=True)

# 8. 全局部署（VS Code 插件主入口：任意工作目录可用）
global_agents = Path.home() / ".claude" / "agents"
for a in AGENTS:
    p = global_agents / f"{a}.md"
    check(p.is_file(), f"全局从对话缺失：{p}")
    if p.is_file():
        body = p.read_text(encoding="utf-8")
        check("F:\\[TARGET_APP]-Toolchain" in body, f"全局 {a}.md 缺少绝对根锚点")
global_md = Path.home() / ".claude" / "CLAUDE.md"
check(global_md.is_file(), "全局 CLAUDE.md（C:\\Users\\swan\\.claude\\CLAUDE.md）不存在")
if global_md.is_file():
    g = global_md.read_text(encoding="utf-8")
    check("F:\\[TARGET_APP]-Toolchain\\CLAUDE.md" in g, "全局 CLAUDE.md 未路由到 QA 宪法")
    check("session-state.md" in g, "全局 CLAUDE.md 未指向会话状态回写文件")

print(f"selfcheck：{len(errors)} 项失败，{len(warnings)} 项警告")
for e in errors:
    print(f"  [FAIL] {e}")
for w in warnings:
    print(f"  [WARN] {w}")
if not errors:
    print("selfcheck 全部通过")
sys.exit(1 if errors else 0)
