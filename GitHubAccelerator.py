import sys
import os
import re
import requests
import concurrent.futures
import subprocess
import atexit
import json
import socket
import platform
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import NamedTemporaryFile
from pythonping import ping

#region 核心配置
HOSTS_PATH = {
    'Windows': r'C:\Windows\System32\drivers\etc\hosts',
    'Linux': '/etc/hosts',
    'Darwin': '/private/etc/hosts'
}[platform.system()]

TEMP_MARKER = "# GitHubAccelerator Block"
MARKER_REGEX = re.compile(rf"{re.escape(TEMP_MARKER)}.*?{re.escape('# End Block')}", re.DOTALL)
#endregion

#region 权限管理
def ensure_admin():
    """跨平台权限验证"""
    if platform.system() == 'Windows':
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            sys.exit("需要管理员权限")
    else:
        if os.getuid() != 0:
            sys.exit("请使用sudo运行")

#endregion

#region Hosts管理器
class HostsManager:
    def __init__(self):
        self.backup = None
        self.temp_mode = False

    def read_hosts(self):
        """安全读取Hosts"""
        try:
            with open(HOSTS_PATH, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(HOSTS_PATH, 'r', encoding='latin-1') as f:
                return f.read()

    def write_hosts(self, content):
        """安全写入Hosts"""
        temp_path = os.path.join(os.path.dirname(HOSTS_PATH), 'hosts.tmp')
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(content)
        os.replace(temp_path, HOSTS_PATH)
        self.flush_dns()

    def flush_dns(self):
        """跨平台DNS刷新"""
        if platform.system() == 'Windows':
            subprocess.run('ipconfig /flushdns 2>&1', shell=True, check=True)
        elif platform.system() == 'Linux':
            try:
                subprocess.run(['systemd-resolve', '--flush-caches'], check=True)
            except:
                subprocess.run(['nscd', '-i', 'hosts'], check=True)
        elif platform.system() == 'Darwin':
            subprocess.run(['killall', '-HUP', 'mDNSResponder'], check=True)

    def apply_optimization(self, ip_map, permanent=False):
        """应用优化配置"""
        original = self._clean_hosts()
        new_block = self._generate_block(ip_map)
        
        if permanent:
            self.write_hosts(f"{original}\n{new_block}")
        else:
            self._temp_write(f"{original}\n{new_block}")

    def _clean_hosts(self):
        """清理旧配置"""
        return MARKER_REGEX.sub('', self.read_hosts()).strip()

    def _generate_block(self, ip_map):
        """生成配置块"""
        lines = [TEMP_MARKER]
        for domain, ips in ip_map.items():
            lines.extend(f"{ip.ljust(16)}{domain}" for ip in ips)
        lines.append("# End Block")
        return '\n'.join(lines)

    def _temp_write(self, content):
        """临时写入"""
        if not self.temp_mode:
            self.backup = self.read_hosts()
            self.temp_mode = True
            atexit.register(self.restore)
        self.write_hosts(content)

    def restore(self):
        """恢复配置"""
        if self.backup:
            self.write_hosts(self.backup)
            self.temp_mode = False
            atexit.unregister(self.restore)
#endregion

#region 网络优化核心
class GitHubOptimizer:
    SOURCES = [
        'https://cdn.jsdelivr.net/gh/521xueweihan/GitHub520@main/hosts',
        'https://gitlab.com/ineo6/hosts/-/raw/master/hosts',
        'https://raw.hellogithub.com/hosts'
    ]

    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False  # 禁用SSL验证
        self.emergency_ips = {
            'github.com': ['20.205.243.166', '140.82.121.4'],
            'assets-cdn.github.com': ['185.199.108.153', '185.199.109.153']
        }

    def fetch_ips(self):
        """获取最新IP数据"""
        for url in self.SOURCES:
            try:
                resp = self.session.get(url, timeout=10)
                if resp.status_code == 200:
                    return self._parse_hosts(resp.text)
            except:
                continue
        return self.emergency_ips

    def _parse_hosts(self, content):
        """解析Hosts内容"""
        ip_map = {}
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                parts = re.split(r'\s+', line)
                if len(parts) > 1 and 'github' in parts.lower():
                    domain = parts.strip()
                    ip_map.setdefault(domain, []).append(parts.strip())
        return ip_map

    def benchmark(self, ip_map):
        """IP性能测试"""
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            for domain, ips in ip_map.items():
                futures = {executor.submit(self._test_ip, ip, domain): ip for ip in ips}
                sorted_ips = sorted(
                    (f.result() for f in concurrent.futures.as_completed(futures)),
                    key=lambda x: x['score']
                )[:3]
                results[domain] = [ip['ip'] for ip in sorted_ips]
        return results

    def _test_ip(self, ip, domain):
        """综合测试IP"""
        result = {'ip': ip, 'latency': 999, 'loss': 1.0, 'score': 9999}
        
        # ICMP测试
        try:
            ping_result = ping(ip, count=3, timeout=2)
            result['latency'] = ping_result.rtt_avg_ms
            result['loss'] = ping_result.packet_loss
        except:
            pass
        
        # HTTP测试
        try:
            start = datetime.now()
            self.session.get(
                f'http://{ip}/',
                headers={'Host': domain},
                timeout=3,
                allow_redirects=False
            )
            result['http'] = (datetime.now() - start).total_seconds() * 1000
        except:
            result['http'] = 999
        
        # 评分算法
        result['score'] = (result['latency'] * 0.6) + (result['loss'] * 500) + (result['http'] * 0.4)
        return result
#endregion

#region 命令行接口
def clear_screen():
    """跨平台清屏"""
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def main():
    ensure_admin()
    hosts = HostsManager()
    optimizer = GitHubOptimizer()

    try:
        while True:
            clear_screen()
            print(f'''
GitHub网络优化工具
1. 应用优化配置
2. 恢复原始配置
3. 退出''')
            choice = input("请选择: ").strip()

            if choice == '1':
                clear_screen()
                print("🔄 获取最新IP...")
                ip_map = optimizer.fetch_ips()
                print("⏱️ 测试节点性能...")
                optimized = optimizer.benchmark(ip_map)
                print("⚡ 应用配置...")
                hosts.apply_optimization(optimized)
                print("✅ 优化完成！")
                input("\n按回车返回主菜单...")
            elif choice == '2':
                clear_screen()
                hosts.restore()
                print("✅ 配置已恢复")
                input("\n按回车返回主菜单...")
            elif choice == '3':
                break
            else:
                print("无效输入")
                input("\n按回车重新选择...")
    except KeyboardInterrupt:
        hosts.restore()
        print("\n已恢复配置并退出")

if __name__ == "__main__":
    main()
#endregion