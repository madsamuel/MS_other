Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Globals
$global:form = New-Object System.Windows.Forms.Form
$global:form.WindowState = 'Minimized'
$global:form.ShowInTaskbar = $false
$global:preventSleep = $true

# Create NotifyIcon
$trayIcon = New-Object System.Windows.Forms.NotifyIcon
$trayIcon.Icon = [System.Drawing.SystemIcons]::Information
$trayIcon.Visible = $true
$trayIcon.Text = "Prevent Sleep Mode"

# Cleanup function
function Cleanup {
    $trayIcon.Visible = $false
    $trayIcon.Dispose()
    $form.Close()
    Write-Host "✔ Clean exit."
}

# Prevent sleep function
function Prevent-Sleep {
    if ($global:preventSleep) {
        [void][System.Runtime.InteropServices.DllImport("kernel32.dll", SetLastError=$true)]
        [extern] static bool SetThreadExecutionState([uint32] $esFlags)
        $esFlags = 0x80000002 # ES_CONTINUOUS | ES_SYSTEM_REQUIRED
        [void][SetThreadExecutionState]::SetThreadExecutionState($esFlags)
    } else {
        [void][SetThreadExecutionState]::SetThreadExecutionState(0x80000000) # ES_CONTINUOUS
    }
}

# Right-click menu
$menu = New-Object System.Windows.Forms.ContextMenuStrip
$pauseItem = New-Object System.Windows.Forms.ToolStripMenuItem "Pause"
$pauseItem.Add_Click({
    $global:preventSleep = -not $global:preventSleep
    $pauseItem.Text = if ($global:preventSleep) { "Pause" } else { "Resume" }
    Prevent-Sleep
})
$exitItem = New-Object System.Windows.Forms.ToolStripMenuItem "Exit"
$exitItem.Add_Click({
    $global:preventSleep = $false
    Prevent-Sleep
    $form.Close()  # Close the message loop
})
$menu.Items.Add($pauseItem)
$menu.Items.Add($exitItem)
$trayIcon.ContextMenuStrip = $menu

# Start preventing sleep
Prevent-Sleep

# Run the real WinForms message loop
[System.Windows.Forms.Application]::Run($form)

# After loop exits, clean up
Cleanup