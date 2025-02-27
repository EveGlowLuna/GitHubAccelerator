#!/bin/bash
set -e

cd "$(dirname "$0")"

# 生成临时签名证书（仅测试用）
security create-keychain -p password build.keychain
security default-keychain -s build.keychain
security unlock-keychain -p password build.keychain
security import dev_certificate.p12 -k build.keychain -P password -T /usr/bin/codesign

# 执行带签名的构建
pyinstaller --onefile \
--hidden-import=concurrent.futures \
--runtime-hook=hooks/hook-mac_signature.py \
--workpath=build \
--distpath=dist \
--specpath=spec \
GitHubAccelerator.py

# 清理临时证书
security delete-keychain build.keychain