"""Configuration for AI Q&A System."""

import yaml
from pathlib import Path
from typing import Dict, Any

CONFIG_PATH = Path(__file__).parent / "config.yaml"

DEFAULT_CONFIG: Dict[str, Any] = {
    "system": {
        "name": "AI-Question-Answering-System",
        "version": "1.0.0"
    },
    "search": {
        "top_k": 5,
        "threshold": 0.3
    },
    "conversation": {
        "max_history": 5,
        "session_timeout_minutes": 30
    },
    "output": {
        "format": "json",
        "include_sources": True
    }
}


def load_config(path: str = None) -> Dict[str, Any]:
    config_path = Path(path) if path else CONFIG_PATH
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            user_config = yaml.safe_load(f) or {}
        return merge_configs(DEFAULT_CONFIG, user_config)
    return DEFAULT_CONFIG


def merge_configs(base: Dict, override: Dict) -> Dict:
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    return result


if __name__ == "__main__":
    cfg = load_config()
    print(yaml.dump(cfg, default_flow_style=False, allow_unicode=True))
