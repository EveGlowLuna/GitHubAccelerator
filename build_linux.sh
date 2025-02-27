#!/bin/bash
set -e

# 设置工作目录
cd "$(dirname "$0")"

# 安装必要依赖
pip install -r requirements.txt

# 执行构建
pyinstaller --onefile \
--hidden-import=concurrent.futures \
--clean \
--workpath=build \
--distpath=dist \
--specpath=spec \
GitHubAccelerator.py

# 文件权限设置
chmod 755 dist/GitHubAccelerator