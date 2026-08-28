# Build the Phil Dev Desktop OCR executable.
# Idempotent: safe to run repeatedly. Run from the project root.
#   .\packaging\build.ps1
$ErrorActionPreference = "Stop"

$python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Virtual environment not found. Create it first: python -m venv .venv"
}

# Regenerate the .ico from the source logo so branding stays in sync.
& $python -c "from PIL import Image; im=Image.open('src/phildev_ocr/assets/logo-phildev.png').convert('RGBA'); im.save('src/phildev_ocr/assets/logo-phildev.ico', sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])"

& $python -m PyInstaller packaging/PhilDevDesktopOCR.spec --distpath dist --workpath build --noconfirm

Write-Host "Build complete: dist\PhilDevDesktopOCR.exe"
