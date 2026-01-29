"""
策略基類
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .strategy_context import StrategyContext


class JobStrategy(ABC):
    """職缺處理策略的抽象基類"""

    @property
    @abstractmethod
    def name(self) -> str:
        """策略名稱"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """策略描述"""
        pass

    @abstractmethod
    def process_job(self, job: dict[str, object], context: StrategyContext) -> bool:
        """
        處理單一職缺

        Args:
            job: 職缺資料
            context: 策略上下文 (包含 page, browser_context, config 等)

        Returns:
            是否成功處理
        """
        pass

    def before_process(self, jobs: list[dict[str, object]], context: StrategyContext) -> None:
        """處理前的準備工作 (可選覆寫)"""
        pass

    def after_process(self, jobs: list[dict[str, object]], context: StrategyContext) -> None:
        """處理後的收尾工作 (可選覆寫)"""
        pass
