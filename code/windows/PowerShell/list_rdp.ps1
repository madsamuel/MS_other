# Ensure required modules
Import-Module -Name CimCmdlets

# Define registry keys to check
$regPath = "HKLM:\Software\Policies\Microsoft\Windows NT\Terminal Services"
$rdpSettings = @{}

if (Test-Path $regPath) {
    Get-ItemProperty -Path $regPath | ForEach-Object {
        foreach ($name in $_.PSObject.Properties.Name) {
            $rdpSettings[$name] = $_.$name
        }
    }
} else {
    $rdpSettings["Policy Status"] = "No RDP Group Policy settings applied"
}

# Check if RDP is enabled
$rdpEnabled = Get-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Terminal Server" -Name "fDenyTSConnections"
$rdpSettings["RDP Enabled"] = if ($rdpEnabled.fDenyTSConnections -eq 0) { "Yes" } else { "No" }

# Get RDP listening status
$rdpListening = Get-NetTCPConnection -LocalPort 3389 -State Listen -ErrorAction SilentlyContinue
$rdpSettings["RDP Port Listening"] = if ($rdpListening) { "Yes" } else { "No" }

# Check RDP service status
$rdpService = Get-Service -Name TermService -ErrorAction SilentlyContinue
$rdpSettings["TermService Status"] = $rdpService.Status

# Get RDP-related performance counters
$rdpPerfCounters = @(
    "\Terminal Services\Session Count",
    "\Terminal Services\Total Sessions",
    "\Terminal Services\Active Sessions",
    "\Terminal Services\Inactive Sessions"
)

$perf = Get-Counter -Counter $rdpPerfCounters -ErrorAction SilentlyContinue
foreach ($sample in $perf.CounterSamples) {
    $rdpSettings[$sample.Path] = $sample.CookedValue
}

# Convert to object for grid view
$output = foreach ($key in $rdpSettings.Keys) {
    [PSCustomObject]@{
        Setting = $key
        Value   = $rdpSettings[$key]
    }
}

# Show in dashboard
$output | Out-GridView -Title "RDP Configuration & Performance Dashboard"
