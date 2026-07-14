import json
import os
import shutil
from typing import Dict, List, Optional


class PresetManager:

    APP_FOLDER_NAME = "CS2Armory"
    LEGACY_RELATIVE_FILE = "presets.json"  # old location, kept for migration

    def __init__(self):
        self.PRESET_FILE = os.path.join(self._get_data_dir(), "presets.json")
        self._ensure_file_exists()

    @classmethod
    def _get_data_dir(cls) -> str:
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or os.path.expanduser("~")
        data_dir = os.path.join(base, cls.APP_FOLDER_NAME)
        os.makedirs(data_dir, exist_ok=True)
        return data_dir

    def _ensure_file_exists(self):
        if not os.path.isfile(self.PRESET_FILE):
            # Pick up a presets.json sitting next to the executable from
            if os.path.isfile(self.LEGACY_RELATIVE_FILE):
                try:
                    shutil.copyfile(self.LEGACY_RELATIVE_FILE, self.PRESET_FILE)
                    return
                except Exception:
                    pass
            with open(self.PRESET_FILE, "w") as f:
                json.dump({}, f, indent=4)

    def load_all(self) -> Dict:
        try:
            with open(self.PRESET_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def save_all(self, presets: Dict):

        tmp_path = self.PRESET_FILE + ".tmp"
        with open(tmp_path, "w") as f:
            json.dump(presets, f, indent=4)
        os.replace(tmp_path, self.PRESET_FILE)

    def get_preset(self, name: str) -> Optional[Dict]:
        presets = self.load_all()
        return presets.get(name.replace(" ", ""))

    def add_preset(self, name: str, servers: List[str], clustered: bool) -> bool:
        key = name.replace(" ", "")
        presets = self.load_all()
        if key in presets:
            return False
        presets[key] = {
            "presetName": name,
            "clustered": clustered,
            "servers": servers
        }
        self.save_all(presets)
        return True

    def update_preset(self, old_name: str, new_name: str, servers: List[str], clustered: bool) -> bool:
        old_key = old_name.replace(" ", "")
        presets = self.load_all()
        if old_key not in presets:
            return False
        del presets[old_key]
        key = new_name.replace(" ", "")
        presets[key] = {
            "presetName": new_name,
            "clustered": clustered,
            "servers": servers
        }
        self.save_all(presets)
        return True

    def delete_preset(self, name: str) -> bool:
        key = name.replace(" ", "")
        presets = self.load_all()
        if key not in presets:
            return False
        del presets[key]
        self.save_all(presets)
        return True

    def get_presets_for_cluster(self, clustered: bool) -> Dict:
        all_presets = self.load_all()
        filtered = {}
        for key, data in all_presets.items():
            if data.get("clustered") == clustered:
                filtered[key] = data
        return filtered
