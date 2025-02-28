import sys
import os
import re
import ctypes
import platform
import requests
import socket
import subprocess
import json
import atexit
import concurrent.futures
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import NamedTemporaryFile
from pythonping import ping

#region 跨平台配置
HOSTS_PATHS = {
    'windows': r'C:\Windows\System32\drivers\etc\hosts',
    'darwin': '/private/etc/hosts',
    'linux': '/etc/hosts'
}

TEMP_MARKER = "# GitHubAccelerator Block"
MARKER_REGEX = re.compile(rf"{re.escape(TEMP_MARKER)}.*?{re.escape('# End Block')}", re.DOTALL)
EMERGENCY_FILE = "emergency_ips.json"
CURRENT_PLATFORM = sys.platform
#endregion

#region 权限管理
def ensure_admin():
    """跨平台管理员权限验证"""
    if CURRENT_PLATFORM == 'win32':
        if not ctypes.windll.shell32.IsUserAnAdmin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
            sys.exit(0)
    else:
        if os.getuid() != 0:
            print("请使用sudo权限运行此程序")
            sys.exit(1)
#endregion

#region 临时模式管理器
class TempModeController:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._backup = None
            cls._instance._active = False
        return cls._instance
    
    def activate(self):
        if not self._active:
            self._backup = self._read_hosts()
            self._active = True
            atexit.register(self.restore)

    def deactivate(self):
        if self._active:
            self.restore()
            self._active = False
            atexit.unregister(self.restore)
    
    def apply_temp_changes(self, content):
        if self._active:
            self.write_hosts(content)
    
    def restore(self):
        if self._backup:
            self.write_hosts(self._backup)
            flush_dns()
    
    def _read_hosts(self):
        try:
            with open(HOSTS_PATHS[CURRENT_PLATFORM], 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(HOSTS_PATHS[CURRENT_PLATFORM], 'r', encoding='latin-1') as f:
                return f.read()
    
    def write_hosts(self, content):
        with NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as tmp:
            tmp.write(content)
            tmp_file = tmp.name
        os.replace(tmp_file, HOSTS_PATHS[CURRENT_PLATFORM])
#endregion

#region 智能修复模块
class ObjectsFixer:
    TARGET_DOMAIN = "objects.githubusercontent.com"
    SOURCES = [
        "https://gitlab.com/ineo6/hosts/-/raw/master/hosts",
        "https://fastly.jsdelivr.net/gh/521xueweihan/GitHub520@main/hosts"
    ]
    
    def __init__(self):
        self.current_ips = []
        self.last_checked = datetime.min

    def is_accessible(self):
        try:
            sock = socket.create_connection((self.TARGET_DOMAIN, 443), 3)
            sock.close()
            resp = requests.head(f"https://{self.TARGET_DOMAIN}", timeout=5)
            return resp.status_code < 500
        except:
            return False

    def fetch_latest_ips(self):
        collected = set()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self._fetch_source, url): url for url in self.SOURCES}
            for future in concurrent.futures.as_completed(futures):
                if ips := future.result():
                    collected.update(ips)
        return list(collected) or self._fallback_ips()

    def _fetch_source(self, url):
        try:
            resp = requests.get(url, timeout=5)
            return self._parse_hosts(resp.text) if resp.ok else []
        except:
            return []

    def _parse_hosts(self, content):
        return [parts[0] for line in content.splitlines() 
                if (parts := line.strip().split()) 
                and len(parts) > 1 
                and self.TARGET_DOMAIN in parts]

    def _fallback_ips(self):
        return ["185.199.111.133", "185.199.108.133", "185.199.110.133"]

    def validate_ip(self, ip):
        return (self._test_port(ip, 443) 
                and self._verify_ssl(ip))

    def _test_port(self, ip, port):
        try:
            with socket.create_connection((ip, port), 3):
                return True
        except:
            return False

    def _verify_ssl(self, ip):
        try:
            resp = requests.head(
                f"https://{ip}",
                headers={"Host": self.TARGET_DOMAIN},
                timeout=5,
                verify=True
            )
            return resp.status_code in [200, 403]
        except:
            return False

    def apply_fix(self):
        if (datetime.now() - self.last_checked).seconds < 3600:
            return
        
        if not self.is_accessible():
            print("🔧 检测到连接异常，启动智能修复...")
            if valid_ips := [ip for ip in self.fetch_latest_ips() if self.validate_ip(ip)]:
                self._update_hosts(valid_ips)
                self.current_ips = valid_ips
                self.last_checked = datetime.now()
                print(f"✅ 已更新有效IP：{', '.join(valid_ips[:3])}...")

    def _update_hosts(self, ips):
        hosts_mgr = HostsManager()
        original = hosts_mgr.clean_hosts_content()
        cleaned = re.sub(rf"\d+\.\d+\.\d+\.\d+\s+{self.TARGET_DOMAIN}", "", original)
        new_block = "\n".join([f"{ip.ljust(16)}{self.TARGET_DOMAIN}" for ip in ips])
        hosts_mgr.temp_controller.write_hosts(f"{cleaned}\n{TEMP_MARKER}\n{new_block}\n# End Block")
        flush_dns()
