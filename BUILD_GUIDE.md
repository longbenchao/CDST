# CDST 跨平台桌面应用打包指南

本文档提供 Windows 和 macOS 两个平台的完整打包说明，生成开箱即用的独立应用程序。

---

## 📦 打包结果

| 平台 | 输出文件 | 大小 | 运行方式 |
|------|---------|------|---------|
| Windows | `CDST.exe` | ~150-250 MB | 双击直接运行 |
| macOS | `CDST.app` | ~150-250 MB | 双击直接运行 |

**特点：**
- ✅ 包含完整 Python 运行时环境
- ✅ 无需安装任何依赖
- ✅ 开箱即用
- ✅ 可复制到任意同平台电脑运行

---

## 🪟 Windows 版本打包

### 方法一：使用自动化脚本（推荐）

1. **打开项目目录**
   ```powershell
   cd C:\路径\到\CDST
   ```

2. **运行打包脚本**
   ```powershell
   .\build_windows.ps1
   ```
   
   如果提示权限问题，先执行：
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **获取结果**
   - 打包完成后，`dist\CDST.exe` 即为可执行文件
   - 可复制到任意 Windows 电脑双击运行

### 方法二：手动步骤

1. **安装 Python 3.10+**
   - 访问 https://python.org/downloads/windows/
   - 下载并安装（勾选 "Add Python to PATH"）

2. **创建虚拟环境**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **安装依赖**
   ```powershell
   pip install --upgrade pip
   pip install customtkinter pillow pandas numpy biopython networkx scipy pyinstaller
   ```

4. **执行打包**
   ```powershell
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

5. **获取结果**
   - `dist\CDST.exe` 即为最终应用

---

## 🍎 macOS 版本打包

### 前置准备

1. **安装带 Tk 支持的 Python**
   ```bash
   brew install python-tk@3.12
   ```

2. **验证 Tkinter**
   ```bash
   python3.12 -c "import tkinter; print('Tk OK:', tkinter.TkVersion)"
   ```

### 方法一：手动打包

1. **创建虚拟环境**
   ```bash
   cd /Users/你的用户名/Git/CDST
   /opt/homebrew/opt/python@3.12/bin/python3.12 -m venv venv
   source venv/bin/activate
   ```

2. **安装依赖**
   ```bash
   pip install --upgrade pip
   pip install customtkinter pillow pandas numpy biopython networkx scipy pyinstaller
   ```

3. **测试运行**
   ```bash
   export PYTHONPATH=$(pwd)/src
   python cdst_gui.py
   ```

4. **执行打包**
   ```bash
   rm -rf build dist *.spec
   pyinstaller --onefile --windowed --name CDST \
     --add-data "src/cdst:cdst" \
     --hidden-import=pandas \
     --hidden-import=numpy \
     --hidden-import=biopython \
     --hidden-import=networkx \
     --hidden-import=scipy \
     --hidden-import=PIL \
     --hidden-import=customtkinter \
     cdst_gui.py
   ```

5. **获取结果**
   - `dist/CDST.app` 即为最终应用
   - 可复制到任意 macOS 电脑双击运行

### 常见问题解决

**问题：Python意外退出 / 崩溃**
```bash
# 确保安装了 tcl-tk
brew install tcl-tk

# 重建虚拟环境
rm -rf venv
/opt/homebrew/opt/python@3.12/bin/python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # 或手动安装所有依赖
```

**问题：找不到模块 cdst**
确保 `--add-data` 参数中的路径分隔符正确：
- macOS/Linux 使用冒号 `:` → `"src/cdst:cdst"`
- Windows 使用分号 `;` → `"src/cdst;cdst"`

---

## 🔧 重要注意事项

### 1. 路径分隔符差异
| 平台 | 分隔符 | 示例 |
|------|--------|------|
| Windows | `;` | `--add-data "src/cdst;cdst"` |
| macOS/Linux | `:` | `--add-data "src/cdst:cdst"` |

### 2. 交叉编译限制
PyInstaller **不支持**跨平台编译：
- ❌ 不能在 Windows 上打包 macOS 应用
- ❌ 不能在 macOS 上打包 Windows 应用
- ✅ 必须在目标操作系统上分别打包

### 3. 文件大小
打包后的应用约 150-250 MB，因为包含：
- 完整 Python 运行时
- 所有依赖库（numpy、pandas、scipy 等）
- GUI 框架（customtkinter/tkinter）

这是正常现象。

### 4. 杀毒软件误报
Windows 版本可能被某些杀毒软件误报：
- 将程序添加到白名单
- 或对程序进行数字签名（需要证书）

---

## 📁 项目文件结构

```
CDST/
├── cdst_gui.py           # GUI 主程序
├── src/
│   └── cdst/             # 核心模块
│       ├── __init__.py
│       ├── core.py
│       └── ...
├── build_windows.ps1     # Windows 自动化打包脚本
├── README_WINDOWS.md     # Windows 详细指南
├── BUILD_GUIDE.md        # 本文件
└── dist/                 # 打包输出目录
    ├── CDST.exe          # Windows 可执行文件
    └── CDST.app          # macOS 应用程序
```

---

## 🚀 快速开始

### Windows 用户
```powershell
# 1. 克隆项目
git clone <仓库地址> CDST
cd CDST

# 2. 运行打包脚本
.\build_windows.ps1

# 3. 完成！dist\CDST.exe 可直接使用
```

### macOS 用户
```bash
# 1. 安装依赖
brew install python-tk@3.12

# 2. 设置环境
cd /路径/到/CDST
/opt/homebrew/opt/python@3.12/bin/python3.12 -m venv venv
source venv/bin/activate
pip install customtkinter pillow pandas numpy biopython networkx scipy pyinstaller

# 3. 打包
pyinstaller --onefile --windowed --name CDST --add-data "src/cdst:cdst" cdst_gui.py

# 4. 完成！dist/CDST.app 可直接使用
```

---

## 📞 故障排查

如遇到问题，请：
1. 在终端/命令行中直接运行生成的可执行文件查看详细错误
2. 检查 Python 版本是否兼容（3.10+）
3. 确认所有依赖已正确安装
4. 查看 `build/` 目录中的日志文件
