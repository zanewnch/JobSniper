"""
檔案存取工具
"""

import os
import json
import csv

from config import OUTPUT_BASE_DIR, CSV_FIELDNAMES


def get_next_file_number(directory: str, prefix: str = "") -> int:
    """取得下一個可用的檔案編號"""
    if not os.path.exists(directory):
        return 1

    existing_files: list[str] = os.listdir(directory)
    numbers: list[int] = []
    for f in existing_files:
        name: str = os.path.splitext(f)[0]
        if prefix:
            if name.startswith(f"{prefix}_"):
                num_part = name[len(prefix) + 1:]
                if num_part.isdigit():
                    numbers.append(int(num_part))
        else:
            if name.isdigit():
                numbers.append(int(name))

    return max(numbers) + 1 if numbers else 1


def save_jobs(jobs: list[dict], prefix: str = "jobs", base_dir: str | None = None) -> dict[str, str]:
    """
    儲存職缺到 CSV 和 JSON 檔案

    Args:
        jobs: 職缺列表
        prefix: 檔名前綴
        base_dir: 輸出基礎目錄 (預設使用 config 設定)

    Returns:
        包含 filename, json_path, csv_path
    """
    base_dir = base_dir or OUTPUT_BASE_DIR
    csv_dir: str = os.path.join(base_dir, "csv")
    json_dir: str = os.path.join(base_dir, "json")

    os.makedirs(csv_dir, exist_ok=True)
    os.makedirs(json_dir, exist_ok=True)

    file_number: int = get_next_file_number(json_dir, prefix=prefix)
    filename: str = f"{prefix}_{file_number}"

    json_path: str = os.path.join(json_dir, f"{filename}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    print(f"已儲存 JSON: {json_path}")

    csv_path: str = os.path.join(csv_dir, f"{filename}.csv")
    if jobs:
        with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(jobs)
    print(f"已儲存 CSV: {csv_path}")

    print(f"總共儲存 {len(jobs)} 個職缺 (檔案: {filename})")

    return {
        'filename': filename,
        'json_path': json_path,
        'csv_path': csv_path,
    }


def load_jobs(filename: str, base_dir: str | None = None) -> list[dict]:
    """載入已存的職缺資料"""
    base_dir = base_dir or OUTPUT_BASE_DIR
    json_path: str = os.path.join(base_dir, "json", f"{filename}.json")

    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def update_job(filename: str, job_index: int, detail: dict, base_dir: str | None = None) -> bool:
    """
    更新單一職缺的詳細資訊

    Args:
        filename: 檔案名稱 (如 test_1, complete_1)
        job_index: 職缺在 list 中的 index
        detail: 要更新的詳細資訊
        base_dir: 輸出基礎目錄
    """
    base_dir = base_dir or OUTPUT_BASE_DIR
    json_path: str = os.path.join(base_dir, "json", f"{filename}.json")
    csv_path: str = os.path.join(base_dir, "csv", f"{filename}.csv")

    jobs: list[dict] = load_jobs(filename, base_dir)
    if not jobs or job_index >= len(jobs):
        return False

    jobs[job_index].update(detail)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)

    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(jobs)

    return True
