"""
自動環境設定 - 確保 Playwright 瀏覽器可用

首次執行時會自動下載 Chromium 到程式旁的 browsers/ 目錄
"""

import os
import sys
import subprocess


def get_app_dir() -> str:
    """取得程式所在目錄 (支援 .py 和 PyInstaller .exe)"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def ensure_browser() -> None:
    """確保 Playwright Chromium 瀏覽器已安裝"""
    app_dir: str = get_app_dir()
    browsers_dir: str = os.path.join(app_dir, 'browsers')

    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = browsers_dir

    if os.path.exists(browsers_dir):
        for name in os.listdir(browsers_dir):
            if name.startswith('chromium-'):
                chromium_dir: str = os.path.join(browsers_dir, name)
                marker: str = os.path.join(chromium_dir, 'INSTALLATION_COMPLETE')
                if os.path.exists(marker):
                    return

    print("=" * 50)
    print("  首次執行，需要下載瀏覽器 (~150MB)")
    print(f"  下載位置: {browsers_dir}")
    print("=" * 50)
    print()

    try:
        process: subprocess.Popen[bytes] = subprocess.Popen(
            [sys.executable, '-m', 'playwright', 'install', 'chromium'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        for line in process.stdout:  # type: ignore[union-attr]
            print(f"  {line.decode('utf-8', errors='replace').rstrip()}")
        process.wait()

        if process.returncode != 0:
            print(f"\n瀏覽器下載失敗 (exit code: {process.returncode})")
            print("請手動執行: playwright install chromium")
            input("\n按 Enter 結束...")
            sys.exit(1)

        print()
        print("=" * 50)
        print("  瀏覽器下載完成!")
        print("=" * 50)
        print()

    except FileNotFoundError:
        print("\n找不到 playwright，請確認已安裝: pip install playwright")
        input("\n按 Enter 結束...")
        sys.exit(1)
