@echo off
setlocal enabledelayedexpansion

:: 设置工作目录为仓库根目录
cd /d %~dp0

:: 检查必要文件存在性
if not exist "github-mark.png" (
    echo 错误：缺少图标文件 github-mark.png
    exit /b 1
)

pyinstaller --onefile ^
--icon="github-mark.png" ^
--version-file="version_info.txt" ^
--hidden-import=concurrent.futures ^
--hidden-import=ctypes.wintypes ^
--uac-admin ^
--clean ^
--workpath="build" ^
GitHubAccelerator.py

if %errorlevel% neq 0 (
    echo 构建失败，错误代码: %errorlevel%
    exit /b %errorlevel%
)