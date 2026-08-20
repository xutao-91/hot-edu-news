[CmdletBinding()]
param(
    [string]$TaskName = 'HotEduNews-Daily',
    [string]$DailyAt = '20:00'
)

$ErrorActionPreference = 'Stop'
$runner = Join-Path $PSScriptRoot 'run_daily.ps1'
if (-not (Test-Path -LiteralPath $runner)) {
    throw "Runner not found: $runner"
}

$action = New-ScheduledTaskAction `
    -Execute 'powershell.exe' `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$runner`""
$trigger = New-ScheduledTaskTrigger -Daily -At $DailyAt
$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
    -RestartCount 2 `
    -RestartInterval (New-TimeSpan -Minutes 30)

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description 'Fetch education news, rebuild the static site, and push GitHub once daily.' `
    -Force

Get-ScheduledTask -TaskName $TaskName | Format-List TaskName, State, Description
