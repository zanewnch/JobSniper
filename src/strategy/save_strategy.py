"""
儲存策略 - 將職缺資料儲存到檔案
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .job_strategy import JobStrategy
from utils import save_jobs, smart_delay, human_like_pause
from core.detail_scraper import detail_scraper

if TYPE_CHECKING:
    from .strategy_context import StrategyContext


class SaveStrategy(JobStrategy):
    """儲存職缺資料到 CSV/JSON 檔案"""

    def __init__(self) -> None:
        self.filename: str | None = None
        self.job_count: int = 0
        self._jobs_buffer: list[dict[str, object]] = []  # 暫存職缺資料

    @property
    def name(self) -> str:
        return "儲存職缺"

    @property
    def description(self) -> str:
        return "將職缺資料儲存到 CSV 和 JSON 檔案"

    def before_process(self, jobs: list[dict[str, object]], context: StrategyContext) -> None:
        """處理前準備"""
        print(f"\n[SaveStrategy] 準備開始收集職缺資料")

    def process_job(self, job: dict[str, object], context: StrategyContext) -> bool:
        """
        抓取詳細資料並更新到 job dict

        Args:
            job: 職缺資料 (包含 url, job_index)
            context: 策略上下文 (包含 browser_context, human_like, delay_multiplier)
        """
        job_index = job.get('job_index', 0)
        url = job.get('url')
        company = job.get('company', '')
        browser_context = context.browser_context
        human_like = context.human_like
        delay_multiplier = context.delay_multiplier

        self.job_count += 1
        print(f"\n[Detail {self.job_count}] {company}")

        try:
            # 開啟詳細頁面
            detail_page = browser_context.new_page()
            detail_page.goto(url, wait_until='domcontentloaded')

            # 根據 human_like 設定延遲
            smart_delay(human_like, delay_multiplier, 'normal')

            # 抓取詳細資訊
            detail = detail_scraper.scrape(detail_page)

            if human_like == 'full':
                human_like_pause(detail_page)

            detail_page.close()

            if detail:
                # 直接更新 job dict（會在 after_process 時一起儲存）
                job.update(detail)
                print(f"  ✓ 已抓取詳細資料")
                return True
            else:
                print(f"  ✗ 抓取失敗")
                return False

        except Exception as e:
            print(f"  ✗ 錯誤: {e}")
            return False

    def after_process(self, jobs: list[dict[str, object]], context: StrategyContext) -> None:
        """處理完成，儲存所有資料"""
        if jobs:
            save_result = save_jobs(jobs)
            self.filename = save_result['filename']
            print(f"\n[SaveStrategy] 完成! 已儲存 {len(jobs)} 個職缺")
            print(f"  檔案: {self.filename}")
        else:
            print(f"\n[SaveStrategy] 完成! 沒有職缺資料需要儲存")
