"""
JobSniper — 104 人力銀行自動化工具
"""

import sys
import os

# 確保 src/ 在 import path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 確保 Playwright 瀏覽器已安裝 (必須在 import playwright 之前)
from utils import ensure_browser
ensure_browser()

# 安裝 log 攔截 (攔截 print → buffer，供前端 poll)
from ui.logger import install as install_logger
install_logger()

import webview
from ui.api import Api


def main() -> None:
    html_path: str = os.path.join(os.path.dirname(__file__), 'src', 'ui', 'index.html')
    api: Api = Api()
    webview.create_window(
        'JobSniper',
        url=html_path,
        js_api=api,
        width=800,
        height=620,
        min_size=(600, 400),
    )
    webview.start()


if __name__ == '__main__':
    main()
