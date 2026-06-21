# PowerShell script: register BA-system daily Telegram notification with Windows Task Scheduler
# Schedule: 18:00 every weekday (Mon-Fri)
#
# Usage from PowerShell (run as admin recommended):
#   powershell -ExecutionPolicy Bypass -File telegram_register_task.ps1

$TaskName = 'BA-System Telegram Daily 1800'
$ScriptPath = 'C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude\telegram_run_daily.bat'
$WorkDir = 'C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude'

# Verify .bat exists
if (-not (Test-Path $ScriptPath)) {
    Write-Host "ERROR: $ScriptPath not found" -ForegroundColor Red
    exit 1
}

# Unregister existing task if present
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Found existing task. Unregistering first..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Trigger: 18:00 every weekday
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday, Tuesday, Wednesday, Thursday, Friday -At 18:00

# Action: run the .bat file
$Action = New-ScheduledTaskAction -Execute $ScriptPath -WorkingDirectory $WorkDir

# Settings: battery-friendly, wake-to-run, auto-retry on fail
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -WakeToRun -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5) -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

# Register the task
Register-ScheduledTask -TaskName $TaskName -Trigger $Trigger -Action $Action -Settings $Settings -Description "BA-system live engine - fetch watchlist from BQ + send to Telegram. Runs after VN market close + ticker_1m refresh." -User $env:USERNAME

Write-Host ""
Write-Host "OK Task registered: $TaskName" -ForegroundColor Green
Write-Host "   Schedule: Monday-Friday at 18:00"
Write-Host "   Action: $ScriptPath"
Write-Host ""
Write-Host "Verify in Task Scheduler GUI (taskschd.msc) or via:"
Write-Host "   Get-ScheduledTask -TaskName '$TaskName'"
Write-Host ""
Write-Host "Run manually to test:"
Write-Host "   Start-ScheduledTask -TaskName '$TaskName'"
Write-Host ""
Write-Host "Unregister later:"
Write-Host "   Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:0"
