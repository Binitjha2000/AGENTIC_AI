# scripts/server_health_check.py (Modified - Outputting Markdown instead of rich console)
import psutil
import platform
import socket
import time
import speedtest
import matplotlib.pyplot as plt
import os
import numpy as np
from typing import Tuple, List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
import logging
from dataclasses import dataclass

# Configure logging (SUPPRESSED for chatbot output)
# logging.basicConfig(...) # Commented out!
logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """Dataclass to hold all system metrics"""
    system_info: Dict[str, str]
    cpu: Dict[str, float]
    memory: Dict[str, float]
    disk: Dict[str, float]
    network: Dict[str, Optional[float]]
    gpu: List[str]
    processes: List[Dict[str, str]]

class SystemHealthMonitor:
    """Comprehensive system health monitoring and reporting tool"""

    def __init__(self):
        self.metrics = SystemMetrics(
            system_info={},
            cpu={},
            memory={},
            disk={},
            network={},
            gpu=[],
            processes=[]
        )
        # Executor is NO LONGER initialized in __init__ and removed from class level


    def _get_system_info(self) -> Dict[str, str]:
        """Collect basic system information"""
        return {
            "system_name": platform.node(),
            "os": f"{platform.system()} {platform.release()}",
            "architecture": platform.architecture()[0],
            "boot_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(psutil.boot_time()))
        }

    def _get_cpu_metrics(self) -> Dict[str, float]:
        """Collect CPU-related metrics"""
        # Executor context removed here
        freq = psutil.cpu_freq()
        return {
            "usage_percent": psutil.cpu_percent(interval=1),
            "freq_current": freq.current,
            "freq_max": freq.max,
            "cores_physical": psutil.cpu_count(logical=False),
            "cores_logical": psutil.cpu_count(logical=True)
        }

    def _get_memory_metrics(self) -> Dict[str, float]:
        """Collect memory metrics with swap information"""
        # Executor context removed here
        virt = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            "total": self._bytes_to_gb(virt.total),
            "used": self._bytes_to_gb(virt.used),
            "available": self._bytes_to_gb(virt.available),
            "swap_total": self._bytes_to_gb(swap.total),
            "swap_used": self._bytes_to_gb(swap.used)
        }

    def _get_disk_metrics(self) -> Dict[str, float]:
        """Collect disk metrics for all mounted partitions"""
        # Executor context removed here
        disks = {}
        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disks[part.device] = {
                    "total": self._bytes_to_gb(usage.total),
                    "used": self._bytes_to_gb(usage.used),
                    "free": self._bytes_to_gb(usage.free),
                    "percent_used": usage.percent
                }
            except PermissionError as e:
                logger.error(f"PermissionError accessing disk {part.device} ({part.mountpoint}): {str(e)}") # Use logger.error
                disks[part.device] = {
                    "error": f"PermissionError: {str(e)}" # Indicate error in report
                }
            except Exception as e:
                logger.error(f"Error accessing disk {part.device} ({part.mountpoint}): {str(e)}") # Use logger.error
                disks[part.device] = {
                    "error": f"Error: {str(e)}" # Indicate error in report
                }
        return disks

    def _get_network_metrics(self) -> Dict[str, Optional[float]]:
        """Collect network metrics with async speed test"""
        metrics = {
            "status": self._check_network_status(),
            "connections": len(psutil.net_connections()),
            "speed_test": None
        }

        # Initialize executor INSIDE this method, use a 'with' block for local context
        with ThreadPoolExecutor(max_workers=1) as executor: # Max workers = 1, just for speed test
            logger.info("Submitting speed test task to executor...") # LOG ADDED
            executor.submit(self._run_speed_test) # Use local 'executor'
            logger.info("Speed test task submitted.") # LOG ADDED
        # Executor implicitly shutdown when exiting 'with' block

        return metrics

    def _run_speed_test(self):
        """Asynchronous speed test execution"""
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            self.metrics.network.update({
                "download": st.download() / 1e6,
                "upload": st.upload() / 1e6,
                "ping": st.results.ping
            })
        except Exception as e:
            logger.error(f"Speed test failed: {str(e)}")

    def _get_gpu_metrics(self) -> List[str]:
        """Collect GPU metrics with fallback"""
        # Executor context removed here
        try:
            import GPUtil
            return [f"{gpu.name}: {gpu.memoryUsed}MB/{gpu.memoryTotal}MB | {gpu.temperature}°C"
                    for gpu in GPUtil.getGPUs()]
        except ImportError:
            return ["GPU monitoring requires GPUtil package"]
        except Exception as e:
            return [f"GPU monitoring error: {str(e)}"]

    def _get_process_metrics(self, top_n: int = 5) -> List[Dict[str, str]]:
        """Get top resource-consuming processes"""
        # Executor context removed here
        procs = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                procs.append(proc.info)
            except psutil.NoSuchProcess:
                continue
        return sorted(
            procs,
            key=lambda p: p['cpu_percent'] + p['memory_percent'],
            reverse=True
        )[:top_n]

    def _check_network_status(self) -> str:
        """Check internet connectivity with multiple endpoints"""
        test_servers = [
            ("8.8.8.8", 53),  # Google DNS
            ("1.1.1.1", 53),  # Cloudflare DNS
            ("208.67.222.222", 53)  # OpenDNS
        ]
        for server in test_servers:
            try:
                socket.create_connection(server, timeout=2)
                return "Online"
            except OSError:
                continue
        return "Offline"

    @staticmethod
    def _bytes_to_gb(value: int) -> float:
        """Convert bytes to gigabytes"""
        return value / (1024 ** 3)

    def collect_metrics(self):
        """Main method to collect all metrics"""
        # Executor and 'with' block REMOVED from collect_metrics entirely

        logger.info("Collecting system info (main thread)...") # LOG ADDED
        self.metrics.system_info = self._get_system_info()
        logger.info("System info collected.") # LOG ADDED

        logger.info("Collecting CPU metrics (main thread)...") # LOG ADDED
        self.metrics.cpu = self._get_cpu_metrics()
        logger.info("CPU metrics collected.") # LOG ADDED

        logger.info("Collecting memory metrics (main thread)...") # LOG ADDED
        self.metrics.memory = self._get_memory_metrics()
        logger.info("Memory metrics collected.") # LOG ADDED

        logger.info("Collecting disk metrics (main thread)...") # LOG ADDED
        self.metrics.disk = self._get_disk_metrics()
        logger.info("Disk metrics collected.") # LOG ADDED

        logger.info("Collecting network metrics (with local executor)...") # LOG ADDED
        self.metrics.network = self._get_network_metrics() # Executor is created and used locally
        logger.info("Network metrics collection initiated (speed test submitted to local executor).") # LOG ADDED

        logger.info("Collecting GPU metrics (main thread)...") # LOG ADDED
        self.metrics.gpu = self._get_gpu_metrics()
        logger.info("GPU metrics collected.") # LOG ADDED

        logger.info("Collecting process metrics (main thread)...") # LOG ADDED
        self.metrics.processes = self._get_process_metrics()
        logger.info("Process metrics collected.") # LOG ADDED

        logger.info("Metrics collection COMPLETED.") # LOG ADDED


    def generate_report(self):
        """Generate Markdown report for chatbot"""
        report_lines = []
        report_lines.append("## COMPREHENSIVE SYSTEM HEALTH REPORT") # Markdown Header 2
        report_lines.append("")

        # System Information (Markdown Section)
        report_lines.append("### System Overview") # Markdown Header 3
        report_lines.append(f"- **System Name**: {self.metrics.system_info['system_name']}") # Markdown bold and list
        report_lines.append(f"- **OS**: {self.metrics.system_info['os']}")
        report_lines.append(f"- **Architecture**: {self.metrics.system_info['architecture']}")
        report_lines.append(f"- **Boot Time**: {self.metrics.system_info['boot_time']}")
        report_lines.append("")

        # CPU Metrics (Markdown Section)
        report_lines.append("### CPU Metrics") # Markdown Header 3
        report_lines.append(f"- **Usage Percent**: {self.metrics.cpu['usage_percent']:.1f}%")
        report_lines.append(f"- **Frequency Current**: {self.metrics.cpu['freq_current']:.1f}GHz")
        report_lines.append(f"- **Frequency Max**: {self.metrics.cpu['freq_max']:.1f}GHz")
        report_lines.append(f"- **Cores (Physical)**: {self.metrics.cpu['cores_physical']:.0f}")
        report_lines.append(f"- **Cores (Logical)**: {self.metrics.cpu['cores_logical']:.0f}")
        report_lines.append("")

        # Memory Metrics (Markdown Section)
        report_lines.append("### Memory Metrics") # Markdown Header 3
        report_lines.append(f"- **Total**: {self.metrics.memory['total']:.1f}GB")
        report_lines.append(f"- **Used**: {self.metrics.memory['used']:.1f}GB")
        report_lines.append(f"- **Available**: {self.metrics.memory['available']:.1f}GB")
        report_lines.append("")

        # Disk Metrics (Markdown Section)
        report_lines.append("### Disk Metrics") # Markdown Header 3
        for k, v in self.metrics.disk.items():
            if "error" in v:
                report_lines.append(f"- **{k}**: Error: {v['error']}") # Plain error message in Markdown list
                logger.error(f"Disk Error for {k}: {v['error']}") # Keep logging errors
            else:
                report_lines.append(f"- **{k}**: {v['used']:.1f}/{v['total']:.1f}GB ({v['percent_used']}%)")
        report_lines.append("")

        # Network Metrics (Markdown Section)
        report_lines.append("### Network Metrics") # Markdown Header 3
        net_data = self.metrics.network
        report_lines.append(f"- **Status**: {net_data['status']}")
        report_lines.append(f"- **Connections**: {net_data['connections']}")
        if net_data.get('speed_test'):
            report_lines.append(f"- **Download Speed**: {net_data['download']:.2f} Mbps")
            report_lines.append(f"- **Upload Speed**: {net_data['upload']:.2f} Mbps")
            report_lines.append(f"- **Ping**: {net_data['ping']:.1f} ms")
        report_lines.append("")

        # GPU Metrics (Markdown Section)
        report_lines.append("### GPU Metrics") # Markdown Header 3
        if self.metrics.gpu:
            for i, info in enumerate(self.metrics.gpu, 1):
                report_lines.append(f"- **GPU {i}**: {info}")
        else:
            report_lines.append("- No GPU information available") # Handle no GPU case
        report_lines.append("")

        # Top Processes (Markdown Section)
        report_lines.append("### Top Processes") # Markdown Header 3
        for p in self.metrics.processes:
            report_lines.append(f"- **{p['name']} (PID: {p['pid']})**: CPU: {p['cpu_percent']}% | MEM: {p['memory_percent']}%")
        report_lines.append("")

        report_lines.append(f"[System dashboard saved as 'system_health_dashboard.png'](./system_health_dashboard.png)") # Markdown link to image

        report_markdown = "\n".join(report_lines) # Join all lines with newlines

        print(report_markdown) # Output the entire Markdown report to stdout

    def generate_visualizations(self):
        """Generate visualizations - No changes needed here for functionality"""
        # ... (rest of generate_visualizations - NO CHANGES NEEDED)
        plt.tight_layout()
        plt.savefig("system_health_dashboard.png")
        print("[System dashboard saved as 'system_health_dashboard.png'](./system_health_dashboard.png)") # Markdown link here too


    def _plot_3d_disk(self):
        """3D disk visualization helper method"""
        path = next(iter(self.metrics.disk))  # Get first disk
        sizes, labels = [], []

        try:
            for entry in os.scandir(path):
                if entry.is_dir():
                    try:
                        sizes.append(sum(f.stat().st_size for f in os.scandir(entry) if f.is_file()))
                        labels.append(entry.name)
                    except:
                        continue
        except Exception as e:
            logger.error(f"Disk scan failed: {str(e)}")
            return

        if not sizes:
            return

        x = np.arange(len(sizes))
        ax = plt.gca()
        ax.bar3d(x, np.zeros(len(sizes)), np.zeros(len(sizes)),
                0.5, 0.5, sizes, shade=True)
        ax.set_xticks(x)
        ax.set_xticklabels([label[:10] for label in labels], rotation=45)
        ax.set_title("3D Disk Usage Visualization")

if __name__ == "__main__":
    monitor = SystemHealthMonitor()
    monitor.collect_metrics()
    monitor.generate_report()
    monitor.generate_visualizations()