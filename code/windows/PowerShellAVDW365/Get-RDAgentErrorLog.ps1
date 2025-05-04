# Set log file path
$logPath = "$env:SystemRoot\System32\Winevt\Logs\RemoteDesktopServices.evtx"

# Check if file exists
if (-not (Test-Path $logPath)) {
    Write-Error "Log file not found: $logPath"
    return
}

# Read events from file (no FilterHashtable here)
$events = Get-WinEvent -Path $logPath

# Filter to only Error level events (LevelDisplayName = "Error")
$errorEvents = $events | Where-Object { $_.LevelDisplayName -eq "Error" }

# Display results
if ($errorEvents.Count -eq 0) {
    Write-Host "No error events found in $logPath"
} else {
    $errorEvents | Select-Object TimeCreated, Id, LevelDisplayName, Message | Format-Table -AutoSize
}
