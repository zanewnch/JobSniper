"""
詳細頁面抓取
"""

import re
import logging
from playwright.sync_api import Page
from utils import human_like_scroll, random_delay
from .job_parser import job_parser

logger = logging.getLogger(__name__)


class DetailScraper:
    """職缺詳細頁面抓取"""

    FIELDS: list[tuple[str, str]] = [
        ('detailed_job_description', '工作內容'),
        ('detailed_address', '上班地點'),
        ('detailed_work_hours', '上班時段'),
        ('detailed_company_benefits', '福利制度'),
    ]

    def scrape(self, detail_page: Page) -> dict[str, str]:
        """從詳細頁面抓取資訊"""
        logger.debug("開始抓取詳細頁面")
        detail = {key: '' for key, _ in self.FIELDS}
        detail['detailed_company_photos'] = ''

        try:
            logger.debug("正在 scroll 頁面")
            human_like_scroll(detail_page)
            random_delay(1, 2)
            logger.debug("scroll 完成")

            for key, heading in self.FIELDS:
                logger.debug(f"抓取{heading}")
                detail[key] = job_parser.get_section_content(detail_page, heading)
                logger.debug(f"{heading}: {detail[key][:50] if detail[key] else '(空)'}")

            # 公司環境照片（結構不同，單獨處理）
            logger.debug("抓取公司環境照片")
            try:
                photos = detail_page.get_by_role("heading", name=re.compile(r"公司環境照片")).first
                if photos.count() > 0:
                    detail['detailed_company_photos'] = photos.inner_text().strip()
                    logger.debug(f"公司環境照片: {detail['detailed_company_photos']}")
                else:
                    logger.debug("公司環境照片: (找不到)")
            except Exception as e:
                logger.debug(f"公司環境照片抓取失敗: {e}")

        except Exception as e:
            logger.error(f"抓取詳細資訊時發生錯誤: {e}")

        logger.debug("詳細頁面抓取完成")
        return detail


# 全域實例
detail_scraper = DetailScraper()
