"""
pywebview API Bridge — 前端 JS 透過 window.pywebview.api 呼叫這些方法
"""

from __future__ import annotations

import subprocess
import threading
from core import job_searcher, auth_manager
from config import RUN_CONFIG, SESSION_FILE, BASE_URL
from strategy import JobStrategy, SaveStrategy, ApplyStrategy
from ui.logger import get_logs


class Api:
    """暴露給 pywebview 前端的 Python API"""

    def __init__(self) -> None:
        self._running: bool = False
        self._thread: threading.Thread | None = None
        self._codegen_proc: subprocess.Popen | None = None

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

    # ── 開發工具 ──

    def open_codegen(self) -> dict[str, bool | str]:
        """啟動 Playwright Codegen，載入已儲存的 session"""
        if self._codegen_proc and self._codegen_proc.poll() is None:
            return {'success': False, 'error': 'Codegen 已在執行中'}
        try:
            cmd = ["python", "-m", "playwright", "codegen"]
            if auth_manager.has_session_file():
                cmd += [f"--load-storage={SESSION_FILE}"]
            cmd.append(BASE_URL)
            self._codegen_proc = subprocess.Popen(cmd)
            threading.Thread(
                target=self._wait_codegen,
                daemon=True,
            ).start()
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _wait_codegen(self) -> None:
        """等待 Codegen 結束，通知前端"""
        self._codegen_proc.wait()
        self._codegen_proc = None
        print("Codegen 已關閉")

    # ── 爬蟲 ──

    def start_scraper(self, keyword: str, pages: int, headless: bool, human_like: str, delay_multiplier: float, strategy_name: str, job_type: str = '全職', experience: list[str] | None = None) -> dict[str, bool | str]:
        """
        啟動爬蟲（在 background thread 執行）

        Args:
            keyword: 搜尋關鍵字
            pages: 要爬幾頁 (0 = 全部)
            headless: 是否隱藏瀏覽器
            human_like: 擬人化程度 (minimal / normal / full)
            delay_multiplier: 延遲倍率 (1.0 / 1.5 / 2.0)
            strategy_name: save / apply
            job_type: 工作性質 (全職 / 兼職 / all)
            experience: 經歷要求 (e.g. ["1年以下", "1-3年"])
        """
        if self._running:
            return {'success': False, 'error': '爬蟲正在執行中'}

        # 組合 config
        config = RUN_CONFIG.copy()
        config['pages'] = pages
        config['headless'] = headless
        config['human_like'] = human_like
        config['delay_multiplier'] = delay_multiplier
        config['job_type'] = job_type
        config['experience'] = experience or []

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
            job_type = config.get('job_type', '全職')
            print(f"工作性質: {'全部' if job_type == 'all' else job_type}")
            exp_list = config.get('experience', [])
            print(f"經歷: {', '.join(exp_list) if exp_list else '不限'}")

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
