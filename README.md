# GitHubAccelerator

![GitHub License](https://img.shields.io/github/license/EveGlowLuna/GitHubAccelerator)
![Platform Support](https://img.shields.io/badge/Platform-Windows%20|%20Linux%20|%20macOS-blueviolet)

**智能网络加速工具 - 优化GitHub访问体验**

## 核心功能
!!!text
- 实时检测并修复`objects.githubusercontent.com`连接
- 智能优选全球最快的GitHub CDN节点
- 跨平台Hosts文件安全操作（自动备份/恢复）
- 应急IP库自动更新机制（30天强制刷新）

## 编译指南
### Windows系统
!!!bat
pyinstaller --onefile --icon=github-mark.png ^
--hidden-import=concurrent.futures ^
--uac-admin --add-data="*.json;." ^
--version-file=version_info.txt ^
GitHubAccelerator.py -n GitHubAccelerator.exe

### Linux系统
!!!bash
pyinstaller --onefile \
--add-data="*.json:." \
--hidden-import=concurrent.futures \
--clean \
GitHubAccelerator.py -n GitHubAccelerator

### macOS系统
!!!bash
pyinstaller --onefile \
--add-data="*.json:." \
--runtime-hook=hooks/hook-mac_signature.py \
--hidden-import=concurrent.futures \
GitHubAccelerator.py -n GitHubAccelerator.app

## 使用说明
### 首次运行
!!!bash
# Linux/macOS需要权限
sudo chmod +x GitHubAccelerator
sudo ./GitHubAccelerator

# Windows右键选择"以管理员身份运行"

### 主菜单操作
!!!text
 应用优化配置 - 自动完成：
    1. 获取最新IP地址
    2. 执行网络质量测试
    3. 更新Hosts文件
    4. 刷新DNS缓存

 移除优化配置 - 安全还原原始Hosts

 模式切换：
    - 临时模式：程序退出自动还原
    - 永久模式：长期保留优化配置

 退出程序

## 技术亮点
!!!text
- 智能IP验证体系：
  ✅ TCP 443端口可达性检测
  ✅ HTTPS证书有效性验证
  ✅ 实际下载速度基准测试

- 安全机制：
  🔒 Hosts修改前自动备份
  🔒 应急IP库签名验证
  🔒 操作日志审计追踪

- 跨平台支持：
  🖥️ 自动适配不同系统路径：
    Windows: C:\Windows\System32\drivers\etc\hosts
    Unix: /etc/hosts

## 常见问题
### 连接测试失败
!!!text
现象：网络诊断显示所有IP不可用
解决方案：
1. 检查本地防火墙设置
2. 尝试使用应急模式：
!!!bash
sudo ./GitHubAccelerator --emergency

### DNS未及时更新
!!!bash
# 手动刷新DNS缓存
sudo systemd-resolve --flush-caches  # Linux
sudo killall -HUP mDNSResponder     # macOS
ipconfig /flushdns                  # Windows

## 支持与反馈
**问题反馈渠道**：
- GitHub Issues: [提交问题](https://github.com/EveGlowLuna/GitHubAccelerator/issues)
- 紧急支持邮箱: ychen4514@outlook.com（标题加[紧急]）

**技术文档**：
- [操作手册](docs/USERGUIDE.md)
- [开发日志](docs/CHANGELOG.md)

[![Star History Chart](https://api.star-history.com/svg?repos=EveGlowLuna/GitHubAccelerator&type=Timeline)](https://star-history.com/#EveGlowLuna/GitHubAccelerator)