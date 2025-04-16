# https://learn.microsoft.com/en-us/azure/virtual-desktop/graphics-chroma-value-increase-4-4-4?tabs=group-policy

# Define the registry path
$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\Terminal Services"

# Create the key if it doesn't exist
if (-Not (Test-Path $regPath)) {
    New-Item -Path $regPath -Force | Out-Null
}

# Set "Prioritize H.264/AVC 444 Graphics mode for Remote Desktop connections"
Set-ItemProperty -Path $regPath -Name "AVC444ModePreferred" -Value 1 -Type DWord

# Set "Configure image quality for RemoteFX Adaptive Graphics" to High
Set-ItemProperty -Path $regPath -Name "RemoteFXAdaptiveGraphicsImageQuality" -Value 2 -Type DWord

Write-Host " Group Policy settings applied successfully:"
Write-Host " - AVC444ModePreferred = 1 (Enabled)"
Write-Host " - RemoteFXAdaptiveGraphicsImageQuality = 2 (High)"
