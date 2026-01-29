"""
工具函式模組

匯出所有工具函式，保持向後兼容：
    from utils import random_delay, save_jobs, handle_captcha_if_detected
"""

# 人類行為模擬
from .human_behavior import (
    random_delay,
    smart_delay,
    human_like_scroll,
    human_like_mouse_move,
    human_like_pause,
    human_like_long_break,
)

# CAPTCHA 檢測與處理
from .captcha import (
    CAPTCHA_INDICATORS,
    check_captcha,
    wait_for_human_verification,
    handle_captcha_if_detected,
)

# 檔案存取
from .file_io import (
    get_next_file_number,
    save_jobs,
    load_jobs,
    update_job,
)

# 環境設定
from .setup import ensure_browser

__all__ = [
    # human_behavior
    'random_delay',
    'smart_delay',
    'human_like_scroll',
    'human_like_mouse_move',
    'human_like_pause',
    'human_like_long_break',
    # captcha
    'CAPTCHA_INDICATORS',
    'check_captcha',
    'wait_for_human_verification',
    'handle_captcha_if_detected',
    # file_io
    'get_next_file_number',
    'save_jobs',
    'load_jobs',
    'update_job',
    # setup
    'ensure_browser',
]
