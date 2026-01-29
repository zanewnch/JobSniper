# 104 人力銀行爬蟲 - 技術規格書

## 專案概述

這是一個使用 Playwright 自動化爬取 104 人力銀行職缺資訊的 Python 爬蟲程式。

## 技術棧

- **語言**: Python 3.x
- **自動化工具**: Playwright
- **資料處理**: Pandas
- **輸出格式**: CSV, JSON

## 專案結構

```
104/
├── main.py              # 主程式入口
├── config/              # 設定模組
│   ├── __init__.py      # 匯出所有設定
│   ├── constants.py     # 固定常數 (URL, PATHS, FIELDNAMES)
│   └── settings.py      # 執行設定 (RUN_CONFIG, MODE_PRESETS)
├── utils/               # 工具函式模組
│   ├── __init__.py      # 匯出所有工具
│   ├── captcha.py       # CAPTCHA 檢測與處理
│   ├── human_behavior.py # 人類行為模擬
│   └── file_io.py       # 檔案存取
├── scraper/             # 爬蟲模組
│   ├── __init__.py      # 模組導出
│   ├── auth.py          # 登入管理
│   ├── browser.py       # 瀏覽器設置
│   ├── search.py        # 搜尋列表頁邏輯
│   ├── parser.py        # 解析工具
│   └── detail.py        # 詳細頁面抓取
├── strategy/            # 策略模式模組
│   ├── __init__.py      # 模組導出
│   ├── base.py          # 策略基類 (JobStrategy)
│   ├── save_strategy.py # 儲存策略
│   └── apply_strategy.py # 應徵策略
├── output/              # 輸出資料夾
│   ├── csv/             # CSV 檔案
│   ├── json/            # JSON 檔案
│   ├── manual_handle/   # 待手動處理的職缺
│   └── session.json     # 登入 session (自動產生)
└── requirements.txt     # 依賴套件
```

## Control Panel (執行參數)

在 `config.py` 的 `RUN_CONFIG` 設定預設值：

```python
RUN_CONFIG = {
    "pages": 1,              # 頁數 (0=全部)
    "headless": False,       # 隱藏瀏覽器
    "human_like": "normal",  # 人類行為模擬 (minimal/normal/full)
    "delay_multiplier": 1.0, # 延遲倍率
}
```

### 參數說明

| 參數 | 說明 | 選項 |
|------|------|------|
| pages | 要爬幾頁 | 數字 (0=全部) |
| headless | 隱藏瀏覽器 | true/false |
| human_like | 人類行為模擬程度 | minimal/normal/full |
| delay_multiplier | 延遲倍率 | 數字 (1.0=正常) |

### 預設模式

| | test | full | apply |
|---|---|---|---|
| 頁數 | 1 | 全部 | 全部 |
| 瀏覽器 | 顯示 | 隱藏 | 顯示 |
| 人類行為 | minimal | full | full |
| 延遲倍率 | 1.0x | 1.5x | 2.0x |

## 使用方式

直接執行，會出現互動選單：

```bash
python main.py
```

選單：
```
=== 104 爬蟲 ===
狀態: 有 session 檔案 (選 4 可驗證是否有效)

請選擇功能:
  1. 執行爬蟲
  2. 登入 (儲存 session)
  3. 登出 (清除 session)
  4. 驗證登入狀態
  0. 離開

選擇 [1]: 1

選擇執行策略:
  1. 儲存職缺 - 將職缺資料儲存到檔案
  2. 自動投履歷 - 自動對職缺投遞履歷

策略 [1]: 1
搜尋關鍵字 [pm]: pm

=== Control Panel ===
快速模式:
  1. test - 測試 (1頁, 顯示瀏覽器)
  2. full - 完整 (全部頁, 隱藏瀏覽器)
  3. apply - 投履歷 (全部頁, 顯示瀏覽器)
  4. custom - 自訂

選擇 [3 apply]:
```

## 爬取流程 (兩階段 + Strategy Pattern)

### Phase 1: 列表頁抓取
1. 前往 104 首頁
2. 關閉彈窗
3. 輸入關鍵字搜尋
4. 套用篩選條件
5. 遍歷每頁的職缺卡片
6. 提取基本資訊

