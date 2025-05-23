Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Globals
$global:form = New-Object System.Windows.Forms.Form
$global:form.WindowState = 'Minimized'
$global:form.ShowInTaskbar = $false
$global:stopRequested = $false
$global:rdpCache = "Loading..."
$global:lastRefresh = Get-Date

# Create NotifyIcon
$trayIcon = New-Object System.Windows.Forms.NotifyIcon
$trayIcon.Icon = [System.Drawing.SystemIcons]::Information
$trayIcon.Visible = $true
$trayIcon.Text = "RDP Tray Monitor"

# Create Timer
$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = 60000

# Cleanup function
function Cleanup {
    try { $timer.Stop(); $timer.Dispose() } catch {}
    try { $refreshTimer.Stop(); $refreshTimer.Dispose() } catch {}
    try { $trayIcon.Visible = $false; $trayIcon.Dispose() } catch {}
    try { $form.Close() } catch {}
    Write-Host "Clean exit."
    exit
}

# Background refresh of RDP details
function Refresh-RDPDetails {
    try {
        $info = @{}

        $regPath = "HKLM:\Software\Policies\Microsoft\Windows NT\Terminal Services"
        if (Test-Path $regPath) {
            Get-ItemProperty -Path $regPath | ForEach-Object {
                foreach ($name in $_.PSObject.Properties.Name) {
                    $info["[Policy] $name"] = $_.$name
                }
            }
        } else {
            $info["[Policy]"] = "No GPO RDP settings found"
        }

        $rdpEnabled = (Get-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Terminal Server" -Name "fDenyTSConnections").fDenyTSConnections
        $info["RDP Enabled"] = if ($rdpEnabled -eq 0) { "Yes" } else { "No" }

        $portOpen = Get-NetTCPConnection -LocalPort 3389 -State Listen -ErrorAction SilentlyContinue
        $info["RDP Port Listening (3389)"] = if ($portOpen) { "Yes" } else { "No" }

        $svc = Get-Service TermService -ErrorAction SilentlyContinue
        $info["TermService Status"] = if ($svc) { $svc.Status } else { "Not found" }

        $counters = @(
            "\Terminal Services\Active Sessions",
            "\Terminal Services\Inactive Sessions",
            "\Terminal Services\Total Sessions"
        )
        try {
            $perf = Get-Counter -Counter $counters -ErrorAction Stop
            foreach ($sample in $perf.CounterSamples) {
                $info[$sample.Path] = [math]::Round($sample.CookedValue, 0)
            }
        } catch {}

        $global:rdpCache = ($info.GetEnumerator() | Sort-Object Name | ForEach-Object { "$($_.Name): $($_.Value)" }) -join "`n"
        $global:lastRefresh = Get-Date
    } catch {
        $global:rdpCache = "Failed to refresh: $_"
    }
}

# Format compact tooltip
function Get-ShortStatus {
    $statusLines = $global:rdpCache.Split("`n")[0..2] -join " | "
    $prefix = "RDP: "
    $maxLength = 63 - $prefix.Length
    return "$prefix$statusLines".Substring(0, [Math]::Min($statusLines.Length, $maxLength))
}

# Double-click shows full RDP details
$trayIcon.Add_DoubleClick({
    [System.Windows.Forms.MessageBox]::Show($global:rdpCache, "RDP Details", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
})

# Right-click menu with Exit
$menu = New-Object System.Windows.Forms.ContextMenuStrip
$exitItem = New-Object System.Windows.Forms.ToolStripMenuItem "Exit"
$exitItem.Add_Click({
    $global:stopRequested = $true
    Cleanup
})
$menu.Items.Add($exitItem)
$trayIcon.ContextMenuStrip = $menu

# Timer to update tooltip and show balloon
$timer.Add_Tick({
    $tooltip = Get-ShortStatus
    $trayIcon.Text = $tooltip
    $trayIcon.BalloonTipTitle = "RDP Monitor"
    $trayIcon.BalloonTipText = $tooltip
    $trayIcon.ShowBalloonTip(1000)
})
$timer.Start()

# Background refresh timer (every 30 seconds)
$refreshTimer = New-Object System.Windows.Forms.Timer
$refreshTimer.Interval = 30000
$refreshTimer.Add_Tick({ Refresh-RDPDetails })
$refreshTimer.Start()

# Initial refresh and display
Refresh-RDPDetails
$initTip = Get-ShortStatus
$trayIcon.Text = $initTip
$trayIcon.BalloonTipTitle = "RDP Monitor"
$trayIcon.BalloonTipText = $initTip
$trayIcon.ShowBalloonTip(2000)

# Start message loop
[System.Windows.Forms.Application]::Run($form)

# On exit
Cleanup