#endregion

#region 网络优化模块
class NetworkOptimizer:
    def __init__(self):
        self.sources = [
            'https://gitee.com/frankwuzp/github-host/raw/main/hosts',
            'https://mirror.ghproxy.com/https://raw.githubusercontent.com/521xueweihan/GitHub520/main/hosts'
        ]
        self.emergency_file = Path(EMERGENCY_FILE)
        self._init_emergency_file()

    def _init_emergency_file(self):
        if not self.emergency_file.exists() or self._needs_update():
            self._refresh_emergency_ips()

    def _needs_update(self):
        try:
            mtime = datetime.fromtimestamp(self.emergency_file.stat().st_mtime)
            return (datetime.now() - mtime) > timedelta(days=30)
        except:
            return True

    def _refresh_emergency_ips(self):
        new_ips = self._fetch_external_ips() or self._builtin_fallback()
        with open(self.emergency_file, 'w') as f:
            json.dump({
                "version": datetime.now().strftime("%Y.%m.%d"),
                "ips": new_ips
            }, f, indent=2)

    def _fetch_external_ips(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self._fetch_source, url): url for url in self.sources}
            for future in concurrent.futures.as_completed(futures):
                if ips := future.result():
                    return ips
        return None

    def _fetch_source(self, url):
        try:
            resp = requests.get(url, timeout=5)
            return self.parse_hosts(resp.text) if resp.ok else None
        except:
            return None

    def _builtin_fallback(self):
        return {
            "github.com": ["20.205.243.166", "140.82.113.4"],
            "assets-cdn.github.com": ["185.199.108.153"]
        }

    def parse_hosts(self, content):
        ip_map = {}
        for line in content.splitlines():
            if parts := re.split(r'\s+', line.strip()):
                if len(parts) > 1 and 'github' in parts[1].lower():
                    domain = parts[1].strip()
                    ip_map.setdefault(domain, []).append(parts[0].strip())
        return ip_map

    def get_github_ips(self):
        try:
            for source in self.sources:
                if ips := self._fetch_source(source):
                    return ips
            with open(self.emergency_file, 'r') as f:
                return json.load(f)['ips']
        except:
            return self._builtin_fallback()

    def benchmark_ips(self, ip_map):
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = {}
            for domain, ips in ip_map.items():
                futures = {executor.submit(self.test_ip, ip): ip for ip in ips}
                sorted_ips = sorted(
                    (f.result() for f in concurrent.futures.as_completed(futures)),
                    key=lambda x: x['score']
                )[:3]
                results[domain] = [ip['address'] for ip in sorted_ips]
            return results

    def test_ip(self, ip):
        result = {'address': ip, 'latency': 999, 'loss': 1.0, 'score': 9999}
        
        # ICMP测试
        ping_result = ping(ip, count=3, timeout=2)
        result.update({
            'latency': ping_result.rtt_avg_ms,
            'loss': ping_result.packet_loss
        })
        
        # HTTP测试
        try:
            start = datetime.now()
            requests.head(
                f'http://{ip}/', 
                headers={'Host': "github.com"},
                timeout=3
            )
            result['http'] = (datetime.now() - start).total_seconds() * 1000
        except:
            result['http'] = 999
        
        # 综合评分
        result['score'] = (result['latency'] * 0.5) + (result['loss'] * 500) + (result['http'] * 0.5)
        return result
