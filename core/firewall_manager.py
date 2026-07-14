import subprocess
import os
import platform
from typing import Dict, List

_IS_WINDOWS = platform.system().lower() == "windows"
_NO_WINDOW_FLAG = 0x08000000  


class FirewallManager:
    NETSHPATH = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "netsh.exe")
    RULE_PREFIX = "CS2Armory_"
    MAX_IPS_PER_RULE = 300

    def __init__(self):
        if not os.path.isfile(self.NETSHPATH):
            raise FileNotFoundError("netsh.exe not found")

    def _run_netsh(self, args: str) -> tuple:
        cmd = f'"{self.NETSHPATH}" {args}'
        popen_kwargs = dict(
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL, shell=True, text=True,
        )
        if _IS_WINDOWS:
            popen_kwargs["creationflags"] = _NO_WINDOW_FLAG
        p = subprocess.Popen(cmd, **popen_kwargs)
        try:
            out, err = p.communicate(timeout=20)
        except subprocess.TimeoutExpired:
            p.kill()
            raise RuntimeError("netsh timed out (is the Windows Firewall service running?)")
        return out, err, p.returncode

    @staticmethod
    def _chunk_ips(ips: str, size: int) -> List[str]:
        ip_list = [ip.strip() for ip in ips.split(",") if ip.strip()]
        return [",".join(ip_list[i:i + size]) for i in range(0, len(ip_list), size)] or [ips]

    def block_server(self, name: str, ips: str) -> bool:
        rule = self.RULE_PREFIX + name.replace(" ", "")
        self.unblock_server(name)

        errors = []
        for chunk in self._chunk_ips(ips, self.MAX_IPS_PER_RULE):
            args = f'advfirewall firewall add rule name="{rule}" dir=out action=block protocol=ANY remoteip={chunk}'
            out, err, code = self._run_netsh(args)
            if code != 0:
                errors.append(err.strip() or out.strip() or f"exit code {code}")

        if errors:
            raise RuntimeError(f"Block failed for '{name}': {'; '.join(errors)}")
        if not self.is_blocked(name):
            raise RuntimeError(f"netsh reported success for '{name}' but no rule was found afterward.")
        return True

    def unblock_server(self, name: str) -> bool:
        rule = self.RULE_PREFIX + name.replace(" ", "")
        args = f'advfirewall firewall delete rule name="{rule}"'
        out, err, code = self._run_netsh(args)
        combined = f"{out}\n{err}".lower()
        if code != 0 and "no rules match" not in combined:
            raise RuntimeError(f"Unblock failed: {err.strip() or out.strip()}")
        return True

    def is_blocked(self, name: str) -> bool:
        rule = self.RULE_PREFIX + name.replace(" ", "")
        args = f'advfirewall firewall show rule name="{rule}"'
        out, err, code = self._run_netsh(args)
        return code == 0 and "no rules match" not in out.lower()

    def block_all(self, servers: Dict[str, str]) -> Dict[str, bool]:
        results, errors = {}, {}
        for name, ips in servers.items():
            try:
                self.block_server(name, ips)
                results[name] = True
            except Exception as e:
                results[name] = False
                errors[name] = str(e)
        if errors:
            details = "\n".join(f"- {n}: {msg}" for n, msg in errors.items())
            raise RuntimeError(f"{len(errors)} server(s) failed to block:\n{details}")
        return results

    def unblock_all(self, servers: Dict[str, str]) -> Dict[str, bool]:
        results, errors = {}, {}
        for name in servers.keys():
            try:
                self.unblock_server(name)
                results[name] = True
            except Exception as e:
                results[name] = False
                errors[name] = str(e)
        if errors:
            details = "\n".join(f"- {n}: {msg}" for n, msg in errors.items())
            raise RuntimeError(f"{len(errors)} server(s) failed to unblock:\n{details}")
        return results
