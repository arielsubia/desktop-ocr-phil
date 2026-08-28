# Launch Phil Dev Desktop OCR from source in one step.
#
# Usage (from anywhere):
#   & "C:\Users\ariel\Documents\Projects\desktop-ocr-phil\run.ps1"
#
# By default the app runs detached (its own window process) so this terminal
# stays free. Pass -Attached to run it in the foreground and see its console
# output for debugging (Ctrl+C stops it).
param(
    [switch]$Attached
)
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
$venvPythonw = Join-Path $projectRoot ".venv\Scripts\pythonw.exe"

if (-not (Test-Path $venvPython)) {
    throw "Virtual environment not found at $venvPython. Create it: python -m venv .venv"
}

if ($Attached) {
    # Foreground: console stays attached, Ctrl+C stops the app.
    & $venvPython -m phildev_ocr
} else {
    # Detached: no console window, terminal returns immediately.
    Start-Process -FilePath $venvPythonw -ArgumentList "-m", "phildev_ocr" -WorkingDirectory $projectRoot
    Write-Host "Phil Dev Desktop OCR launched. Look for its icon in the system tray."
}
