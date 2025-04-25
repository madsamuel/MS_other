# Updated Script Using Background Job
##############################################
# Set log file path
$logPath = "$env:SystemRoot\System32\Winevt\Logs\RemoteDesktopServices.evtx"

# Check if file exists
if (-not (Test-Path $logPath)) {
    Write-Error "Log file not found: $logPath"
    return
}

# Start a background job to load and filter events
$job = Start-Job -ScriptBlock {
    param($path)
    $events = Get-WinEvent -Path $path
    $events | Where-Object { $_.LevelDisplayName -eq "Error" } |
        Select-Object TimeCreated, Id, LevelDisplayName, Message
} -ArgumentList $logPath

Write-Host "Processing in background... Use 'Receive-Job -Id $($job.Id)' to retrieve results once completed."
Write-Host "You can check job status with 'Get-Job -Id $($job.Id)' and remove it with 'Remove-Job -Id $($job.Id)'"

# To Retrieve Results Later aka Check job status
Get-Job -Id $($job.Id)

# Get results
Receive-Job -Id $($job.Id) | Format-Table -AutoSize

# Clean up
Remove-Job -Id $($job.Id)
