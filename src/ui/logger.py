"""
Log 捕捉系統 — 攔截 print() 輸出，緩衝給前端 poll
"""

import sys
import io
import threading


class LogCapture(io.TextIOBase):
    """攔截 stdout，將訊息存入 buffer 供前端讀取"""

    def __init__(self) -> None:
        self._buffer: list[str] = []
        self._lock: threading.Lock = threading.Lock()

    def write(self, text: str) -> int:
        if text and text.strip():
            with self._lock:
                self._buffer.append(text.rstrip('\n'))
        return len(text)

    def flush(self) -> None:
        pass

    def get_new_logs(self) -> list[str]:
        """取出所有新 log，清空 buffer"""
        with self._lock:
            logs = self._buffer.copy()
            self._buffer.clear()
        return logs


# 全域 logger 實例
log_capture = LogCapture()


def install() -> None:
    """安裝 log 攔截（取代 sys.stdout）"""
    sys.stdout = log_capture


def get_logs() -> list[str]:
    """取得新 log"""
    return log_capture.get_new_logs()
