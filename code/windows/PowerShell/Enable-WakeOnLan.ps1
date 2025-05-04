# Self-elevate the script if not already running as admin
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Restarting script with elevated privileges..."
    $script = $MyInvocation.MyCommand.Definition
    Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -NoProfile -File `"$script`"" -Verb RunAs
    exit
}

# Get all Ethernet adapters (filter out Bluetooth, virtual, Wi-Fi, etc.)
$adapters = Get-NetAdapter | Where-Object { $_.Status -eq "Up" -and $_.HardwareInterface -eq $true }

foreach ($adapter in $adapters) {
    Write-Host "Configuring adapter: $($adapter.Name)" -ForegroundColor Cyan

    # Enable Wake-on-LAN magic packet
    powercfg -deviceenablewake "$($adapter.Name)"
    
    # Enable required registry keys
    $key = "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"
    $found = $false

    Get-ChildItem $key | ForEach-Object {
        $driverDesc = Get-ItemProperty -Path $_.PsPath -Name DriverDesc -ErrorAction SilentlyContinue
        if ($driverDesc -and $driverDesc.DriverDesc -eq $adapter.InterfaceDescription) {
            $found = $true
            Set-ItemProperty -Path $_.PsPath -Name "WakeOnMagicPacket" -Value "1" -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $_.PsPath -Name "WakeOnPattern" -Value "0" -ErrorAction SilentlyContinue
            Write-Host "Wake-on-MagicPacket enabled in registry."
        }
    }

    if (-not $found) {
        Write-Warning "Could not find registry settings for adapter: $($adapter.InterfaceDescription)"
    }
}

Write-Host "`nDone. Make sure Wake-on-LAN is enabled in BIOS/UEFI as well." -ForegroundColor Green
