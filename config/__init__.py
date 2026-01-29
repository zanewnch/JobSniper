"""
設定模組

匯出所有設定：
    from config import BASE_URL, RUN_CONFIG
"""

# 固定常數
from .constants import (
    BASE_URL,
    OUTPUT_BASE_DIR,
    MANUAL_HANDLE_DIR,
    SESSION_FILE,
    CSV_FIELDNAMES,
    DELAY,
    DEFAULT_FILTERS,
)

# 執行設定
from .settings import (
    LOG_LEVEL,
    RUN_CONFIG,
)

# 瀏覽器常數
from .browser import (
    USER_AGENTS,
    STEALTH_SCRIPT,
)

__all__ = [
    # constants
    'BASE_URL',
    'OUTPUT_BASE_DIR',
    'MANUAL_HANDLE_DIR',
    'SESSION_FILE',
    'CSV_FIELDNAMES',
    'DELAY',
    'DEFAULT_FILTERS',
    # settings
    'LOG_LEVEL',
    'RUN_CONFIG',
    # browser
    'USER_AGENTS',
    'STEALTH_SCRIPT',
]
