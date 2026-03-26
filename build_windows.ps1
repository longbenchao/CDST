# build_windows.ps1 - CDST Windows 自动化打包脚本

Write-Host "=== CDST Windows Build Script ===" -ForegroundColor Green
Write-Host ""

# 检查 Python 是否安装
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found. Please install Python 3.10+ from https://python.org" -ForegroundColor Red
    exit 1
}

# 激活或创建虚拟环境
Write-Host ""
Write-Host "Setting up virtual environment..." -ForegroundColor Yellow
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "Activating existing virtual environment..." -ForegroundColor Cyan
    & ".\venv\Scripts\Activate.ps1"
} else {
    Write-Host "Creating new virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    & ".\venv\Scripts\Activate.ps1"
}

# 安装依赖
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install --upgrade pip --quiet
pip install customtkinter pillow pandas numpy biopython networkx scipy pyinstaller --quiet
Write-Host "Dependencies installed successfully!" -ForegroundColor Green

# 清理旧构建
Write-Host ""
Write-Host "Cleaning old builds..." -ForegroundColor Yellow
Remove-Item -Recurse -Force build, dist, *.spec -ErrorAction SilentlyContinue
Write-Host "Clean complete!" -ForegroundColor Green

# 检查 src/cdst 目录是否存在
if (-not (Test-Path ".\src\cdst")) {
    Write-Host "ERROR: src/cdst directory not found!" -ForegroundColor Red
    Write-Host "Please ensure the project structure is correct." -ForegroundColor Yellow
    exit 1
}

# 打包
Write-Host ""
Write-Host "Building executable..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Cyan

pyinstaller --onefile --windowed --name CDST `
  --add-data "src/cdst;cdst" `
  --hidden-import=pandas `
  --hidden-import=numpy `
  --hidden-import=biopython `
  --hidden-import=networkx `
  --hidden-import=scipy `
  --hidden-import=PIL `
  --hidden-import=customtkinter `
  --hidden-import=tkinter `
  cdst_gui.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== Build Complete! ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable location:" -ForegroundColor Cyan
    Write-Host "  $(Get-Location)\dist\CDST.exe" -ForegroundColor White
    Write-Host ""
    Write-Host "File size: $((Get-Item ".\dist\CDST.exe").Length / 1MB) MB" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "You can now copy CDST.exe to any Windows computer and run it directly!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "=== Build Failed! ===" -ForegroundColor Red
    Write-Host "Check the error messages above for details." -ForegroundColor Yellow
    exit 1
}
