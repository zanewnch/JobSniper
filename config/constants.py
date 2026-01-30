"""
固定常數
"""

import os
import sys

# 網站設定
BASE_URL: str = "https://www.104.com.tw/"


# 輸出路徑
def _get_app_dir() -> str:
    """取得程式所在目錄（支援 .py 與 PyInstaller .exe）"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


OUTPUT_BASE_DIR: str = os.path.join(_get_app_dir(), "output")
MANUAL_HANDLE_DIR: str = os.path.join(OUTPUT_BASE_DIR, "manual_handle")
SESSION_FILE: str = os.path.join(OUTPUT_BASE_DIR, "session.json")

# CSV 欄位順序
CSV_FIELDNAMES: list[str] = [
    'title', 'url', 'company', 'location', 'experience', 'education', 'salary',
    'detailed_job_description', 'detailed_address', 'detailed_work_hours',
    'detailed_company_benefits', 'detailed_company_photos'
]

# 延遲設定 (秒)
DELAY: dict[str, tuple[float, float]] = {
    "short": (0.3, 0.8),
    "medium": (0.5, 1),
    "long": (1, 2),
    "page_load": (2, 3)
}

# 搜尋篩選條件
DEFAULT_FILTERS: dict[str, str | list[str] | list[int]] = {
    # 地區 (nth-child index，會先選第一個二級分類)
    "area_indices": [3],  # 第 3 個子區域

    # 職務類別
    "job_category": "行銷／企劃／專案管理類",  # 大類名稱
    "job_category_indices": [5],  # 要勾選的職務位置 (可多選, nth-child index)

    # 工作要求
    "experience": ["1年以下", "1-3年"],
    "job_type": "全職",
    "update_time": "一個月內"
}