#endregion

#region Hosts管理
class HostsManager:
    def __init__(self):
        self.temp_controller = TempModeController()
    
    def apply_optimization(self, optimal_ips, permanent=True):
        original = self.clean_hosts_content()
        new_block = self._generate_block(optimal_ips)
        
        if permanent:
            self._write_permanent(original, new_block)
        else:
            self._write_temporary(original, new_block)
        flush_dns()

    def restore_optimization(self):
        try:
            self.temp_controller.write_hosts(self.clean_hosts_content())
            flush_dns()
            return True
        except Exception as e:
            print(f"恢复失败: {str(e)}")
            return False
    
    def clean_hosts_content(self):
        return MARKER_REGEX.sub('', self.temp_controller._read_hosts()).strip()
    
    def _generate_block(self, ips):
        block = [TEMP_MARKER]
        for domain, ip_list in ips.items():
            block.extend(f"{ip.ljust(16)}{domain}" for ip in ip_list)
        block.append("# End Block")
        return '\n'.join(block)
    
    def _write_permanent(self, original, new_block):
        self.temp_controller.write_hosts(f"{original}\n\n{new_block}")
    
    def _write_temporary(self, original, new_block):
        self.temp_controller.activate()
        self.temp_controller.apply_temp_changes(f"{original}\n{new_block}")
#endregion

#region 主程序
def flush_dns():
    """跨平台DNS刷新"""
    commands = {
        'win32': 'ipconfig /flushdns',
        'darwin': 'dscacheutil -flushcache',
        'linux': 'systemd-resolve --flush-caches'
    }
    subprocess.run(commands[CURRENT_PLATFORM], shell=True, check=True)

def clear_screen():
    os.system('cls' if CURRENT_PLATFORM == 'win32' else 'clear')

def main():
    ensure_admin()
    fixer = ObjectsFixer()
    optimizer = NetworkOptimizer()
    hosts = HostsManager()
    mode = 'temp'

    try:
        while True:
            clear_screen()
            print(f'''GitHub 网络优化工具 v1.3.7.0
当前模式: {'永久' if mode == 'perm' else '临时'}
1. 应用优化配置
2. 移除优化配置
3. 网络诊断修复
4. 切换模式
5. 退出程序''')

            choice = input("请选择操作 (1-5): ").strip()
            
            if choice == "1":
                clear_screen()
                print("🔄 获取最新IP信息...")
                ip_data = optimizer.get_github_ips()
                
                print("⏱️ 网络质量测试中...")
                best_ips = optimizer.benchmark_ips(ip_data)
                
                print("⚡ 应用优化配置...")
                hosts.apply_optimization(best_ips, mode == 'perm')
                print("✅ 优化完成！")
                input("按回车继续...")
                
            elif choice == "2":
                clear_screen()
                if hosts.restore_optimization():
                    print("✅ 恢复完成！")
                else:
                    print("❌ 恢复失败")
                input("按回车继续...")
                
            elif choice == "3":
                clear_screen()
                print("🩺 执行网络诊断...")
                fixer.apply_fix()
                test_connection('github.com', 443)
                test_connection('objects.githubusercontent.com', 443)
                input("按回车继续...")
                
            elif choice == "4":
                mode = 'perm' if mode == 'temp' else 'temp'
                print(f"✅ 已切换至{'永久' if mode == 'perm' else '临时'}模式")
                input("按回车继续...")
                
            elif choice == "5":
                print("👋 感谢使用！")
                sys.exit(0)
                
            else:
                print("⚠️ 无效输入")
                input("按回车继续...")

    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        sys.exit(1)

def test_connection(host, port):
    try:
        with socket.create_connection((host, port), timeout=3):
            print(f"✔️ {host}:{port} 连接正常")
            return True
    except Exception as e:
        print(f"❌ {host}:{port} 连接失败: {str(e)}")
        return False

if __name__ == "__main__":
    main()
#endregion