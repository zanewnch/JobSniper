"""
pywebview API Bridge — 前端 JS 透過 window.pywebview.api 呼叫這些方法
"""

from __future__ import annotations

import threading
from core import job_searcher, auth_manager
from config import RUN_CONFIG
from strategy import JobStrategy, SaveStrategy, ApplyStrategy
from ui.logger import get_logs


class Api:
    """暴露給 pywebview 前端的 Python API"""

    def __init__(self) -> None:
        self._running: bool = False
        self._thread: threading.Thread | None = None

    # ── 狀態 ──

    def get_status(self) -> dict[str, bool]:
        """取得目前登入狀態"""
        return {
            'has_session': auth_manager.has_session_file(),
            'is_running': self._running,
        }

    def check_login(self) -> dict[str, bool]:
        """真正驗證 session 是否有效（會開隱藏瀏覽器）"""
        valid = auth_manager.is_logged_in(verbose=True)
        return {'valid': valid}

    # ── 登入/登出 ──

    def login(self) -> dict[str, bool | str]:
        """開啟瀏覽器讓使用者手動登入"""
        try:
            auth_manager.login_and_save()
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def logout(self) -> dict[str, bool]:
        """清除 session"""
        auth_manager.clear_session()
        return {'success': True}

    # ── 爬蟲 ──

    def start_scraper(self, keyword: str, pages: int, headless: bool, human_like: str, delay_multiplier: float, strategy_name: str) -> dict[str, bool | str]:
        """
        啟動爬蟲（在 background thread 執行）

        Args:
            keyword: 搜尋關鍵字
            pages: 要爬幾頁 (0 = 全部)
            headless: 是否隱藏瀏覽器
            human_like: 擬人化程度 (minimal / normal / full)
            delay_multiplier: 延遲倍率 (1.0 / 1.5 / 2.0)
            strategy_name: save / apply
        """
        if self._running:
            return {'success': False, 'error': '爬蟲正在執行中'}

        # 組合 config
        config = RUN_CONFIG.copy()
        config['pages'] = pages
        config['headless'] = headless
        config['human_like'] = human_like
        config['delay_multiplier'] = delay_multiplier

        # 選策略
        strategy = ApplyStrategy() if strategy_name == 'apply' else SaveStrategy()

        # 在背景執行
        self._running = True
        self._thread = threading.Thread(
            target=self._run_scraper,
            args=(keyword, config, strategy),
            daemon=True,
        )
        self._thread.start()

        return {'success': True}

    def _run_scraper(self, keyword: str, config: dict[str, object], strategy: JobStrategy) -> None:
        """背景執行爬蟲"""
        try:
            print(f"\n=== 開始執行 ===")
            print(f"關鍵字: {keyword}")
            print(f"策略: {strategy.name}")
            print(f"頁數: {config['pages'] if config['pages'] > 0 else '全部'}")
            print(f"瀏覽器: {'隱藏' if config['headless'] else '顯示'}")
            print(f"人類行為: {config['human_like']}")
            print(f"延遲倍率: {config['delay_multiplier']}x")

            jobs = job_searcher.search(
                keyword,
                pages=config['pages'],
                headless=config['headless'],
                config=config,
                strategy=strategy,
            )

            if jobs:
                print(f"\n=== 完成 ===")
                print(f"總共處理 {len(jobs)} 個職缺")
            else:
                print("沒有找到任何職缺")

        except Exception as e:
            print(f"\n=== 錯誤 ===")
            print(f"{e}")
        finally:
            self._running = False

    # ── Logs ──

    def poll_logs(self) -> list[str]:
        """前端 poll 新的 log 訊息"""
        return get_logs()
