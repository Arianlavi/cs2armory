import subprocess
import platform
import threading
import time
from typing import Dict, List, Optional, Callable

_IS_WINDOWS = platform.system().lower() == "windows"
_NO_WINDOW_FLAG = 0x08000000  


def _popen_kwargs():
    kwargs = dict(stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, text=True)
    if _IS_WINDOWS:
        kwargs["creationflags"] = _NO_WINDOW_FLAG
    return kwargs


class PingWorker(threading.Thread):
    

    def __init__(self, server_name: str, ip_addresses: List[str], callback: Callable):
        super().__init__()
        self.server_name = server_name
        self.ip_addresses = ip_addresses
        self.callback = callback
        self.result = None
        self.daemon = True

    def run(self):
        for ip in self.ip_addresses:
            if not ip:
                continue
            try:
                cmd = ["ping", "-n", "1", "-w", "1000", ip] if _IS_WINDOWS else ["ping", "-c", "1", "-W", "1", ip]

                start = time.time()
                proc = subprocess.Popen(cmd, **_popen_kwargs())
                stdout, _ = proc.communicate(timeout=2)
                elapsed_ms = (time.time() - start) * 1000

                if proc.returncode == 0:
                    latency = self._parse_ping_output(stdout)
                    if latency is None:
                        latency = max(0, int(elapsed_ms))
                    self.result = latency
                    self.callback(self.server_name, latency)
                    return
            except Exception:
                continue

        self.result = -1
        self.callback(self.server_name, -1)

    def _parse_ping_output(self, output: str) -> Optional[int]:
        for line in output.splitlines():
            if "time=" in line:
                try:
                    part = line.split("time=")[1].split()[0]
                    return int(float(part[:-2])) if part.endswith("ms") else int(float(part))
                except Exception:
                    pass
            elif "time<" in line:
                return 0
        return None


class PingManager:

    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.workers: List[PingWorker] = []
        self.results: Dict[str, int] = {}
        self.callbacks: List[Callable] = []

    def ping_servers(self, servers: Dict[str, str], callback: Callable, on_complete: Optional[Callable] = None):

        self.results.clear()
        self.workers.clear()
        self.callbacks.append(callback)

        for name, ips in servers.items():
            ip_list = [ip.strip() for ip in ips.split(",") if ip.strip()]
            self.workers.append(PingWorker(name, ip_list, self._on_result))

        for i in range(0, len(self.workers), self.max_workers):
            batch = self.workers[i:i + self.max_workers]
            for w in batch:
                w.start()
            for w in batch:
                w.join()

        if on_complete:
            on_complete()

    def _on_result(self, server_name: str, latency: int):
        self.results[server_name] = latency
        for cb in self.callbacks:
            cb(server_name, latency)

    def get_result(self, server_name: str) -> Optional[int]:
        return self.results.get(server_name)
