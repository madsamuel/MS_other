Add-Type -AssemblyName System.Drawing

# Get defaults before param in case $PSScriptRoot is not set
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$defaultPng = Join-Path $scriptDir "input.png"
$defaultIco = Join-Path $scriptDir "output.ico"

param (
    [string]$InputPng = $defaultPng,
    [string]$OutputIco = $defaultIco
)

function Convert-PngToIco {
    param (
        [string]$pngPath,
        [string]$icoPath
    )

    if (-not (Test-Path $pngPath)) {
        Write-Error "PNG file not found: $pngPath"
        return
    }

    try {
        $bitmap = [System.Drawing.Bitmap]::FromFile($pngPath)

        $iconStream = New-Object System.IO.FileStream($icoPath, [System.IO.FileMode]::Create)
        $iconHeader = [byte[]]@(0, 0, 1, 0, 1, 0)
        $iconStream.Write($iconHeader, 0, 6)

        $width = [byte]($bitmap.Width -bor 0)
        $height = [byte]($bitmap.Height -bor 0)
        $iconStream.WriteByte($width)
        $iconStream.WriteByte($height)
        $iconStream.WriteByte(0)
        $iconStream.WriteByte(0)
        $iconStream.Write([byte[]]@(1, 0, 32, 0), 0, 4)

        $pngBytes = [System.IO.File]::ReadAllBytes($pngPath)
        $size = [BitConverter]::GetBytes($pngBytes.Length)
        $offset = [BitConverter]::GetBytes(22)

        $iconStream.Write($size, 0, 4)
        $iconStream.Write($offset, 0, 4)
        $iconStream.Write($pngBytes, 0, $pngBytes.Length)

        $iconStream.Close()
        Write-Host "ICO saved to: $icoPath"
    } catch {
        Write-Error "Failed to convert: $_"
    } finally {
        if ($bitmap) { $bitmap.Dispose() }
    }
}

Convert-PngToIco -pngPath $InputPng -icoPath $OutputIco
