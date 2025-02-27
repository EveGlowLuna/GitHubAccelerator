#!/bin/zsh
# 清理旧构建
rm -rf dist/ build/

# 生成专用ICNS图标
iconutil -c icns icons.iconset -o GitHubAccelerator.icns

# 执行打包（含自定义钩子）
pyinstaller --noconfirm \
    --onefile \
    --name "GitHubAccelerator" \
    --icon GitHubAccelerator.icns \
    --add-data "emergency_ips.json:." \
    --additional-hooks-dir=hooks \
    --hidden-import concurrent.futures \
    --runtime-hook=hooks/hook-mac_signature.py \
    GitHubAccelerator.py

# 签名处理
codesign --remove-signature dist/GitHubAccelerator
codesign --force --deep -s - dist/GitHubAccelerator