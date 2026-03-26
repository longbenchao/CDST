# Windows 版本构建指南

## 前置要求
- Windows 10/11 操作系统
- Python 3.10 或更高版本 (推荐 3.12)
- 管理员权限的命令行 (PowerShell 或 CMD)

## 步骤 1: 安装 Python

1. 访问 https://www.python.org/downloads/windows/
2. 下载最新稳定版 (推荐 Python 3.12.x)
3. **重要**: 安装时勾选 "Add Python to PATH"
4. 完成安装后，打开 PowerShell 验证:
   ```powershell
   python --version
   ```

## 步骤 2: 克隆项目并进入目录

```powershell
cd C:\Users\你的用户名\Documents
git clone <项目仓库地址> CDST
cd CDST
```

或直接复制项目文件到某目录，如 `C:\Projects\CDST`

## 步骤 3: 创建虚拟环境

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

如果执行脚本策略受限，使用:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

或使用 CMD:
```cmd
venv\Scripts\activate.bat
```

## 步骤 4: 安装依赖

```powershell
pip install --upgrade pip
pip install customtkinter pillow pandas numpy biopython networkx scipy pyinstaller
```

## 步骤 5: 测试运行

```powershell
$env:PYTHONPATH="C:\Projects\CDST\src"
python cdst_gui.py
```

如果 GUI 正常启动，说明环境配置成功。

## 步骤 6: 打包成独立可执行文件 (.exe)

```powershell
# 确保在虚拟环境中
.\venv\Scripts\Activate.ps1

# 清理旧构建
Remove-Item -Recurse -Force build, dist, *.spec -ErrorAction SilentlyContinue

# 执行打包
pyinstaller --onefile --windowed --name CDST ^
  --add-data "src/cdst;cdst" ^
  --hidden-import=pandas ^
  --hidden-import=numpy ^
  --hidden-import=biopython ^
  --hidden-import=networkx ^
  --hidden-import=scipy ^
  --hidden-import=PIL ^
  --hidden-import=customtkinter ^
  cdst_gui.py
```

**注意**: Windows 使用分号 `;` 作为路径分隔符，而 macOS/Linux 使用冒号 `:`

## 步骤 7: 获取打包结果

打包完成后，在 `dist` 目录下会生成:
- `CDST.exe` - 独立可执行文件

您可以将此文件复制到任何 Windows 计算机上直接双击运行，无需安装 Python 或任何依赖。

## 可选: 创建快捷方式

1. 右键点击 `CDST.exe`
2. 选择 "发送到" -> "桌面快捷方式"
3. 可自定义图标：右键快捷方式 -> 属性 -> 更改图标

## 常见问题解决

### 问题 1: "找不到模块 cdst"
确保 `--add-data` 参数正确，并且 `src/cdst` 目录存在。

### 问题 2: 打包后运行闪退
在命令行中运行生成的 exe 查看错误信息:
```powershell
.\dist\CDST.exe
```

### 问题 3: 杀毒软件误报
PyInstaller 打包的程序可能被某些杀毒软件误报为病毒。解决方法:
- 将程序添加到杀毒软件白名单
- 对程序进行数字签名 (需要证书)
- 向杀毒软件厂商提交误报申诉

### 问题 4: 缺少 DLL 文件
如果出现 "找不到 XXX.dll" 错误，可能需要安装 Visual C++ Redistributable:
下载地址: https://aka.ms/vs/17/release/vc_redist.x64.exe

## 文件大小说明

打包后的 `CDST.exe` 文件大小约为 150-250 MB，因为包含了完整的 Python 运行时和所有依赖库。这是正常现象。

## 自动化打包脚本

创建 `build_windows.ps1` 文件:

```powershell
# build_windows.ps1
Write-Host "=== CDST Windows Build Script ===" -ForegroundColor Green

# 激活虚拟环境
Write-Host "Activating virtual environment..."
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    & ".\venv\Scripts\Activate.ps1"
} else {
    Write-Host "Creating virtual environment..."
    python -m venv venv
    & ".\venv\Scripts\Activate.ps1"
}

# 安装依赖
Write-Host "Installing dependencies..."
pip install --upgrade pip
pip install customtkinter pillow pandas numpy biopython networkx scipy pyinstaller

# 清理
Write-Host "Cleaning old builds..."
Remove-Item -Recurse -Force build, dist, *.spec -ErrorAction SilentlyContinue

# 打包
Write-Host "Building executable..."
pyinstaller --onefile --windowed --name CDST `
  --add-data "src/cdst;cdst" `
  --hidden-import=pandas `
  --hidden-import=numpy `
  --hidden-import=biopython `
  --hidden-import=networkx `
  --hidden-import=scipy `
  --hidden-import=PIL `
  --hidden-import=customtkinter `
  cdst_gui.py

Write-Host "=== Build Complete! ===" -ForegroundColor Green
Write-Host "Executable location: $(Get-Location)\dist\CDST.exe" -ForegroundColor Cyan
```

运行方式:
```powershell
.\build_windows.ps1
```
