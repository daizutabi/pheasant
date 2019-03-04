from typing import Any, Dict

config: Dict[str, Any] = {
    'code_pattern': r'#?!\[(.+?)\]\((.+?)\)',

    # Language-extensions
    'language': {
        'python': ['py'],
        'yaml': ['yml'],
        }
}
