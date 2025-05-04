Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Create Tray Icon
$trayIcon = New-Object System.Windows.Forms.NotifyIcon
$trayIcon.Icon = [System.Drawing.SystemIcons]::Information
$trayIcon.Visible = $true
$trayIcon.Text = "Perf Monitor"

# Performance Counter Templates
$counterTemplates = @(
    '\Processor(_Total)\% Processor Time',
    '\System\Processor Queue Length',
    '\Memory\Available MBytes',
    '\Memory\Pages/sec',
    '\PhysicalDisk(_Total)\% Disk Time',
    '\PhysicalDisk(_Total)\Avg. Disk Queue Length',
    '\Network Interface(*)\Bytes Total/sec',
    '\Network Interface(*)\Packets Outbound Errors',
    '\Network Interface(*)\Packets Received Errors',
    '\RemoteFX Network\Current TCP RTT',
    '\RemoteFX Network\Current UDP RTT',
    '\RemoteFX Graphics\Frames Skipped Per Second'
)

# Expand Wildcard Counters
function Expand-ValidCounters {
    $expanded = @()
    foreach ($template in $counterTemplates) {
        try {
            $setName = ($template -split '\\')[1] -replace '\(.*\)', ''
            $counters = Get-Counter -ListSet $setName -ErrorAction Stop
            $matched = $counters.Paths | Where-Object { $_ -like $template }
            if ($matched) {
                $expanded += $matched
            }
        } catch {
            Write-Host "Skipping invalid counter: $template"
        }
    }
    return $expanded
}

# Get Performance Data
function Get-PerfData {
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
    return ($lines -join "`r`n")
}

# Show Static Form
function Show-PerfForm {
    $form = New-Object System.Windows.Forms.Form
    $form.Text = "Performance Metrics"
    $form.Size = New-Object System.Drawing.Size(800, 500)
    $form.StartPosition = "CenterScreen"

    $textBox = New-Object System.Windows.Forms.TextBox
    $textBox.Multiline = $true
    $textBox.Dock = "Fill"
    $textBox.ScrollBars = "Vertical"
    $textBox.ReadOnly = $true
    $textBox.Font = New-Object System.Drawing.Font("Consolas", 10)
    $textBox.Text = Get-PerfData

    $form.Controls.Add($textBox)
    $form.Topmost = $true
    $form.Add_Shown({ $form.Activate() })
    $form.ShowDialog()
}

# Double-click = Show static perf window
$trayIcon.Add_DoubleClick({ Show-PerfForm })

# Right-click Exit Menu
$menu = New-Object System.Windows.Forms.ContextMenuStrip
$exitItem = New-Object System.Windows.Forms.ToolStripMenuItem "Exit"
$exitItem.Add_Click({
    $trayIcon.Visible = $false
    $trayIcon.Dispose()
    [System.Windows.Forms.Application]::Exit()
})
$menu.Items.Add($exitItem)
$trayIcon.ContextMenuStrip = $menu

# Start Message Loop
[System.Windows.Forms.Application]::Run()
