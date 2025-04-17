Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Counters to monitor
$counterPaths = @(
    '\Network Interface(*)\Bytes Total/sec',
    '\Network Interface(*)\Packets Outbound Errors',
    '\Network Interface(*)\Packets Received Errors',
    '\Processor(_Total)\% Processor Time',
    '\System\Processor Queue Length',
    '\Memory\Available MBytes',
    '\Memory\Pages/sec',
    '\PhysicalDisk(_Total)\% Disk Time',
    '\PhysicalDisk(_Total)\Avg. Disk Queue Length',
    '\RemoteFX Network\Current TCP RTT',
    '\RemoteFX Network\Current UDP RTT',
    '\RemoteFX Graphics\Frames Skipped Per Second'
)

# Tray icon setup
$trayIcon = New-Object System.Windows.Forms.NotifyIcon
$trayIcon.Icon = [System.Drawing.SystemIcons]::Information
$trayIcon.Visible = $true
$trayIcon.Text = "Performance Monitor"

# Create exit menu
$contextMenu = New-Object System.Windows.Forms.ContextMenu
$exitItem = New-Object System.Windows.Forms.MenuItem "Exit", {
    $trayIcon.Visible = $false
    $timer.Stop()
    $timer.Dispose()
    [System.Windows.Forms.Application]::Exit()
}
$contextMenu.MenuItems.Add($exitItem)
$trayIcon.ContextMenu = $contextMenu

# Timer to poll counters
$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = 30000 # 30 seconds

$timer.Add_Tick({
    try {
        $results = Get-Counter -Counter $counterPaths -ErrorAction Stop
        $summaryLines = @()

        $summaryLines = @()
        foreach ($sample in $results.CounterSamples) {
            $path = [string]$sample.Path
            $value = "{0:N2}" -f $sample.CookedValue
            $summaryLines += "${path}: ${value}"
        }
        $summary = ($summaryLines -join "`n")

        $summary = ($summaryLines -join "`n")

        # Truncate if too long for balloon
        $maxLength = 255
        if ($summary.Length -gt $maxLength) {
            $summary = $summary.Substring(0, $maxLength - 3) + "..."
        }

        $trayIcon.BalloonTipTitle = "System Performance Summary"
        $trayIcon.BalloonTipText = $summary
        $trayIcon.ShowBalloonTip(5000)
    } catch {
        $trayIcon.BalloonTipTitle = "Error Reading Counters"
        $trayIcon.BalloonTipText = $_.Exception.Message
        $trayIcon.ShowBalloonTip(5000)
    }
})

$timer.Start()
[System.Windows.Forms.Application]::Run()
