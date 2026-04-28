# CDST Windows Portable Build

CDST 的 Windows 桌面版使用 PyInstaller 打包。产物包含 Python 运行时和项目依赖，用户不需要安装 Python。

## 推荐产物

推荐发布：

```text
dist/CDST-Windows-Portable.zip
```

用户解压后双击：

```text
CDST.exe
```

## 在 Windows 本机打包

在 Windows 10/11 PowerShell 中运行：

```powershell
.\build_windows.ps1
```

默认会生成 portable 目录包：

```text
dist\CDST\
dist\CDST-Windows-Portable.zip
```

如果确实需要单个 exe：

```powershell
.\build_windows.ps1 -Mode onefile
```

单 exe 启动会更慢，也更容易被杀毒软件误报；portable zip 更适合包含 pandas、SciPy、matplotlib 这类科学计算依赖的桌面工具。

## 使用 GitHub Actions 打包

仓库已经配置 `.github/workflows/build.yml`。

1. 打开 GitHub 仓库的 Actions 页面。
2. 选择 `Build CDST Desktop App`。
3. 点击 `Run workflow`。
4. 完成后下载 `CDST-Windows` artifact。
5. 解压后得到 `CDST-Windows-Portable.zip`，这个就是可发布给 Windows 用户的包。

## 重要说明

PyInstaller 不能可靠跨平台编译：macOS 不能直接打包 Windows `.exe`。Windows 版本必须在 Windows 环境中构建，推荐用 GitHub Actions 的 `windows-latest` runner。
