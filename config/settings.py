"""
可調整的執行設定
"""

import logging

# Logging 設定
LOG_LEVEL: int = logging.WARNING  # 改成 logging.DEBUG 可看詳細訊息
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(levelname)s - %(name)s - %(message)s'
)

# ==================================================
# 執行參數 (Control Panel)
# ==================================================
RUN_CONFIG: dict[str, int | bool | str | float] = {
    "pages": 1,              # 要爬幾頁 (0 = 全部)
    "headless": False,       # True=隱藏瀏覽器, False=顯示
    "human_like": "full",     # "minimal"=最少, "normal"=普通, "full"=完整
    "delay_multiplier": 2.0,  # 延遲倍率 (1.0=正常, 2.0=兩倍慢)
}

