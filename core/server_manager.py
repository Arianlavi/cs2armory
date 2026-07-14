import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Dict, Tuple, Optional
from collections import defaultdict


class ServerManager:
    
    ENDPOINTS = [
        "https://api.steampowered.com/ISteamApps/GetSDRConfig/v1/?appid=730",
    ]

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
    }

    CLUSTER_RULES = {
        "China": ["China", "Hong Kong", "Alibaba", "Tencent"],
        "Japan": ["Tokyo"],
        "Stockholm (Sweden)": ["Stockholm"],
        "India": ["Chennai", "Mumbai"]
    }

    def __init__(self):
        self.unclustered: Dict[str, str] = {}
        self.clustered: Dict[str, str] = {}
        self.revision: Optional[str] = None
        self._session = self._build_session()

    @staticmethod
    def _build_session() -> requests.Session:
        session = requests.Session()
        retry = Retry(total=3, backoff_factor=0.6, status_forcelist=[429, 500, 502, 503, 504])
        session.mount("https://", HTTPAdapter(max_retries=retry))
        session.mount("http://", HTTPAdapter(max_retries=retry))
        return session

    def _fetch_raw(self) -> dict:
        last_error = None
        for url in self.ENDPOINTS:
            try:
                response = self._session.get(url, headers=self.HEADERS, timeout=15)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                last_error = e
                continue
        raise ConnectionError(f"Could not reach Steam (tried {len(self.ENDPOINTS)} endpoints): {last_error}")

    def fetch_servers(self) -> Tuple[Dict[str, str], Dict[str, str], str]:
        try:
            data = self._fetch_raw()
            self.revision = str(data.get("revision") or "unknown")

            pops = data.get("pops")
            if not isinstance(pops, dict) or not pops:
                raise ValueError("Response contained no server ('pops') data")

            clustered_temp = defaultdict(list)
            unclustered_temp = defaultdict(list)
            for pop_id, pop_data in pops.items():
                if not isinstance(pop_data, dict):
                    continue
                ips = []
                relays = pop_data.get("relays")
                if isinstance(relays, list):
                    ips.extend(r.get("ipv4") for r in relays if isinstance(r, dict) and r.get("ipv4"))

                addr_ranges = pop_data.get("service_address_ranges")
                if isinstance(addr_ranges, list):
                    ips.extend(a for a in addr_ranges if isinstance(a, str) and a)

                ips = [ip for ip in ips if ip]
                if not ips:
                    continue
                desc = pop_data.get("desc", "")
                server_name = f"{desc} ({pop_id})" if desc else str(pop_id)
                clustered = False
                for cluster_name, keywords in self.CLUSTER_RULES.items():
                    if any(k in server_name for k in keywords):
                        clustered_temp[cluster_name].extend(ips)
                        clustered = True
                        break
                unclustered_temp[server_name].extend(ips)
                if not clustered:
                    clustered_temp[server_name].extend(ips)

            if not unclustered_temp:
                raise ValueError("No servers with usable IPs were found in the response")

            self.clustered = {k: ",".join(v) for k, v in clustered_temp.items()}
            self.unclustered = {k: ",".join(v) for k, v in unclustered_temp.items()}
            return self.clustered, self.unclustered, self.revision
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to reach Steam: {e}")
        except (KeyError, ValueError) as e:
            raise RuntimeError(f"Unexpected API response format: {e}")

    def get_clustered(self) -> Dict[str, str]:
        return self.clustered

    def get_unclustered(self) -> Dict[str, str]:
        return self.unclustered

    def get_revision(self) -> Optional[str]:
        return self.revision
