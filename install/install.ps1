# Install the saas-ai-audit skill into %USERPROFILE%\.claude\skills\
# Usage: .\install\install.ps1

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Target = Join-Path $env:USERPROFILE ".claude\skills\saas-ai-audit"

Write-Host "-> Target: $Target"

if (Test-Path $Target) {
    $confirm = Read-Host "Skill already installed. Overwrite? [y/N]"
    if ($confirm -ne "y" -and $confirm -ne "Y") {
        Write-Host "Aborted."
        exit 0
    }
    Remove-Item -Recurse -Force $Target
}

New-Item -ItemType Directory -Force -Path $Target | Out-Null
Copy-Item "$RepoRoot\skill\SKILL.md" -Destination $Target
Copy-Item "$RepoRoot\skill\themes.json" -Destination $Target
Copy-Item "$RepoRoot\skill\audit_xlsx.py" -Destination $Target

Write-Host "[OK] Skill installed to $Target"
Write-Host ""
Write-Host "Check Python + openpyxl are installed:"
Write-Host "  python --version"
Write-Host "  python -c 'import openpyxl; print(openpyxl.__version__)'"
Write-Host ""
Write-Host "If openpyxl is missing: pip install openpyxl"
Write-Host ""
Write-Host "Then in Claude Code, type: /saas-ai-audit"
