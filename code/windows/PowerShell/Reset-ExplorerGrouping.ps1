# Set Explorer "Group by: None" for common folder types

$regBase = "HKCU:\Software\Microsoft\Windows\Shell\Bags\AllFolders\Shell"

# Ensure the key exists
if (-not (Test-Path $regBase)) {
    New-Item -Path $regBase -Force | Out-Null
}

# Set no grouping
Set-ItemProperty -Path $regBase -Name "GroupByDirection" -Value 0 -Type DWord -Force
Set-ItemProperty -Path $regBase -Name "GroupByKey:FMTID" -Value "{00000000-0000-0000-0000-000000000000}" -Type String -Force
Set-ItemProperty -Path $regBase -Name "GroupByKey:PID" -Value 0 -Type DWord -Force

# Clear existing folder views to apply new default
$bagsPath = "HKCU:\Software\Microsoft\Windows\Shell\Bags"
$bagMRUPath = "HKCU:\Software\Microsoft\Windows\Shell\BagMRU"

Remove-Item -Path $bagsPath -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path $bagMRUPath -Recurse -Force -ErrorAction SilentlyContinue

# Restart Explorer to apply changes
Stop-Process -Name explorer -Force
Start-Process explorer
