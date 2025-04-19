Add-Type -AssemblyName System.Windows.Forms
[console]::ForegroundColor = "Green"
[console]::BackgroundColor = "Black"
Clear-Host

# Set console to max size
$maxWidth = [System.Console]::LargestWindowWidth
$maxHeight = [System.Console]::LargestWindowHeight
[System.Console]::SetBufferSize($maxWidth, $maxHeight)
[System.Console]::SetWindowSize($maxWidth, $maxHeight)

$width = [System.Console]::WindowWidth
$height = [System.Console]::WindowHeight

# Initialize falling stream positions for all columns
$columns = @(0..($width - 1))
$positions = @{}
foreach ($col in $columns) {
    $positions[$col] = Get-Random -Minimum 0 -Maximum $height
}

# Main loop
while ($true) {
    foreach ($col in $columns) {
        $row = $positions[$col]

        # Draw random ASCII char
        $char = [char](Get-Random -Minimum 33 -Maximum 126)
        try {
            [System.Console]::SetCursorPosition($col, $row)
            Write-Host "$char" -NoNewline
        } catch {}

        # Advance position downward
        $positions[$col] = ($row + 1) % $height
    }

    Start-Sleep -Milliseconds 35
}
