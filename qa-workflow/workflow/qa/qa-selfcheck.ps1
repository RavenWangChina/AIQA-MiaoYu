[CmdletBinding()]
param(
    [string]$Root = ""
)

$ErrorActionPreference = "Stop"
$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
if ([string]::IsNullOrWhiteSpace($Root)) { $Root = Split-Path -Parent $scriptDirectory }
$problems = [System.Collections.Generic.List[string]]::new()

function Require-File([string]$RelativePath) {
    $path = Join-Path $Root $RelativePath
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        $problems.Add("Missing file: $RelativePath")
    }
}

function Require-Text([string]$RelativePath, [string[]]$Keywords) {
    $path = Join-Path $Root $RelativePath
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { return }
    $text = Get-Content -LiteralPath $path -Raw -Encoding UTF8
    foreach ($keyword in $Keywords) {
        if ($text -notlike "*$keyword*") {
            $problems.Add("$RelativePath missing field: $keyword")
        }
    }
}

Require-File "codex-qa-orchestration.md"
Require-File "templates/qa-task-card.yaml"
Require-File "[target-app]-orchestration.md"
Require-File "local-storage-governance.md"
Require-Text "codex-qa-orchestration.md" @(
    "Codex", "L1-L4", "status", "BLOCKED"
)
Require-Text "templates/qa-task-card.yaml" @(
    "task_id", "baseline", "allowed_operations", "data_label", "result_dir", "acceptance", "prohibited_operations", "test_matrix", "injection", "recovery", "evidence_required"
)
Require-Text "[target-app]-orchestration.md" @("[TARGET_APP]", "commit", "Git", "SSH")
Require-Text "local-storage-governance.md" @("E:\[TARGET_APP]", "F:\[TARGET_APP]-Toolchain", "G:\[TARGET_APP]-Data")

$taskCard = Join-Path $Root "templates/qa-task-card.yaml"
if (Test-Path -LiteralPath $taskCard -PathType Leaf) {
    $yaml = Get-Content -LiteralPath $taskCard -Raw -Encoding UTF8
    if ($yaml -notmatch 'task_id:\s*"SWAN-') { $problems.Add("task_id must use the SWAN prefix") }
    if ($yaml -notmatch 'data_label:\s*"(public|internal|test|sanitized|production-controlled)"') {
        $problems.Add("data_label is not an allowed data label")
    }
    if ($yaml -notmatch 'code_root:\s*"E:\\\\[TARGET_APP]') { $problems.Add("code_root must point to E:\\[TARGET_APP]") }
    if ($yaml -notmatch 'result_dir:\s*"F:\\\\[TARGET_APP]-Toolchain\\\\results') {
        $problems.Add("result_dir must point to F:\\[TARGET_APP]-Toolchain\\results")
    }
    if ($yaml -notmatch 'data_root:\s*"G:\\\\[TARGET_APP]-Data') { $problems.Add("data_root must point to G:\\[TARGET_APP]-Data") }
}

if ($problems.Count -gt 0) {
    Write-Output "QA self-check failed ($($problems.Count) item(s))"
    $problems | ForEach-Object { Write-Output "- $_" }
    exit 1
}

Write-Output "QA self-check passed"
Write-Output "Protocol, task card, orchestration, and E/F/G path rules passed field checks."
