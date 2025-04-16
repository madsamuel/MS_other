Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Globals
$global:form = New-Object System.Windows.Forms.Form
$global:form.WindowState = 'Minimized'
$global:form.ShowInTaskbar = $false
$global:stopRequested = $false

# Create NotifyIcon
$trayIcon = New-Object System.Windows.Forms.NotifyIcon
$trayIcon.Icon = [System.Drawing.SystemIcons]::Information
$trayIcon.Visible = $true
$trayIcon.Text = "RDP Tray Monitor"

# Cleanup function
function Cleanup {
    $trayIcon.Visible = $false
    $trayIcon.Dispose()
    $timer.Stop()
    $timer.Dispose()
    $form.Close()
    Write-Host "✔ Clean exit."
}

# Function to get RDP info
function Get-RDPDetails {
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
    $perf = Get-Counter -Counter $counters -ErrorAction SilentlyContinue
    foreach ($sample in $perf.CounterSamples) {
        $info[$sample.Path] = [math]::Round($sample.CookedValue, 0)
    }

    return ($info.GetEnumerator() | Sort-Object Name | ForEach-Object { "$($_.Name): $($_.Value)" }) -join "`n"
}

# Double-click shows details
$trayIcon.Add_DoubleClick({
    [System.Windows.Forms.MessageBox]::Show((Get-RDPDetails), "RDP Details", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
})

# Right-click menu
$menu = New-Object System.Windows.Forms.ContextMenuStrip
$exitItem = New-Object System.Windows.Forms.ToolStripMenuItem "Exit"
$exitItem.Add_Click({
    $global:stopRequested = $true
    $form.Close()  # Close the message loop
})
$menu.Items.Add($exitItem)
$trayIcon.ContextMenuStrip = $menu

# Timer to update tooltip and balloon
$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = 60000
$timer.Add_Tick({
    $status = (Get-RDPDetails).Split("`n")[0..2] -join " | "
    $prefix = "RDP: "
    $maxLength = 63 - $prefix.Length
    $shortStatus = $status.Substring(0, [Math]::Min($status.Length, $maxLength))
    $trayIcon.Text = "$prefix$shortStatus"
    $trayIcon.BalloonTipTitle = "RDP Monitor"
    $trayIcon.BalloonTipText = $status
    $trayIcon.ShowBalloonTip(1000)
})
$timer.Start()

# First-time tooltip
$status = (Get-RDPDetails).Split("`n")[0..2] -join " | "
$prefix = "RDP: "
$maxLength = 63 - $prefix.Length
$shortStatus = $status.Substring(0, [Math]::Min($status.Length, $maxLength))
$trayIcon.Text = "$prefix$shortStatus"
$trayIcon.BalloonTipTitle = "RDP Monitor"
$trayIcon.BalloonTipText = $status
$trayIcon.ShowBalloonTip(2000)

# Run the real WinForms message loop
[System.Windows.Forms.Application]::Run($form)

# After loop exits, clean up
Cleanup