### Phase 2: 策略處理
根據選擇的策略處理每個職缺：
- **SaveStrategy**: 抓取詳細資訊並儲存到檔案
- **ApplyStrategy**: (待實作) 自動投遞履歷

## Strategy Pattern 架構

```
JobStrategy (base.py)         <- 抽象基類
    ├── SaveStrategy          <- 儲存職缺資料
    └── ApplyStrategy         <- 自動投履歷
```

### JobStrategy 介面
```python
class JobStrategy(ABC):
    @property
    def name(self) -> str           # 策略名稱
    @property
    def description(self) -> str    # 策略描述

    def before_process(jobs, context)   # 處理前準備
    def process_job(job, context)       # 處理單一職缺
    def after_process(jobs, context)    # 處理後收尾
```

### Context 內容
```python
context = {
    'mode': 'test' | 'complete',
    'is_complete_mode': bool,
    'browser_context': BrowserContext,
    'page': Page,
}
```

## 資料欄位

### 基本資訊 (從列表頁)
| 欄位 | 說明 | 範例 |
|------|------|------|
| title | 職缺名稱 | 專案經理 PM |
| url | 職缺連結 | https://www.104.com.tw/job/... |
| company | 公司名稱 | 某某科技股份有限公司 |
| location | 工作地點 | 台北市信義區 |
| experience | 經歷要求 | 3年以上 |
| education | 學歷要求 | 大學 |
| salary | 薪資範圍 | 月薪40,000~60,000元 |

### 詳細資訊 (從詳細頁)
| 欄位 | 說明 |
|------|------|
| detailed_job_description | 工作內容 |
| detailed_address | 上班地點 |
| detailed_work_hours | 上班時段 |
| detailed_company_benefits | 福利制度 |
| detailed_company_photos | 公司環境照片 |

## 篩選條件 (預設)

在 `config.py` 的 `DEFAULT_FILTERS` 設定：

```python
DEFAULT_FILTERS = {
    # 地區
    "areas": ["台北市", "新北市"],

    # 職務類別 (路徑: 大類 > 中類 > 小類)
    "job_category_path": ["經營／人資類", "人力資源類", "專案／產品管理類人員"],
    "job_categories": [
        "專案管理主管",
        "專案管理師",
        "產品企劃主管",
        "產品企劃師",
    ],

    # 工作要求
    "experience": ["1年以下", "1-3年"],
    "job_type": "全職",
    "update_time": "一個月內"
}
```

- **地區**: 台北市、新北市
- **職務類別**: 專案管理主管、專案管理師、產品企劃主管、產品企劃師
- **工作經歷**: 1年以下、1-3年
- **工作性質**: 全職
- **更新時間**: 一個月內

## 反檢測機制

### 瀏覽器偽裝
- 隨機 User-Agent
- 隱藏 webdriver 特徵
- 模擬 Chrome runtime

### 人類行為模擬
- 隨機延遲 (random_delay)
- 模擬滾動 (human_like_scroll)
- 模擬滑鼠移動 (human_like_mouse_move)
- 模擬閱讀停頓 (human_like_pause)

### 延遲設定
| 類型 | 時間範圍 (秒) |
|------|--------------|
| short | 0.3 ~ 0.8 |
| medium | 0.5 ~ 1.0 |
| long | 1.0 ~ 2.0 |
| page_load | 2.0 ~ 3.0 |

## 輸出格式

### JSON
```json
[
  {
    "title": "專案經理",
    "url": "https://www.104.com.tw/job/...",
    "company": "某某公司",
    "location": "台北市",
    "experience": "3年以上",
    "education": "大學",
    "salary": "待遇面議",
    "detailed_job_description": "...",
    "detailed_address": "...",
    "detailed_work_hours": "...",
    "detailed_company_benefits": "...",
    "detailed_company_photos": "..."
  }
]
```

### CSV
- 編碼: UTF-8 with BOM (utf-8-sig)
- 欄位順序: title, url, company, location, experience, education, salary, detailed_*

