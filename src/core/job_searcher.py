"""
104 搜尋列表頁面邏輯
"""

import re
from playwright.sync_api import sync_playwright, Page
from .stealth_browser import stealth_browser
from .job_parser import JobParser, job_parser
from config import BASE_URL, DEFAULT_FILTERS
from utils import (
    random_delay, smart_delay, human_like_scroll, human_like_mouse_move,
    human_like_pause, handle_captcha_if_detected
)


class JobSearcher:
    """104 職缺搜尋與處理"""

    def __init__(self) -> None:
        self.parser: JobParser = job_parser

    def search(self, keyword: str, pages: int = 1, headless: bool = False, config: dict | None = None, strategy: object | None = None) -> list[dict]:
        """
        爬取 104 職缺列表 (兩階段流程)

        Phase 1: 抓取列表頁基本資料
        Phase 2: 用 Strategy 處理每個職缺
        """
        if config is None:
            from config import RUN_CONFIG
            config = RUN_CONFIG

        if strategy is None:
            from strategy import SaveStrategy
            strategy = SaveStrategy()

        print(f"\n使用策略: {strategy.name}")
        print(f"說明: {strategy.description}")

        with sync_playwright() as p:
            browser, browser_ctx = stealth_browser.setup(p, headless=headless)
            page = browser_ctx.new_page()

            from strategy import StrategyContext
            ctx = StrategyContext(strategy, config, browser_context=browser_ctx, page=page)

            # 前往首頁
            print("\n正在前往 104 首頁...")
            page.goto(BASE_URL, wait_until='domcontentloaded')
            random_delay(2, 3)

            if not handle_captcha_if_detected(page, "進入首頁"):
                browser.close()
                return []

            self._close_popups(page)
            self._search_keyword(page, keyword)
            self._apply_filters(page)

            if not handle_captcha_if_detected(page, "套用篩選"):
                browser.close()
                return []

            # ========== 開始處理 ==========
            print(f"\n{'='*60}")
            print(f"開始: {strategy.name}")
            print(f"{'='*60}")

            jobs = []
            page_num = 1

            ctx.before_process(jobs)
            max_pages = pages if pages > 0 else 999

            while page_num <= max_pages:
                print(f"\n[Page {page_num}] 正在抓取列表...")

                if hasattr(ctx.strategy, 'set_page'):
                    ctx.strategy.set_page(page_num)

                if not handle_captcha_if_detected(page, f"第 {page_num} 頁"):
                    break

                human_like_scroll(page)
                if ctx.human_like in ['normal', 'full']:
                    human_like_mouse_move(page)
                    smart_delay(ctx.human_like, ctx.delay_multiplier, 'normal')

                job_cards = page.locator('.vue-recycle-scroller__item-view .job-summary').all()
                print(f"[Page {page_num}] 找到 {len(job_cards)} 個職缺卡片")

                for i, card in enumerate(job_cards):
                    try:
                        job = self.parser.extract_from_card(card)
                        if not job:
                            continue

                        company = job.get('company', '')
                        print(f"  [Page {page_num}][{i+1}] {job.get('title', '')[:30]}  |  {company}")

                        job_index = len(jobs)
                        jobs.append(job)

                        job_info = {
                            **job,
                            'job_index': job_index,
                            'card': card,
                        }
                        ctx.process_job(job_info)

                        if not handle_captcha_if_detected(page, f"處理職缺 {i+1}"):
                            break

                        smart_delay(ctx.human_like, ctx.delay_multiplier, 'normal')

                    except Exception as e:
                        print(f"  [Page {page_num}][{i+1}] 錯誤: {e}")
                        continue

                print(f"[Page {page_num}] 處理完成: {len(job_cards)} 個職缺")

                if hasattr(ctx.strategy, 'export_page_manual_jobs'):
                    ctx.strategy.export_page_manual_jobs(page_num)

                if len(job_cards) == 0:
                    print(f"\n[Page {page_num}] 沒有找到任何職缺卡片，結束搜尋")
                    break

                if page_num < max_pages:
                    if ctx.human_like == 'full':
                        human_like_pause(page)

                    has_next = self._goto_next_page(page, page_num + 1)
                    if not has_next:
                        print(f"\n[Page {page_num}] 已到達最後一頁，結束搜尋")
                        break

                    page_num += 1
                else:
                    print(f"\n[Page {page_num}] 已達到設定頁數上限，結束搜尋")
                    break

            print(f"\n{'='*60}")
            print(f"完成! 共處理 {len(jobs)} 個職缺")
            print(f"{'='*60}")

            ctx.after_process(jobs)
            browser.close()

        return jobs

    # ── Private ──

    def _close_popups(self, page: Page) -> None:
        """關閉各種彈窗"""
        try:
            cancel_btn = page.get_by_role("button", name="Cancel")
            if cancel_btn.is_visible(timeout=2000):
                cancel_btn.click()
                print("已關閉 Cancel 彈窗")
                random_delay(0.5, 1)
        except:
            pass

        try:
            later_btn = page.get_by_role("button", name="下次再說")
            if later_btn.is_visible(timeout=2000):
                later_btn.click()
                print("已關閉 '下次再說' 彈窗")
                random_delay(0.5, 1)
        except:
            pass

    def _search_keyword(self, page: Page, keyword: str) -> None:
        """輸入搜尋關鍵字 (只輸入，不點搜尋)"""
        print(f"輸入關鍵字: {keyword}")
        search_box = page.get_by_role("textbox", name="關鍵字(例：工作職稱、公司名、技能專長...)")
        search_box.click()
        random_delay(0.3, 0.5)
        search_box.fill(keyword)
        random_delay(0.5, 1)

        self._close_popups(page)

    def _apply_filters(self, page: Page) -> None:
        """套用篩選條件"""
        filters = DEFAULT_FILTERS

        try:
            # ========== 地區 ==========
            area_indices = filters.get("area_indices", [])
            if area_indices:
                print(f"設定地區 (indices: {area_indices})")
                page.get_by_role("button", name="地區 ").click()
                random_delay(0.5, 1)

                page.locator(".category-item.category-item--level-two > .category-picker-checkbox > .category-picker-checkbox-input > .checkbox-input").first.check()
                random_delay(0.2, 0.4)
                print(f"  ✓ 選擇一級地區")

                for idx in area_indices:
                    selector = f".second-floor-rect > li:nth-child({idx}) > .category-picker-checkbox > .category-picker-checkbox-input > .checkbox-input"
                    page.locator(selector).check()
                    random_delay(0.2, 0.4)
                    print(f"  ✓ 勾選第 {idx} 個區域")

                random_delay(1, 1.5)

                page.locator("button.category-picker-btn-primary").click()
                random_delay(1.5, 2.5)
                print("  ✓ 地區選擇完成")

            # ========== 職務類別 ==========
            job_category = filters.get("job_category", "")
            if job_category:
                print(f"設定職務類別: {job_category}")
                page.get_by_role("button", name="職務類別 ").click()
                random_delay(0.5, 1)

                page.locator("a").filter(has_text=job_category).click()
                random_delay(0.3, 0.5)
                print(f"  ✓ 選擇大類: {job_category}")

                job_indices = filters.get("job_category_indices", [])
                for idx in job_indices:
                    selector = f".second-floor-rect > li:nth-child({idx}) > .category-picker-checkbox > .category-picker-checkbox-input > .checkbox-input"
                    page.locator(selector).check()
                    random_delay(0.2, 0.4)
                    print(f"  ✓ 勾選第 {idx} 個職務")

                random_delay(1, 1.5)

                page.locator("button.category-picker-btn-primary").click()
                random_delay(1.5, 2.5)
                print("  ✓ 職務類別選擇完成")

            # ========== 搜尋 ==========
            page.get_by_role("button", name="搜尋").click()
            page.wait_for_load_state('domcontentloaded')
            random_delay(2, 3)

            # ========== 更多篩選條件 ==========
            page.get_by_role("button", name=" 所有篩選條件").click()
            random_delay(0.5, 1)

            page.get_by_role("button", name="薪資待遇").nth(1).click()
            random_delay(0.3, 0.5)
            page.get_by_role("button", name="40,000 以上", exact=True).click()
            random_delay(0.3, 0.5)
            print(f"  ✓ 薪資: 40,000 以上")

            page.get_by_role("button", name="工作要求").click()
            random_delay(0.3, 0.5)

            for exp in filters.get("experience", []):
                try:
                    page.get_by_role("button", name=exp).click()
                    random_delay(0.2, 0.4)
                    print(f"  ✓ 經歷: {exp}")
                except:
                    pass

            job_type = filters.get("job_type", "全職")
            page.get_by_text(job_type).click()
            random_delay(0.3, 0.5)
            print(f"  ✓ 工作性質: {job_type}")

            update_time = filters.get("update_time", "一個月內")
            page.get_by_role("button", name=update_time).click()
            random_delay(0.3, 0.5)
            print(f"  ✓ 更新時間: {update_time}")

            page.get_by_role("button", name=re.compile(r"搜出好工作")).click()
            page.wait_for_load_state('domcontentloaded')
            random_delay(2, 3)

            print("篩選條件套用完成!")

        except Exception as e:
            print(f"套用篩選條件時發生錯誤: {e}")

    def _goto_next_page(self, page: Page, next_page_num: int) -> bool:
        """前往下一頁，回傳是否成功"""
        try:
            page_btn = page.get_by_role("link", name=str(next_page_num), exact=True).first
            if page_btn.is_visible():
                page_btn.scroll_into_view_if_needed()
                random_delay(0.5, 1)
                page_btn.click()
                page.wait_for_load_state('domcontentloaded')
                random_delay(2, 3)

                if not handle_captcha_if_detected(page, f"翻到第 {next_page_num} 頁"):
                    return False

                print(f"[Page {next_page_num}] 成功前往第 {next_page_num} 頁")
                return True
            else:
                return False
        except Exception as e:
            print(f"翻頁失敗: {e}")
            return False


# 全域實例
job_searcher = JobSearcher()
