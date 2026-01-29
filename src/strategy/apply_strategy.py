"""
應徵策略 - 自動投遞履歷

已處理的 Edge Cases:
    - 已應徵過 → 檢查「已應徵」「今日已應徵」文字，跳過
    - 找不到應徵按鈕 → 標記失敗
    - 必填項目未填 → 保留 tab 供手動檢查
    - 點擊應徵開新分頁 → 用 expect_popup() 捕捉
    - 公司有額外提問 → 無法自動填寫，保留 tab 供手動檢查

不需處理的 Edge Cases:
    - 職缺已下架/關閉: 已下架的職缺不會出現在搜尋結果
    - 每日應徵次數上限: 104 目前沒有此限制
    - 驗證碼/人機驗證: 目前沒遇過，有 stealth 模式應該夠用
    - 應徵按鈕文字變體: 目前只有「應徵」，沒有「立即應徵」等變體
    - 履歷未完成: 使用前請確認履歷已設定完成
    - 網路逾時/載入失敗: 由外層 try/except 捕捉
"""

from __future__ import annotations

import re
import os
import json
import time
import random
from typing import TYPE_CHECKING

from .job_strategy import JobStrategy
from config import MANUAL_HANDLE_DIR
from utils import random_delay, human_like_pause, handle_captcha_if_detected, human_like_long_break

if TYPE_CHECKING:
    from .strategy_context import StrategyContext


