import ctypes
import sys
import os
import re
import requests
import concurrent.futures
import subprocess
import atexit
import json
import socket
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import NamedTemporaryFile
from pythonping import ping

#region 核心配置
HOSTS_PATH = r'C:\Windows\System32\drivers\etc\hosts'
TEMP_MARKER = "# GitHubAccelerator Block"
MARKER_REGEX = re.compile(rf"{re.escape(TEMP_MARKER)}.*?{re.escape('# End Block')}", re.DOTALL | re.MULTILINE)
EMERGENCY_FILE = "emergency_ips.json"
#endregion

#region 权限管理
def ensure_admin():
    """确保以管理员权限运行"""
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit(0)
#endregion

#region 临时模式管理器
class TempModeController:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._backup = None
            cls._instance._active = False
        return cls._instance
    
    def activate(self):
        """进入临时模式"""
        if not self._active:
            self._backup = self._read_hosts()
            self._active = True
            atexit.register(self.restore)

    def deactivate(self):
        """退出临时模式，提前恢复"""
        if self._active:
            self.restore()
            self._active = False
            atexit.unregister(self.restore)
    
    def apply_temp_changes(self, content):
        """应用临时更改"""
        if self._active:
            self.write_hosts(content)
    
    def restore(self):
        """恢复初始配置"""
        if self._backup:
            self.write_hosts(self._backup)
            self._flush_dns()
    
    def _read_hosts(self):
        """读取Hosts"""
        try:
            with open(HOSTS_PATH, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(HOSTS_PATH, 'r', encoding='latin-1') as f:
                return f.read()
    
    def write_hosts(self, content):
        """安全写入Hosts文件"""
        with NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as tmp:
            tmp.write(content)
            tmp_filename = tmp.name
        os.replace(tmp_filename, HOSTS_PATH)
    
    def _flush_dns(self):
        subprocess.run('ipconfig /flushdns', shell=True, check=True)
#endregion

#region 智能修复模块
class ObjectsFixer:
    TARGET_DOMAIN = "objects.githubusercontent.com"
    SOURCES = [
        "https://gitlab.com/ineo6/hosts/-/raw/master/hosts",
        "https://fastly.jsdelivr.net/gh/521xueweihan/GitHub520@main/hosts",
        "https://ghproxy.com/https://raw.githubusercontent.com/justjavac/ReplaceGoogleCDN/master/hosts"
    ]
    
    def __init__(self):
        self.current_ips = []
        self.last_checked = datetime.min

    def is_accessible(self):
        """智能连通性检测"""
        try:
            # TCP握手测试
            socket.create_connection((self.TARGET_DOMAIN, 443), timeout=3)
            # HTTP响应测试
            resp = requests.head(f"https://{self.TARGET_DOMAIN}", timeout=5)
            return resp.status_code < 500
        except:
            return False

    def fetch_latest_ips(self):
        """多源IP获取"""
        collected = set()
        for source in self.SOURCES:
            try:
                resp = requests.get(source, timeout=5)
                if resp.ok:
                    ips = self._parse_hosts(resp.text)
                    collected.update(ips)
            except:
                continue
        return list(collected) or self._fallback_ips()

    def _parse_hosts(self, content):
        """专用解析逻辑"""
        ips = []
        for line in content.splitlines():
            parts = line.strip().split()
            if len(parts) > 1 and self.TARGET_DOMAIN in parts:
                ips.append(parts[0])
        return ips

    def _fallback_ips(self):
        """内置应急IP（每日更新）"""
        return [
            "185.199.111.133",
            "185.199.108.133",
            "185.199.110.133"
        ]

    def validate_ip(self, ip):
        """综合验证IP有效性"""
        if not self._test_port(ip, 443):
            return False
        return self._verify_ssl(ip)

    def _test_port(self, ip, port):
        try:
            socket.create_connection((ip, port), timeout=3)
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
        """执行完整修复流程"""
        if (datetime.now() - self.last_checked).seconds < 3600:
            return
        
        if not self.is_accessible():
            print("🔧 检测到objects.githubusercontent.com连接异常，尝试自动修复...")
            candidate_ips = self.fetch_latest_ips()
            valid_ips = [ip for ip in candidate_ips if self.validate_ip(ip)]
            
            if valid_ips:
                self._update_hosts(valid_ips)
                self.current_ips = valid_ips
                self.last_checked = datetime.now()
                print(f"✅ 已更新有效IP：{', '.join(valid_ips[:3])}...")

    def _update_hosts(self, ips):
        """安全更新Hosts文件"""
        hosts_mgr = HostsManager()
        original = hosts_mgr.clean_hosts_content()
        
        # 清除旧记录
        old_records = re.compile(rf"\d+\.\d+\.\d+\.\d+\s+{re.escape(self.TARGET_DOMAIN)}")
        cleaned = old_records.sub('', original)
        
        # 添加新记录
        new_block = "\n".join([f"{ip.ljust(16)}{self.TARGET_DOMAIN}" for ip in ips])
        content = f"{cleaned}\n{TEMP_MARKER}\n{new_block}\n# End Block"
        
        hosts_mgr.temp_controller.write_hosts(content)
        hosts_mgr.flush_dns()
#endregion

#region 网络优化模块
class NetworkOptimizer:
    def __init__(self):
        self.sources = [
            'https://gitee.com/frankwuzp/github-host/raw/main/hosts',
            'https://mirror.ghproxy.com/https://raw.githubusercontent.com/521xueweihan/GitHub520/main/hosts',
            'https://fastly.jsdelivr.net/gh/521xueweihan/GitHub520@main/hosts'
        ]
        self.emergency_file = Path(EMERGENCY_FILE)
        self._init_emergency_file()

    def _init_emergency_file(self):
        """初始化应急IP文件"""
        try:
            if not self.emergency_file.exists() or self._needs_update():
                print("🔄 正在更新应急IP文件...")
                self._refresh_emergency_ips()
        except Exception as e:
            print(f"⚠️ 应急文件初始化失败: {str(e)}")

    def _needs_update(self) -> bool:
        """检查是否超过30天未更新"""
        try:
            mtime = datetime.fromtimestamp(self.emergency_file.stat().st_mtime)
            return (datetime.now() - mtime) > timedelta(days=30)
        except:
            return True

    def _refresh_emergency_ips(self):
        """更新应急IP文件"""
        new_ips = self._fetch_external_ips() or self._builtin_fallback()
        data = {
            "version": datetime.now().strftime("%Y.%m.%d"),
            "last_updated": datetime.now().isoformat(),
            "ips": new_ips
        }
        try:
            with open(self.emergency_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️ 无法写入应急文件: {str(e)}")

    def _fetch_external_ips(self):
        """从外部源获取IP"""
        for url in self.sources:
            try:
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    return self._safe_parse(resp.text)
            except Exception as e:
                print(f"源 {url} 获取失败: {str(e)}")
        return None

    def _safe_parse(self, content):
        """安全解析并过滤危险域名"""
        raw_map = self.parse_hosts(content)
        return {k: v for k, v in raw_map.items() if 'objects.githubusercontent.com' not in k}

    @staticmethod
    def _builtin_fallback():
        """内置应急IP（已排除objects.githubusercontent.com）"""
        return {
            "github.com": ["20.205.243.166", "140.82.113.4"],
            "assets-cdn.github.com": ["185.199.108.153", "185.199.109.153"]
        }

    def parse_hosts(self, content):
        """解析Hosts格式内容"""
        ip_map = {}
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                parts = re.split(r'\s+', line)
                if len(parts) > 1 and 'github' in parts[1].lower():
                    domain = parts[1].strip()
                    ip_map.setdefault(domain, []).append(parts[0].strip())
        return ip_map

    def get_github_ips(self):
        """获取最新IP数据"""
        try:
            for source in self.sources[:2]:
                try:
                    resp = requests.get(source, timeout=5)
                    if resp.status_code == 200:
                        return self._safe_parse(resp.text)
                except:
                    continue
            with open(self.emergency_file, 'r') as f:
                data = json.load(f)
                return data['ips']
        except Exception as e:
            print(f"⚠️ 全部源失效，使用内置应急IP: {str(e)}")
            return self._builtin_fallback()

    def benchmark_ips(self, ip_map):
        """并发性能测试"""
        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
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
        """综合网络测试"""
        result = {'address': ip, 'latency': 999, 'loss': 1.0, 'score': 9999}
        
        # ICMP测试
        ping_result = ping(ip, count=3, timeout=2)
        result['latency'] = ping_result.rtt_avg_ms
        result['loss'] = ping_result.packet_loss
        
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
        
        # 评分算法
        result['score'] = (result['latency'] * 0.5) + (result['loss'] * 500) + (result['http'] * 0.5)
        return result
#endregion

#region Hosts操作
class HostsManager:
    def __init__(self):
        self.temp_controller = TempModeController()
    
    def apply_optimization(self, optimal_ips, permanent=True):
        """应用优化配置"""
        original = self.clean_hosts_content()
        new_block = self.generate_block(optimal_ips)
        
        if permanent:
            self.write_permanent(original, new_block)
        else:
            self.write_temporary(original, new_block)
        self.flush_dns()

    def restore_optimization(self):
        """安全移除所有优化"""
        try:
            cleaned = self.clean_hosts_content()
            self.temp_controller.write_hosts(cleaned)
            self.flush_dns()
            return True
        except Exception as e:
            print(f"恢复失败: {str(e)}")
            return False
    
    def clean_hosts_content(self):
        """获取清理后的内容"""
        content = self.temp_controller._read_hosts()
        return MARKER_REGEX.sub('', content).strip()
    
    def generate_block(self, ips):
        """生成配置块"""
        lines = [TEMP_MARKER]
        for domain, ip_list in ips.items():
            lines.extend(f"{ip.ljust(16)}{domain}" for ip in ip_list)
        lines.append("# End Block")
        return '\n'.join(lines)
    
    def write_permanent(self, original, new_block):
        """永久写入"""
        content = f"{original}\n\n{new_block}"
        self.temp_controller.write_hosts(content)
    
    def write_temporary(self, original, new_block):
        """临时写入"""
        self.temp_controller.activate()
        content = f"{original}\n{new_block}"
        self.temp_controller.apply_temp_changes(content)
    
    def flush_dns(self):
        subprocess.run('ipconfig /flushdns', shell=True, check=True)
#endregion

#region 应用入口
def main(mode='temp'):
    ensure_admin()
    
    # 前置修复检测
    fixer = ObjectsFixer()
    fixer.apply_fix()
    
    optimizer = NetworkOptimizer()
    hosts = HostsManager()

    try:
        current_mode = '永久' if mode == 'perm' else '临时'
        while True:
            os.system('cls')
            print(f'''GitHub 网络优化工具 v1.0 Made by EveGlow(YangChen114514)
当前模式: {current_mode}
1. 应用优化配置
2. 移除优化配置
3. 切换模式
4. 退出程序''')
            
            choice = input("请选择操作 (1-4): ").strip()
            
            if choice == "1":
                os.system('cls')
                print("🔄 正在获取最新IP信息...")
                ip_data = optimizer.get_github_ips()
                
                print("⏱️ 正在进行网络质量测试...")
                best_ips = optimizer.benchmark_ips(ip_data)
                
                print("⚡ 正在应用优化配置...")
                hosts.apply_optimization(best_ips, permanent=(mode == 'perm'))
                print("✅ 优化已完成！")
                input("按回车键继续...")
                
            elif choice == "2":
                os.system('cls')
                print("🔄 正在恢复原始配置...")
                if hosts.restore_optimization():
                    print("✅ 恢复完成！")
                else:
                    print("❌ 恢复失败")
                input("按回车键继续...")
                
            elif choice == "3":
                mode = 'perm' if mode == 'temp' else 'temp'
                current_mode = '永久' if mode == 'perm' else '临时'
                print(f"✅已切换至 {current_mode} 模式")
                input("按回车键继续...")
                
            elif choice == "4":
                print("👋 感谢使用！")
                sys.exit(0)
                
            else:
                print("⚠️ 无效输入，请重新选择")
                input("按回车键继续...")

    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        hosts.temp_controller.deactivate()
        input("按回车键退出...")
        sys.exit(1)

if __name__ == "__main__":
    main()
#endregion