# GitHubAccelerator

**提升GitHub连接稳定性，畅享高效开源协作**

## 一、项目简介
在复杂的网络环境下，访问GitHub时常面临连接不稳定、速度慢等问题。本工具旨在帮助中国网络环境下的用户更稳定地连接GitHub。通过智能解析和更新Hosts文件，以及对GitHub相关IP地址的优化筛选，提升访问GitHub资源的速度与稳定性。无论是下载代码仓库、获取项目资源，还是参与开源项目讨论，都能为你提供更稳定的网络支持。

## 二、核心功能
1. **智能IP解析与更新**
    - 多源获取：从多个权威的开源`hosts`源（如知名的GitHub520项目源、其他可靠的社区维护源等）获取最新的GitHub相关IP地址，确保数据的全面性和及时性。
    - 精准筛选：针对GitHub关键域名（如`objects.githubusercontent.com`、`github.com`、`assets - cdn.github.com`等），通过一系列严格的网络测试（TCP握手、HTTP响应、SSL验证等），筛选出稳定且高速的IP，为连接质量提供保障。
2. **应急IP保障**
    - 定期更新：维护一个应急IP文件`emergency_ips.json`，每30天自动检查并从外部源更新应急IP列表。确保在常规IP源不可用或网络环境极端复杂时，仍有可用的IP连接GitHub。
    - 安全筛选：应急IP均经过精心筛选，排除可能导致连接问题或存在安全风险的域名，保障用户网络访问安全。
3. **网络性能优化**
    - 并发测试：利用多线程并发技术，对获取到的GitHub相关IP进行全面的网络性能测试，包括ICMP延迟测试、HTTP请求响应时间测试以及丢包率测试。
    - 智能排序：根据综合评分算法，对测试结果进行排序，选取性能最优的前3个IP应用到本地`hosts`文件，最大程度提升连接速度和稳定性。
4. **安全便捷的`hosts`操作**
    - 临时模式：在临时模式下，工具会自动备份原始`hosts`文件内容，在程序退出时无缝恢复，让你可以放心测试优化效果，而无需担心对系统造成永久性影响。
    - 永久模式：若你对优化效果满意，可选择永久模式，将优化配置直接写入`hosts`文件，长期享受稳定的GitHub连接。
    - 自动刷新：每次更新`hosts`文件后，工具会自动执行`ipconfig /flushdns`命令，立即刷新本地DNS缓存，确保新配置迅速生效。

## 四、如何使用
1. **下载代码**
本工具的源代码托管在 GitHub 仓库中，你可以按照以下步骤下载：
访问项目的官方 GitHub 仓库（仓库地址请替换为实际地址）。
在仓库页面中，找到绿色的 Code 按钮，点击后选择 Download ZIP 选项，将源代码压缩包下载到本地。
解压下载的压缩包至你指定的目录。
2. **编译项目**
本项目使用 pyinstaller 进行编译，编译前请确保你已经安装了 pyinstaller，如果未安装，可以使用以下命令进行安装：
```bash
pip install pyinstaller
```
项目根目录下提供了 pack.bat 脚本，用于自动化编译过程，该脚本的内容如下：
```bat
pyinstaller --onefile --icon=github-mark.png --version-file=version_info.txt ^
--hidden-import=concurrent.futures ^
--hidden-import=ctypes.wintypes ^
--uac-admin ^
--clean ^
GitHubAccelerator.py
```
该脚本的具体参数解释如下：
 - `--onefile`：将所有依赖打包成一个单独的可执行文件。
 - `--icon=github-mark.png`：指定可执行文件的图标为 `github-mark.png`，请确保该图标文件位于项目根目录下。
 - `--version-file=version_info.txt`：指定版本信息文件为 `version_info.txt`，该文件包含了可执行文件的版本、版权等信息。
 - `--hidden-import=concurrent.futures` 和 `--hidden-import=ctypes.wintypes`：指定需要隐式导入的模块。
 - `--uac-admin`：要求以管理员身份运行生成的可执行文件。
 - `--clean`：在打包前清理之前的构建缓存。
编译步骤如下：
 - 打开命令行工具（如 `cmd` 或 `PowerShell`），进入到项目的根目录。
 - 运行 `pack.bat` 脚本
```bash
pack.bat
```
编译完成后，在项目根目录下的 dist 文件夹中会生成一个单独的可执行文件 GitHubAccelerator.exe，你可以直接运行该文件使用本工具。

## 五、使用方法
编译完成后，可按照以下步骤使用本工具：
1. 以管理员身份运行
由于修改 hosts 文件需要管理员权限，因此请右键点击生成的 GitHubAccelerator.exe 文件，选择 “以管理员身份运行”。
2. 主菜单操作
运行程序后，会出现主菜单，你可以根据自己的需求选择相应的操作：
 - 应用优化配置：选择此项后，工具将迅速获取最新的 IP 信息，并进行全面的网络质量测试，最终将性能最佳的 IP 应用到 hosts 文件中
 - 移除优化配置：当你需要恢复原始 hosts 设置时，选择此选项，工具会安全地将 hosts 文件恢复到初始状态。
 - 切换模式：可在临时模式和永久模式之间灵活切换，满足不同场景下的使用需求。
 - 退出程序：选择此项可正常退出工具。

## 六、项目优势
1. **多源数据保障**：通过整合多个不同的数据源获取IP地址，大大增加了获取到有效、可用IP的概率，提升了工具在不同网络环境下的适应性。
2. **深度检测筛选**：对IP进行多维度的严格检测和验证，确保每一个应用到`hosts`文件中的IP都具备良好的稳定性和高速性能。
3. **灵活模式选择**：临时模式和永久模式的设计，为用户提供了极大的便利。你可以先通过临时模式测试优化效果，再决定是否采用永久模式长期应用优化配置。
4. **自动维护更新**：应急IP文件的自动更新以及定期的IP地址检测机制，确保了工具能够持续适应不断变化的网络环境，始终为用户提供可靠的服务。

## 七、注意事项
1. **法律合规**：请确保在使用本工具时，遵守相关法律法规以及网络服务提供商的规定。本工具仅用于优化正常的GitHub访问，严禁用于任何非法或违反网络使用规则的行为。
2. **网络环境影响**：尽管本工具旨在提升GitHub连接稳定性，但网络环境复杂多变，可能仍存在部分网络环境下无法完全解决连接问题的情况。在使用过程中，若遇到异常，请及时反馈。
3. **软件更新**：建议定期从项目官方GitHub仓库获取最新版本的工具，以享受最新的功能和性能优化，同时确保工具能够适应GitHub网络架构的变化。

## 六、技术支持与反馈
如果你在使用过程中遇到任何问题，或者有宝贵的改进建议，欢迎随时通过以下方式与我们联系：
- **GitHub Issues**：访问项目的GitHub仓库，在`Issues`板块提交你的问题或建议。我们会及时查看并回复。
- **邮箱**：发送邮件至`ychen4514@outlook.com`，请在邮件主题中清晰注明“GitHub网络优化工具问题反馈”，并详细描述问题现象及操作步骤。

我们致力于不断优化工具性能，为广大用户提供更优质的服务。感谢你的支持与使用！ 

## Star History
[![Star History Chart](https://api.star-history.com/svg?repos=EveGlowLuna/GitHubAccelerator&type=Date)](https://star-history.com/#EveGlowLuna/GitHubAccelerator&Date) 