class ApplyStrategy(JobStrategy):
    """自動投遞履歷"""

    def __init__(self) -> None:
        self.applied_count: int = 0
        self.skipped_count: int = 0
        self.failed_count: int = 0
        self.pending_tabs: list[dict[str, object]] = []  # 保留未成功的 tabs 供檢查
        self.current_page: int = 1  # 當前頁碼
        self.page_manual_jobs: dict[int, list[dict[str, str]]] = {}  # {page_num: [{company, title}, ...]}

    @property
    def name(self) -> str:
        return "自動投履歷"

    @property
    def description(self) -> str:
        return "自動對搜尋到的職缺投遞履歷"

    def set_page(self, page_num: int) -> None:
        """設定當前頁碼"""
        self.current_page = page_num

    def _add_manual_job(self, company: str, title: str) -> None:
        """記錄需要手動處理的職缺"""
        if self.current_page not in self.page_manual_jobs:
            self.page_manual_jobs[self.current_page] = []
        self.page_manual_jobs[self.current_page].append({
            'company': company,
            'title': title
        })

    def export_page_manual_jobs(self, page_num: int | None = None) -> None:
        """
        匯出某頁需要手動處理的職缺到 JSON

        Args:
            page_num: 頁碼，None 則使用 current_page
        """
        page_num = page_num or self.current_page
        jobs = self.page_manual_jobs.get(page_num, [])

        if not jobs:
            return  # 沒有需要手動處理的職缺

        # 確保目錄存在
        os.makedirs(MANUAL_HANDLE_DIR, exist_ok=True)

        # 輸出檔案
        file_path = os.path.join(MANUAL_HANDLE_DIR, f"page_{page_num}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, ensure_ascii=False, indent=2)

        print(f"    📁 已匯出 {len(jobs)} 個待處理職缺: page_{page_num}.json")

    def before_process(self, jobs: list[dict[str, object]], context: StrategyContext) -> None:
        """處理前確認"""
        print(f"\n[ApplyStrategy] 準備投遞 {len(jobs)} 個職缺")
        print("注意: 請確認已登入且履歷已設定完成")

    def process_job(self, job: dict[str, object], context: StrategyContext) -> bool:
        """
        對單一職缺投遞履歷 (直接在列表頁點擊應徵按鈕)

        Args:
            job: 職缺資料 (包含 card, job_index, company, title)
            context: 策略上下文 (包含 browser_context, page, delay_multiplier)
        """
        job_index = job.get('job_index', 0)
        company = job.get('company', '')
        title = job.get('title', '')
        card = job.get('card')  # 職缺卡片 locator
        page = context.page
        browser_context = context.browser_context
        delay_multiplier = context.delay_multiplier

        try:
            # 先檢查是否已經應徵過
            already_applied = card.locator("div").filter(has_text=re.compile(r"^(近日已應徵|今日已應徵|已應徵)$")).first
            if already_applied.is_visible(timeout=1000):
                already_text = already_applied.inner_text().strip()
                print(f"    ⏭ 跳過 ({already_text})")
                self.skipped_count += 1
                return False

            # 找到卡片上的「應徵」按鈕
            apply_btn = card.locator("div").filter(has_text=re.compile(r"^應徵$")).nth(1)

            if not apply_btn.is_visible(timeout=2000):
                print(f"    ✗ 找不到應徵按鈕")
                self.failed_count += 1
                return False

            # 點擊應徵按鈕，會開新分頁
            with page.expect_popup() as popup_info:
                apply_btn.click()

            # 新分頁 (應徵確認頁面)
            apply_page = popup_info.value

            # 等待頁面載入 (Cloudflare 驗證可能需要幾秒)
            random_delay(3 * delay_multiplier, 5 * delay_multiplier)

            # CAPTCHA 檢測 (應徵頁面可能有 Cloudflare 驗證)
            if not handle_captcha_if_detected(apply_page, f"應徵 {company}"):
                apply_page.close()
                self.failed_count += 1
                return False

            # 點擊「確認送出」按鈕
            confirm_btn = apply_page.get_by_role("button", name=re.compile(r"確認送出"))

            if not confirm_btn.is_visible(timeout=5000):
                print(f"    ✗ 找不到確認送出按鈕")
                apply_page.close()
                self.failed_count += 1
                return False

            confirm_btn.click()
            random_delay(2 * delay_multiplier, 3 * delay_multiplier)

            # 等待「應徵成功」文字出現
            success_text = apply_page.get_by_text("應徵成功")

            if success_text.is_visible(timeout=10000):
                print(f"    ✓ 應徵成功")
                self.applied_count += 1
                apply_page.close()

                # 應徵成功後隨機休息（降低 Cloudflare 檢測率）
                human_like_long_break()

                # 每投遞 5 個，長休息 30-60 秒
                if self.applied_count % 5 == 0:
                    break_time = random.uniform(30, 60)
                    print(f"\n    🎯 已投遞 {self.applied_count} 個，休息 {break_time:.0f} 秒...\n")
                    time.sleep(break_time)
            else:
                # ==================================================
                # 沒看到「應徵成功」，可能的原因：
                # 1. 公司設定了額外提問（如：是否有兩年以上專案管理經驗？）
                #    這些提問是必填的，需要手動填寫後才能送出
                #    例如：蜘蛛網路股份有限公司 - 專案經理 Project Manager
                #    https://www.104.com.tw/job/7xpf9?apply=form&jobsource=cs_sub_custlist_rc
                # 2. 其他必填項目未填（如：選擇履歷版本）
                #
                # 處理方式：保留 tab 不關閉，讓使用者手動處理
                # ==================================================
                print(f"    ⚠ 未看到應徵成功，保留 tab 供檢查")
                self._add_manual_job(company, title)  # 記錄待手動處理
                self.pending_tabs.append({
                    'company': company,
                    'title': title,
                    'apply_page': apply_page,
                })
                self.failed_count += 1

            return True

        except Exception as e:
            print(f"    ✗ 投遞失敗: {e}")
            self.failed_count += 1
            return False

    def after_process(self, jobs: list[dict[str, object]], context: StrategyContext) -> None:
        """處理完成統計"""
        print(f"\n[ApplyStrategy] 完成!")
        print(f"  成功投遞: {self.applied_count}")
        print(f"  跳過 (已應徵): {self.skipped_count}")
        print(f"  失敗/待檢查: {self.failed_count}")
        print(f"  總計: {len(jobs)}")

        if self.pending_tabs:
            print(f"\n⚠ 有 {len(self.pending_tabs)} 個 tab 保留中，請手動檢查:")
            for i, tab in enumerate(self.pending_tabs, 1):
                print(f"  {i}. {tab['company']} - {tab['title']}")
            print("\n檢查完畢後，請手動關閉這些 tab。")
            print("瀏覽器將保持開啟狀態。")
            input("\n按 Enter 結束程式...")
