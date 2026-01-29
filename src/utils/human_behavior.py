"""
人類行為模擬工具
"""

import time
import random

from playwright.sync_api import Page


def random_delay(min_sec: float = 1, max_sec: float = 3) -> None:
    """隨機延遲，模擬人類行為"""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)


def smart_delay(human_like: str = 'normal', delay_multiplier: float = 1.0, level: str = 'normal') -> None:
    """
    根據 human_like 設定和 level 自動計算延遲

    Args:
        human_like: 人類行為模擬程度 ('minimal', 'normal', 'full')
        delay_multiplier: 延遲倍率
        level: 延遲等級 ('short', 'normal', 'long')
    """
    delay_table: dict[str, dict[str, tuple[float, float]]] = {
        'minimal': {'short': (0.5, 1), 'normal': (0.5, 1), 'long': (1, 2)},
        'normal': {'short': (0.5, 1), 'normal': (1, 2), 'long': (2, 4)},
        'full': {'short': (1, 2), 'normal': (2, 4), 'long': (4, 6)},
    }

    human_like = human_like if human_like in delay_table else 'normal'
    level = level if level in delay_table[human_like] else 'normal'
    min_sec, max_sec = delay_table[human_like][level]

    random_delay(min_sec * delay_multiplier, max_sec * delay_multiplier)


def human_like_scroll(page: Page) -> None:
    """模擬人類滾動行為"""
    scroll_times = random.randint(2, 4)
    for _ in range(scroll_times):
        scroll_distance = random.randint(200, 500)
        page.mouse.wheel(0, scroll_distance)
        random_delay(0.3, 0.8)


def human_like_mouse_move(page: Page) -> None:
    """模擬人類滑鼠移動"""
    try:
        x = random.randint(100, 800)
        y = random.randint(100, 600)
        page.mouse.move(x, y)
        random_delay(0.1, 0.3)
    except:
        pass


def human_like_pause(page: Page) -> None:
    """模擬人類閱讀停頓"""
    random_delay(1, 3)
    if random.random() > 0.5:
        page.mouse.wheel(0, random.randint(50, 150))
        random_delay(0.3, 0.5)


def human_like_long_break() -> None:
    """
    模擬人類長休息（降低 Cloudflare 檢測率）

    隨機決定是否休息，以及休息多久：
    - 70% 機率：短休息 2-5 秒
    - 20% 機率：中休息 5-10 秒
    - 10% 機率：長休息 10-20 秒（模擬看手機、喝水等）
    """
    roll = random.random()

    if roll < 0.7:
        delay = random.uniform(2, 5)
    elif roll < 0.9:
        delay = random.uniform(5, 10)
        print(f"    ☕ 休息 {delay:.1f} 秒...")
    else:
        delay = random.uniform(10, 20)
        print(f"    ☕ 長休息 {delay:.1f} 秒...")

    time.sleep(delay)
