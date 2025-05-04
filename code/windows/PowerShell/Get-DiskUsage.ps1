# --- Auto-elevate and relaunch in PowerShell if needed ---
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole("Administrator")) {
    Write-Host "Restarting with admin rights..."
    Start-Process powershell "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

param (
    [string]$Path = "C:\"
)

# Ensure the path exists
if (-not (Test-Path $Path)) {
    Write-Error "Path not found: $Path"
    exit 1
}

Write-Host "Analyzing disk usage at $Path ..." -ForegroundColor Cyan

# Helper: Convert bytes to readable string
function Format-Size {
    param([int64]$bytes)
    switch ($bytes) {
        {$_ -ge 1PB} { "{0:N2} PB" -f ($bytes / 1PB); break }
        {$_ -ge 1TB} { "{0:N2} TB" -f ($bytes / 1TB); break }
        {$_ -ge 1GB} { "{0:N2} GB" -f ($bytes / 1GB); break }
        {$_ -ge 1MB} { "{0:N2} MB" -f ($bytes / 1MB); break }
        {$_ -ge 1KB} { "{0:N2} KB" -f ($bytes / 1KB); break }
        default     { "$bytes Bytes" }
    }
}

# Get folder sizes (top level only)
$folders = Get-ChildItem -Path $Path -Directory -Force -ErrorAction SilentlyContinue
$folderSizes = @()

foreach ($folder in $folders) {
    try {
        $size = (Get-ChildItem -Path $folder.FullName -Recurse -Force -ErrorAction SilentlyContinue |
                Measure-Object -Property Length -Sum).Sum
        $folderSizes += [pscustomobject]@{
            Folder = $folder.Name
            Size   = $size
            Pretty = Format-Size $size
        }
    } catch {
        Write-Warning "Failed to read: $($folder.FullName)"
    }
}

# Sort and show
Write-Host ""
Write-Host "Top-Level Folder Sizes:" -ForegroundColor Green
$folderSizes | Sort-Object Size -Descending | Format-Table Folder, Pretty

# Get file type usage
$fileStats = Get-ChildItem -Path $Path -Recurse -File -Force -ErrorAction SilentlyContinue |
    Group-Object Extension |
    ForEach-Object {
        $size = ($_.Group | Measure-Object Length -Sum).Sum
        [pscustomobject]@{
            Extension = $_.Name
            Count     = $_.Count
            Size      = $size
            Pretty    = Format-Size $size
        }
    } | Sort-Object Size -Descending

Write-Host ""
Write-Host "File Type Usage:" -ForegroundColor Green
$fileStats | Select-Object -First 15 | Format-Table Extension, Count, Pretty

# Classify into storage categories
$categories = @{
    "Documents" = @(".doc", ".docx", ".pdf", ".txt", ".xls", ".xlsx", ".ppt", ".pptx")
    "Images"    = @(".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".heic")
    "Videos"    = @(".mp4", ".mov", ".avi", ".mkv", ".wmv")
    "Audio"     = @(".mp3", ".wav", ".flac", ".aac", ".ogg")
    "Archives"  = @(".zip", ".rar", ".7z", ".tar", ".gz", ".iso")
    "Code"      = @(".py", ".js", ".html", ".css", ".cs", ".java", ".cpp", ".ps1", ".sh")
    "Executables" = @(".exe", ".dll", ".msi", ".bat", ".cmd")
}

$categoryStats = @{}
foreach ($cat in $categories.Keys) {
    $exts = $categories[$cat]
    $catFiles = Get-ChildItem -Path $Path -Recurse -File -Force -ErrorAction SilentlyContinue |
                Where-Object { $exts -contains $_.Extension.ToLower() }
    $size = ($catFiles | Measure-Object Length -Sum).Sum
    $categoryStats[$cat] = $size
}

Write-Host ""
Write-Host "Storage Type Breakdown:" -ForegroundColor Green
$categoryStats.GetEnumerator() | Sort-Object Value -Descending | ForEach-Object {
    "{0,-15}: {1}" -f $_.Key, (Format-Size $_.Value)
}

# Keep the console open when double-clicked
if ($Host.Name -eq "ConsoleHost") {
    Write-Host "`nPress any key to exit..."
    [void][System.Console]::ReadKey($true)
}
