"""
設定関連のモジュール
"""
import json
from pathlib import Path

def get_settings():
    """設定ファイルを読み込む"""
    settings_path = Path(__file__).parent / "settings.json"
    with open(settings_path) as f:
        return json.load(f)

__all__ = ["get_settings"]
