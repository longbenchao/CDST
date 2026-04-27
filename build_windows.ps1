# build_windows.ps1 - CDST Windows 自动化打包脚本

param(
    [ValidateSet("onedir", "onefile")]
    [string]$Mode = "onedir"
)

Write-Host "=== CDST Windows Build Script ===" -ForegroundColor Green
Write-Host "Build mode: $Mode" -ForegroundColor Cyan
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
pip install -r requirements-build.txt --quiet
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

$modeArg = if ($Mode -eq "onefile") { "--onefile" } else { "--onedir" }

pyinstaller $modeArg --windowed --noconfirm --clean --name CDST `
  --add-data "src/cdst;cdst" `
  --collect-all=matplotlib `
  --collect-all=customtkinter `
  --collect-all=scipy `
  --collect-all=Bio `
  --hidden-import=pandas `
  --hidden-import=numpy `
  --hidden-import=Bio `
  --hidden-import=networkx `
  --hidden-import=scipy `
  --hidden-import=matplotlib `
  --hidden-import=PIL `
  --hidden-import=customtkinter `
  --hidden-import=psutil `
  --hidden-import=tkinter `
  --hidden-import=cdst `
  --hidden-import=cdst.core `
  --hidden-import=cdst.cli `
  --hidden-import=cdst.gui `
  --hidden-import=cdst.gui.main_window `
  --hidden-import=cdst.gui.utils `
  --hidden-import=cdst.gui.utils.config `
  --hidden-import=cdst.gui.utils.logger `
  --hidden-import=cdst.gui.utils.worker `
  --hidden-import=cdst.gui.tabs `
  --hidden-import=cdst.gui.tabs.quick_analysis `
  --hidden-import=cdst.gui.tabs.step_by_step `
  --hidden-import=cdst.gui.tabs.database_manager `
  --hidden-import=cdst.gui.tabs.results_viewer `
  --hidden-import=cdst.gui.tabs.settings `
  --hidden-import=cdst.visualization `
  cdst_gui_new.py

if ($LASTEXITCODE -eq 0) {
    if ($Mode -eq "onedir") {
        $portableZip = Join-Path (Get-Location) "dist\CDST-Windows-Portable.zip"
        if (Test-Path $portableZip) {
            Remove-Item $portableZip -Force
        }
        Compress-Archive -Path ".\dist\CDST\*" -DestinationPath $portableZip -Force
    }

    Write-Host ""
    Write-Host "=== Build Complete! ===" -ForegroundColor Green
    Write-Host ""
    if ($Mode -eq "onefile") {
        Write-Host "Executable location:" -ForegroundColor Cyan
        Write-Host "  $(Get-Location)\dist\CDST.exe" -ForegroundColor White
        Write-Host ""
        Write-Host "File size: $([math]::Round((Get-Item ".\dist\CDST.exe").Length / 1MB, 1)) MB" -ForegroundColor Yellow
    } else {
        Write-Host "Portable app folder:" -ForegroundColor Cyan
        Write-Host "  $(Get-Location)\dist\CDST" -ForegroundColor White
        Write-Host "Portable zip:" -ForegroundColor Cyan
        Write-Host "  $(Get-Location)\dist\CDST-Windows-Portable.zip" -ForegroundColor White
        Write-Host ""
        Write-Host "Zip size: $([math]::Round((Get-Item ".\dist\CDST-Windows-Portable.zip").Length / 1MB, 1)) MB" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "Users can unzip the portable package and double-click CDST.exe. No Python installation is needed." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "=== Build Failed! ===" -ForegroundColor Red
    Write-Host "Check the error messages above for details." -ForegroundColor Yellow
    exit 1
}