### 檔案命名規則
- 格式: `{mode}_{number}.json` / `{mode}_{number}.csv`
- 範例: `test_1.json`, `complete_3.csv`
- 自動遞增編號

## 登入機制

### Session 管理
- Session 檔案: `output/session.json`
- 使用 Playwright 的 `storage_state` 功能保存登入狀態
- 包含 cookies 和 localStorage

### 登入流程
1. 執行 `python main.py`
2. 選擇 `2. 登入`
3. 瀏覽器會開啟 104 登入頁面
4. 手動登入帳號
5. 關閉瀏覽器視窗
6. Session 自動儲存

### 使用方式
- 爬蟲執行時會自動載入已儲存的 session
- 如果 session 過期，重新選擇「登入」即可
- 未登入也可以爬取，但某些功能可能受限

## 模組說明

### main.py
- 程式入口
- Control Panel 互動選單
- 顯示執行結果

### config/
- **constants.py**: 固定常數
  - BASE_URL: 104 網站網址
  - OUTPUT_BASE_DIR: 輸出目錄
  - SESSION_FILE: Session 檔案路徑
  - CSV_FIELDNAMES: CSV 欄位順序
  - DELAY: 延遲設定
  - DEFAULT_FILTERS: 預設篩選條件
- **settings.py**: 執行設定
  - LOG_LEVEL: 日誌等級
  - RUN_CONFIG: 執行參數
  - MODE_PRESETS: 預設模式

### utils/
- **human_behavior.py**: 人類行為模擬
  - random_delay(): 隨機延遲
  - smart_delay(): 智慧延遲 (根據 human_like 設定)
  - human_like_scroll(): 模擬滾動
  - human_like_mouse_move(): 模擬滑鼠
  - human_like_pause(): 模擬停頓
  - human_like_long_break(): 長休息
- **captcha.py**: CAPTCHA 處理
  - check_captcha(): 檢測 CAPTCHA
  - wait_for_human_verification(): 等待人工驗證
  - handle_captcha_if_detected(): 主要入口函數
- **file_io.py**: 檔案存取
  - get_next_file_number(): 取得下一個檔案編號
  - save_jobs(): 儲存職缺
  - load_jobs(): 載入職缺
  - update_job(): 更新單一職缺

### scraper/auth.py
- has_session_file(): 檢查 session 檔案是否存在
- is_logged_in(): 驗證 session 是否有效
- login_and_save(): 開啟瀏覽器讓使用者手動登入
- clear_session(): 清除已儲存的 session
- get_session_path(): 取得 session 檔案路徑

### scraper/browser.py
- setup_stealth_browser(): 設定反檢測瀏覽器
- USER_AGENTS: User-Agent 列表

### scraper/search.py
- scrape_104_jobs(): 主要爬取函式
- _close_popups(): 關閉彈窗
- _search_keyword(): 輸入搜尋關鍵字
- _apply_filters(): 套用篩選條件
- _scrape_detail_by_url(): 抓取詳細頁面
- _goto_next_page(): 翻頁

### scraper/parser.py
- parse_job_info(): 解析混合職缺資訊字串
- get_section_content(): 取得頁面區塊內容
- extract_job_from_card(): 從卡片提取資訊

### scraper/detail.py
- scrape_job_detail(): 從詳細頁面抓取資訊

### strategy/base.py
- JobStrategy: 策略抽象基類
  - name: 策略名稱
  - description: 策略描述
  - before_process(): 處理前準備
  - process_job(): 處理單一職缺
  - after_process(): 處理後收尾

### strategy/save_strategy.py
- SaveStrategy: 儲存策略
  - 抓取職缺詳細資訊
  - 儲存到 CSV/JSON 檔案

### strategy/apply_strategy.py
- ApplyStrategy: 應徵策略
  - 開啟職缺詳細頁面
  - 點擊「應徵」按鈕
  - 在 popup 中點擊「確認送出」
  - 統計成功/失敗數量

## 依賴套件

```
playwright>=1.40.0
pandas>=2.0.0
```

## 安裝步驟

```bash
# 建立虛擬環境
python -m venv .venv
.venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 安裝 Playwright 瀏覽器
playwright install chromium
```
