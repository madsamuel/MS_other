# Define the download URLs
$files = @{
    "Big_Power_Point.pptx" = "https://github.com/madsamuel/MS_other/raw/master/experiments/autoit/workloads/Big_Power_Point.pptx"
    "Big_Word_File.docx" = "https://github.com/madsamuel/MS_other/raw/master/experiments/autoit/workloads/Big_Word_File.docx"
    "Big_excel.xls" = "https://github.com/madsamuel/MS_other/raw/master/experiments/autoit/workloads/Big_excel.xls"
}

# Set the destination folder (Desktop)
$desktopPath = [System.Environment]::GetFolderPath("Desktop")

# Download each file
foreach ($file in $files.GetEnumerator()) {
    $destination = "$desktopPath\$($file.Key)"
    Write-Host "Downloading $($file.Key)..."
    Invoke-WebRequest -Uri $file.Value -OutFile $destination
    Write-Host "$($file.Key) downloaded successfully to $destination"
}

Write-Host "All files have been downloaded!"