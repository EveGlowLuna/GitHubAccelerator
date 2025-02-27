#!/bin/bash
set -e

# 生成符合 macOS 规范的 .icns 图标文件（需 512x512 原始图）
mkdir -p icons.iconset
sips -z 16 16     github-mark.png --out icons.iconset/icon_16x16.png
sips -z 32 32     github-mark.png --out icons.iconset/icon_16x16@2x.png
sips -z 128 128   github-mark.png --out icons.iconset/icon_128x128.png
sips -z 256 256   github-mark.png --out icons.iconset/icon_128x128@2x.png
sips -z 512 512   github-mark.png --out icons.iconset/icon_512x512.png
iconutil -c icns icons.iconset -o github-mark.icns || true

# 动态生成 py2app 配置文件
cat > setup.py <<'EOF'
from setuptools import setup

APP = ['GitHubAccelerator.py']
DATA_FILES = [
    'hooks', 
    'github-mark.icns',
    'github-mark.png'
]
OPTIONS = {
    'iconfile': 'github-mark.icns',
    'plist': {
        'CFBundleName': "GitHubAccelerator",
        'CFBundleShortVersionString': "1.0.0",
        'CFBundleVersion': "20250227.1",
        'LSMinimumSystemVersion': "10.15.0"
    },
    'argv_emulation': False,
    'packages': ['requests', 'pythonping']
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
EOF

# 安装依赖并执行构建
pip install --upgrade py2app==0.28.6
python setup.py py2app -b 0 --dist-dir dist

# 修复系统权限（需管理员密码）
sudo spctl --master-disable
xattr -dr com.apple.quarantine dist/GitHubAccelerator.app

# 清理临时文件
rm -rf build/ github-mark.icns setup.py icons.iconset