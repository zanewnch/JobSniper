"""
登入管理模組
"""

import os
from playwright.sync_api import sync_playwright
from config import BASE_URL, SESSION_FILE


class AuthManager:
    """Session 與登入管理"""

    def __init__(self, session_file: str = SESSION_FILE):
        self.session_file = session_file

    def has_session_file(self) -> bool:
        """檢查是否有 session 檔案"""
        return os.path.exists(self.session_file)

    def get_session_path(self) -> str | None:
        """取得 session 檔案路徑 (如果檔案存在)"""
        return self.session_file if self.has_session_file() else None

    def is_logged_in(self, verbose: bool = False) -> bool:
        """
        真正檢查 session 是否有效 (會開瀏覽器驗證)

        Args:
            verbose: 是否顯示檢查過程
        """
        if not self.has_session_file():
            return False

        if verbose:
            print("正在驗證登入狀態...")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(storage_state=self.session_file)
                page = context.new_page()

                page.goto("https://pda.104.com.tw/member", wait_until='domcontentloaded', timeout=10000)

                current_url = page.url
                is_valid = "login" not in current_url.lower()

                browser.close()

                if verbose:
                    if is_valid:
                        print("Session 有效")
                    else:
                        print("Session 已過期")

                return is_valid
        except Exception as e:
            if verbose:
                print(f"驗證失敗: {e}")
            return False

    def login_and_save(self) -> bool:
        """開啟瀏覽器讓使用者手動登入，登入後儲存 session"""
        print("\n=== 登入模式 ===")
        print("1. 瀏覽器會開啟 104 登入頁面")
        print("2. 請手動登入你的帳號")
        print("3. 登入成功後，關閉瀏覽器視窗")
        print("4. Session 會自動儲存")
        print()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                locale='zh-TW',
                timezone_id='Asia/Taipei',
            )
            page = context.new_page()

            login_url = "https://pda.104.com.tw/member/login"
            print(f"正在開啟登入頁面: {login_url}")
            page.goto(login_url)

            print("\n請在瀏覽器中登入你的 104 帳號...")
            print("登入成功後，請關閉瀏覽器視窗。\n")

            try:
                page.wait_for_event('close', timeout=0)
            except:
                pass

            os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
            context.storage_state(path=self.session_file)
            print(f"\n已儲存 session: {self.session_file}")

            browser.close()

        print("登入完成!")
        return True

    def clear_session(self) -> None:
        """清除已儲存的 session"""
        if os.path.exists(self.session_file):
            os.remove(self.session_file)
            print(f"已清除 session: {self.session_file}")
        else:
            print("沒有已儲存的 session")


# 全域實例 — 讓其他模組直接用
auth_manager = AuthManager()
