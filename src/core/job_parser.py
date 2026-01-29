"""
解析工具函式
"""

import re
import logging
from playwright.sync_api import Page, Locator

logger = logging.getLogger(__name__)


class JobParser:
    """職缺資料解析"""

    # 正則表達式（編譯一次重複使用）
    _RE_LOCATION: re.Pattern[str] = re.compile(r'^([\u4e00-\u9fa5]+[市縣][\u4e00-\u9fa5]*[區鄉鎮市]?)')
    _RE_EXPERIENCE: re.Pattern[str] = re.compile(r'(\d+年以上|經歷不拘)')
    _RE_EDUCATION: re.Pattern[str] = re.compile(r'(博士|碩士|大學|專科|高中職|高中|學歷不拘)')
    _RE_SALARY: re.Pattern[str] = re.compile(r'(待遇面議|月薪[\d,~]+元[以上]*|年薪[\d,~]+[萬元]+[以上]*|時薪[\d,~]+元[以上]*)')
    _INFO_KEYWORDS: tuple[str, ...] = ('年以上', '經歷不拘', '待遇面議', '月薪', '年薪')

    def parse_info(self, text: str) -> dict[str, str]:
        """
        解析混合的職缺資訊字串
        例如: "新竹市5年以上大學待遇面議" -> {location, experience, education, salary}
        """
        result = {
            'location': '',
            'experience': '',
            'education': '',
            'salary': ''
        }

        if not text:
            return result

        m = self._RE_LOCATION.match(text)
        if m:
            result['location'] = m.group(1)

        m = self._RE_EXPERIENCE.search(text)
        if m:
            result['experience'] = m.group(1)

        m = self._RE_EDUCATION.search(text)
        if m:
            result['education'] = m.group(1)

        m = self._RE_SALARY.search(text)
        if m:
            result['salary'] = m.group(1)

        return result

    def get_section_content(self, page: Page, heading_name: str) -> str:
        """找到 heading 後，取得該區塊的內容（使用父元素定位法）"""
        try:
            heading = page.get_by_role("heading", name=heading_name).first
            logger.debug(f"找 heading '{heading_name}': count={heading.count()}")
            if heading.count() > 0:
                # 方法1: 找父元素，然後取得整個區塊的文字（排除 heading 本身）
                parent = heading.locator("xpath=..")
                logger.debug(f"找 parent: count={parent.count()}")
                if parent.count() > 0:
                    parent_text = parent.inner_text().strip()
                    content = parent_text.replace(heading_name, '', 1).strip()
                    logger.debug(f"parent text 長度: {len(content)}")
                    if content:
                        return content

                # 方法2: 找祖父元素（heading 可能在更深的嵌套中）
                grandparent = heading.locator("xpath=../..")
                logger.debug(f"找 grandparent: count={grandparent.count()}")
                if grandparent.count() > 0:
                    gp_text = grandparent.inner_text().strip()
                    content = gp_text.replace(heading_name, '', 1).strip()
                    logger.debug(f"grandparent text 長度: {len(content)}")
                    if content:
                        return content

                # 方法3: 用 xpath 找下一個 div 或 p (更通用)
                next_content = heading.locator("xpath=following::div[1] | following::p[1]")
                logger.debug(f"找 following div/p: count={next_content.count()}")
                if next_content.count() > 0:
                    text = next_content.first.inner_text().strip()
                    logger.debug(f"following text 長度: {len(text)}")
                    return text
            else:
                logger.debug(f"找不到 heading '{heading_name}'")
        except Exception as e:
            logger.debug(f"get_section_content 錯誤: {e}")
        return ''

    def extract_from_card(self, card: Locator) -> dict[str, str] | None:
        """從職缺卡片提取基本資訊"""
        job = {
            'title': '',
            'url': '',
            'company': '',
            'location': '',
            'experience': '',
            'education': '',
            'salary': ''
        }

        title_link = card.get_by_role("link").first
        if title_link.count() > 0:
            job['title'] = title_link.inner_text().strip()
            href = title_link.get_attribute('href')
            job['url'] = f"https:{href}" if href and not href.startswith('http') else href

        company_links = card.get_by_role("link").all()
        if len(company_links) > 1:
            job['company'] = company_links[1].inner_text().strip()

        card_text = card.inner_text()
        lines = [line.strip() for line in card_text.split('\n') if line.strip()]

        for line in lines:
            if any(kw in line for kw in self._INFO_KEYWORDS):
                parsed = self.parse_info(line)
                job.update(parsed)
                break

        return job if job.get('title') else None


# 全域實例
job_parser = JobParser()
