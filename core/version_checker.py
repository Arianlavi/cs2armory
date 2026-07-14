import requests
import re
from typing import Optional, Tuple

class VersionChecker:
    REPO_API = "https://api.github.com/repos/arianlavi/cs2armory/releases"

    @classmethod
    def check(cls, current_version: str) -> Optional[Tuple[str, str]]:
        try:
            headers = {"User-Agent": "CS2Armory"}
            response = requests.get(cls.REPO_API, headers=headers, timeout=5)
            response.raise_for_status()
            releases = response.json()
            if not releases:
                return None
            latest = releases[0]
            tag = latest.get("tag_name", "").strip()
            if tag.startswith("v"):
                tag = tag[1:]
            if cls._is_newer(tag, current_version):
                return tag, latest.get("html_url")
            return None
        except:
            return None

    @staticmethod
    def _is_newer(tag: str, current: str) -> bool:
        def parse(v):
            parts = re.split(r'[._-]', v)
            return [int(p) for p in parts if p.isdigit()]
        tag_parts = parse(tag)
        curr_parts = parse(current)
        if not tag_parts:
            return False
        if not curr_parts:
            return True
        for t, c in zip(tag_parts, curr_parts):
            if t > c:
                return True
            elif t < c:
                return False
        return len(tag_parts) > len(curr_parts)