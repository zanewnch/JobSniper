"""
瀏覽器設置
"""

import random
from playwright.sync_api import Playwright, Browser, BrowserContext
from .auth_manager import AuthManager, auth_manager
from config.browser import USER_AGENTS, STEALTH_SCRIPT


class StealthBrowser:
    """Stealth 瀏覽器管理"""

    def __init__(self, auth: AuthManager = auth_manager):
        self.auth: AuthManager = auth

    def setup(self, playwright: Playwright, headless: bool = False, use_session: bool = True) -> tuple[Browser, BrowserContext]:
        """
        建立 stealth 瀏覽器 + context

        Args:
            playwright: Playwright 實例
            headless: 是否隱藏瀏覽器視窗
            use_session: 是否載入已儲存的 session

        Returns:
            (browser, context)
        """
        browser = playwright.chromium.launch(
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-infobars',
                '--no-sandbox',
            ]
        )

        session_path = self.auth.get_session_path() if use_session else None

        context_options = {
            'viewport': {'width': 1920, 'height': 1080},
            'user_agent': random.choice(USER_AGENTS),
            'locale': 'zh-TW',
            'timezone_id': 'Asia/Taipei',
        }

        if session_path:
            context_options['storage_state'] = session_path
            print(f"已載入登入 session")

        context = browser.new_context(**context_options)
        context.add_init_script(STEALTH_SCRIPT)

        return browser, context


# 全域實例
stealth_browser = StealthBrowser()
