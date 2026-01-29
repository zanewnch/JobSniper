"""
策略上下文 - Strategy Pattern Context
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import BrowserContext, Page
    from .job_strategy import JobStrategy


class StrategyContext:
    """Strategy pattern Context — 持有策略與執行狀態，委派處理邏輯給策略"""

    def __init__(
        self,
        strategy: JobStrategy,
        config: dict[str, object],
        browser_context: BrowserContext | None = None,
        page: Page | None = None,
    ) -> None:
        self.strategy: JobStrategy = strategy
        self.config: dict[str, object] = config
        self.browser_context: BrowserContext | None = browser_context
        self.page: Page | None = page

    @property
    def human_like(self) -> str:
        return self.config.get('human_like', 'normal')

    @property
    def delay_multiplier(self) -> float:
        return self.config.get('delay_multiplier', 1.0)

    def before_process(self, jobs: list[dict[str, object]]) -> None:
        """委派處理前準備給策略"""
        self.strategy.before_process(jobs, self)

    def process_job(self, job: dict[str, object]) -> bool:
        """委派單一職缺處理給策略"""
        return self.strategy.process_job(job, self)

    def after_process(self, jobs: list[dict[str, object]]) -> None:
        """委派處理後收尾給策略"""
        self.strategy.after_process(jobs, self)
