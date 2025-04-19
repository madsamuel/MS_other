Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Create Tray Icon
$trayIcon = New-Object System.Windows.Forms.NotifyIcon
$trayIcon.Icon = [System.Drawing.SystemIcons]::Information
$trayIcon.Visible = $true
$trayIcon.Text = "Perf Monitor"

# Counter templates (some with wildcards)
$counterTemplates = @(
    '\Processor(_Total)\% Processor Time',
    '\System\Processor Queue Length',
    '\Memory\Available MBytes',
    '\Memory\Pages/sec',
    '\PhysicalDisk(_Total)\% Disk Time',
    '\PhysicalDisk(_Total)\Avg. Disk Queue Length',
    '\Network Interface(*)\Bytes Total/sec',
    '\Network Interface(*)\Packets/sec',
    '\Network Interface(*)\Packets Received/sec',
    '\Network Interface(*)\Packets Sent/sec',
    '\Network Interface(*)\Current Bandwidth',
    '\Network Interface(*)\Bytes Received/sec',
    '\Network Interface(*)\Packets Received Unicast/sec',
    '\Network Interface(*)\Packets Received Non-Unicast/sec',
    '\Network Interface(*)\Packets Received Discarded',
    '\Network Interface(*)\Packets Received Errors',
    '\Network Interface(*)\Packets Received Unknown',
    '\Network Interface(*)\Bytes Sent/sec',
    '\Network Interface(*)\Packets Sent Unicast/sec',
    '\Network Interface(*)\Packets Sent Non-Unicast/sec',
    '\Network Interface(*)\Packets Outbound Discarded',
    '\Network Interface(*)\Packets Outbound Errors',
    '\Network Interface(*)\Output Queue Length',
    '\Network Interface(*)\Offloaded Connections',
    '\Network Interface(*)\TCP Active RSC Connections',
    '\Network Interface(*)\TCP RSC Coalesced Packets/sec',
    '\Network Interface(*)\TCP RSC Exceptions/sec',
    '\Network Interface(*)\TCP RSC Average Packet Size'
)

# Expand wildcards to real instance paths
function Expand-ValidCounters {
    $expanded = @()
    foreach ($template in $counterTemplates) {
        try {
            $setName = $template.Split('\')[1]
            $counters = Get-Counter -ListSet $setName -ErrorAction Stop
            $matched = $counters.Paths | Where-Object { $_ -like $template }
            if ($matched) {
                $expanded += $matched
            }
        } catch {
            Write-Host "Skipping unavailable counter: $template"
        }
    }
    return $expanded
}

# Show counter popup
function Show-Counters {
    $lines = @()
    try {
        $counters = Expand-ValidCounters
        if ($counters.Count -eq 0) {
            $lines += "No valid counters found."
        } else {
            $results = Get-Counter -Counter $counters -ErrorAction Stop
            foreach ($sample in $results.CounterSamples) {
                $name = $sample.Path
                $value = "{0:N2}" -f $sample.CookedValue
                $lines += "${name}: ${value}"
            }
        }
    } catch {
        $lines += "Error: $($_.Exception.Message)"
    }

    $summary = $lines -join "`n"
    [System.Windows.Forms.MessageBox]::Show($summary, "Performance Metrics", 'OK', 'Information')
}

# Timer: popup every 30 seconds
$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = 30000
$timer.Add_Tick({ Show-Counters })
$timer.Start()

# Double-click tray icon to show metrics
$trayIcon.Add_DoubleClick({ Show-Counters })

# Right-click menu: Exit
$menu = New-Object System.Windows.Forms.ContextMenuStrip
$exitItem = New-Object System.Windows.Forms.ToolStripMenuItem "Exit"
$exitItem.Add_Click({
    $timer.Stop()
    $timer.Dispose()
    $trayIcon.Visible = $false
    $trayIcon.Dispose()
    [System.Windows.Forms.Application]::Exit()
})
$menu.Items.Add($exitItem)
$trayIcon.ContextMenuStrip = $menu

# Start message loop
[System.Windows.Forms.Application]::Run()
