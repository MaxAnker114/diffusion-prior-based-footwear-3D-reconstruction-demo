param(
    [string]$JobName = "main_windows_fonts_preview"
)

$ErrorActionPreference = "Stop"

function Convert-ToWslPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    $pathForWsl = $Path.Replace("\", "/")
    $converted = & wsl.exe wslpath -a $pathForWsl
    if ($LASTEXITCODE -ne 0 -or -not $converted) {
        throw "Failed to convert path to WSL path: $Path"
    }
    return ($converted | Select-Object -First 1).Trim()
}

function Convert-ToBashDoubleQuoted {
    param([Parameter(Mandatory = $true)][string]$Value)

    $escaped = $Value.Replace("\", "\\").Replace('"', '\"').Replace('$', '\$').Replace('`', '\`')
    return '"' + $escaped + '"'
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$fontsDir = Join-Path $env:WINDIR "Fonts"

$requiredFonts = @(
    "simsun.ttc",
    "simhei.ttf",
    "simkai.ttf",
    "simfang.ttf",
    "STXINGKA.TTF"
)

foreach ($font in $requiredFonts) {
    $fontPath = Join-Path $fontsDir $font
    if (-not (Test-Path -LiteralPath $fontPath)) {
        throw "Required Windows font is missing: $fontPath"
    }
}

$fontConfigPath = Join-Path $env:TEMP "codex-ustc-windows-fonts.conf"
$fontConfigXml = @"
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
  <include ignore_missing="yes">/etc/fonts/fonts.conf</include>
  <dir>/mnt/c/Windows/Fonts</dir>
</fontconfig>
"@

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($fontConfigPath, $fontConfigXml, $utf8NoBom)

$wslScriptDir = Convert-ToWslPath $scriptDir
$wslFontConfig = Convert-ToWslPath $fontConfigPath

$quotedDir = Convert-ToBashDoubleQuoted $wslScriptDir
$quotedFontConfig = Convert-ToBashDoubleQuoted $wslFontConfig
$quotedJobName = Convert-ToBashDoubleQuoted $JobName

$bash = @"
set -euo pipefail
source ~/.profile >/dev/null 2>&1 || true
cd $quotedDir
mkdir -p .build/windows-fonts-preview/chapters
if ! FONTCONFIG_FILE=$quotedFontConfig latexmk -xelatex -outdir=.build/windows-fonts-preview -jobname=$quotedJobName -interaction=nonstopmode -halt-on-error main.tex > .build/windows-fonts-preview/build.log 2>&1; then
  tail -n 100 .build/windows-fonts-preview/build.log
  exit 1
fi
cp ".build/windows-fonts-preview/$JobName.pdf" "./$JobName.pdf"
"@

& wsl.exe -- bash -lc $bash
if ($LASTEXITCODE -ne 0) {
    throw "Windows-font PDF preview build failed."
}

Write-Host "Done: $(Join-Path $scriptDir "$JobName.pdf")"
