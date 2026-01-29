"""
CAPTCHA 檢測與處理
"""

import time

from playwright.sync_api import Page
from .human_behavior import random_delay


# 常見 CAPTCHA 特徵 (可擴充)
CAPTCHA_INDICATORS: dict[str, list[str]] = {
    'iframe_src': [
        'recaptcha', 'hcaptcha', 'captcha', 'challenge',
        'turnstile', 'arkose', 'geetest',
    ],
    'selectors': [
        'iframe[src*="captcha"]',
        'iframe[src*="recaptcha"]',
        'iframe[src*="hcaptcha"]',
        'iframe[title*="reCAPTCHA"]',
        '.g-recaptcha',
        '.h-captcha',
        '#captcha',
        '[class*="captcha"]',
        '[id*="captcha"]',
        '#challenge-running',
        '#cf-challenge-running',
        '.cf-turnstile',
        '[class*="verify"]',
        '[class*="Verify"]',
    ],
    'text_content': [
        '請完成驗證',
        '我不是機器人',
        '請證明你是人類',
        'verify you are human',
        'are you a robot',
        'checking your browser',
        '正在檢查您的瀏覽器',
        '正在驗證您是否是人類',
        '檢閱您的連線安全性',
        '需要在繼續之前檢閱',
    ],
    'url_keywords': [
        '/challenge',
        '/captcha',
        '/verify',
    ],
}


def check_captcha(page: Page) -> dict[str, bool | str | None]:
    """
    檢測頁面是否有 CAPTCHA 驗證

    Returns:
        {'detected': bool, 'type': str | None, 'details': str | None}
    """
    result: dict[str, bool | str | None] = {'detected': False, 'type': None, 'details': None}

    try:
        current_url: str = page.url.lower()
        for keyword in CAPTCHA_INDICATORS['url_keywords']:
            if keyword in current_url:
                return {'detected': True, 'type': 'url', 'details': f'URL 包含: {keyword}'}

        for selector in CAPTCHA_INDICATORS['selectors']:
            try:
                if page.locator(selector).count() > 0:
                    return {'detected': True, 'type': 'selector', 'details': f'找到元素: {selector}'}
            except:
                pass

        try:
            page_text: str = page.locator('body').inner_text(timeout=2000).lower()
            for text in CAPTCHA_INDICATORS['text_content']:
                if text.lower() in page_text:
                    return {'detected': True, 'type': 'text', 'details': f'頁面包含文字: {text}'}
        except:
            pass

        try:
            iframes = page.locator('iframe').all()
            for iframe in iframes:
                src: str = iframe.get_attribute('src') or ''
                for keyword in CAPTCHA_INDICATORS['iframe_src']:
                    if keyword in src.lower():
                        return {'detected': True, 'type': 'iframe', 'details': f'iframe 包含: {keyword}'}
        except:
            pass

    except Exception:
        pass

    return result


def wait_for_human_verification(page: Page, timeout: int = 300) -> bool:
    """
    等待用戶手動完成 CAPTCHA 驗證

    Args:
        page: Playwright page
        timeout: 最長等待時間 (秒)

    Returns:
        是否成功 (驗證消失)
    """
    print("\n" + "=" * 60)
    print("⚠️  檢測到人機驗證!")
    print("=" * 60)
    print("請在瀏覽器中手動完成驗證...")
    print(f"等待中... (最多 {timeout} 秒)")
    print("=" * 60 + "\n")

    try:
        import winsound
        winsound.Beep(1000, 500)
    except:
        pass

    start_time: float = time.time()
    check_interval: int = 2

    while time.time() - start_time < timeout:
        captcha_status = check_captcha(page)
        if not captcha_status['detected']:
            print("\n✅ 驗證完成! 繼續執行...\n")
            random_delay(1, 2)
            return True

        time.sleep(check_interval)

    print("\n❌ 等待超時，請手動處理後重新執行")
    return False


def handle_captcha_if_detected(page: Page, action_name: str = "操作") -> bool:
    """
    檢測並處理 CAPTCHA (主要入口函數)

    Args:
        page: Playwright page
        action_name: 當前操作名稱 (用於 log)

    Returns:
        True=沒有驗證或已完成, False=驗證超時
    """
    captcha_status = check_captcha(page)

    if captcha_status['detected']:
        print(f"\n[{action_name}] 檢測到驗證: {captcha_status['details']}")
        return wait_for_human_verification(page)

    return True
