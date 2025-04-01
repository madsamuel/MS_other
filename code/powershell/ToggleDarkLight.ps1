 
# Path to the Personalize key
$regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
 
# Registry value names for Light/Dark theme
$appThemeValue = "AppsUseLightTheme"
$systemThemeValue = "SystemUsesLightTheme"
 
# Get current values for Apps and System theme (defaults to 1 if not found)
$currentAppsTheme   = (Get-ItemPropertyValue -Path $regPath -Name $appThemeValue   -ErrorAction SilentlyContinue) | ForEach-Object { $_ }
$currentSystemTheme = (Get-ItemPropertyValue -Path $regPath -Name $systemThemeValue -ErrorAction SilentlyContinue) | ForEach-Object { $_ }
 
# If AppsUseLightTheme is 1 (Light Mode), switch both to 0 (Dark Mode)
if ($currentAppsTheme -eq 1) {
    Set-ItemProperty -Path $regPath -Name $appThemeValue -Value 0
    Set-ItemProperty -Path $regPath -Name $systemThemeValue -Value 0
    Write-Host "Switched to Dark Mode."
} else {
    # Otherwise, switch both to 1 (Light Mode)
    Set-ItemProperty -Path $regPath -Name $appThemeValue -Value 1
    Set-ItemProperty -Path $regPath -Name $systemThemeValue -Value 1
    Write-Host "Switched to Light Mode."
}
