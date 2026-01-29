# JobSniper

104 人力銀行自動化工具 — 自動搜尋職缺、儲存資料、投遞履歷。

## 功能

- **自動搜尋** — 依關鍵字、地區、職務類別、薪資等條件搜尋職缺
- **儲存職缺** — 將搜尋結果（含詳細資訊）匯出為 CSV / JSON
- **自動投履歷** — 自動對搜尋到的職缺投遞履歷，遇到需手動處理的會保留 tab
- **反偵測** — Stealth 瀏覽器 + 人類行為模擬，降低被封鎖的風險
- **CAPTCHA 處理** — 自動偵測驗證碼，暫停等待手動解決
- **Session 管理** — 登入一次後儲存 session，後續不需重複登入
- **桌面 GUI** — pywebview 桌面介面，操作直覺、即時顯示執行 log

## 安裝

### 環境需求

- Python 3.11+

### 安裝步驟

```bash
git clone https://github.com/your-username/JobSniper.git
cd JobSniper
pip install .
```

首次執行時會自動下載 Chromium 瀏覽器（~170MB），之後不會重複下載。

## 使用方式

```bash
python main.py
```

啟動後會開啟桌面視窗，包含：

- 關鍵字輸入、模式/策略選擇
- 登入 / 登出 / 驗證登入 按鈕
- 即時 log 輸出區域

### 首次使用

1. 點擊「登入」按鈕 — 會開啟瀏覽器讓你手動登入 104
2. 登入後 session 會自動儲存
3. 之後點擊「開始執行」即可開始使用

### 執行模式

| 模式 | 說明 |
|------|------|
| test | 測試用，1 頁，顯示瀏覽器 |
| full | 完整爬取，全部頁，隱藏瀏覽器 |
| apply | 自動投履歷，全部頁，顯示瀏覽器 |
| custom | 自訂所有參數 |

### 處理策略

| 策略 | 說明 |
|------|------|
| 儲存職缺 | 抓取職缺詳細資料，儲存為 CSV/JSON |
| 自動投履歷 | 自動點擊應徵按鈕，投遞履歷 |

## 專案結構

```
JobSniper/
├── main.py                 # 程式入口
├── config/                 # 設定檔（搜尋條件、執行參數）
│   ├── constants.py
│   └── settings.py
├── src/
│   ├── core/               # 核心邏輯（瀏覽器、搜尋、解析）
│   │   ├── auth.py         # 登入/Session 管理
│   │   ├── browser.py      # Stealth 瀏覽器設定
│   │   ├── search.py       # 搜尋列表頁邏輯
│   │   ├── detail.py       # 職缺詳細頁解析
│   │   └── parser.py       # HTML 解析
│   ├── strategy/           # 策略模式（處理職缺的方式）
│   │   ├── base.py         # 策略抽象基類
│   │   ├── context.py      # 策略上下文
│   │   ├── save_strategy.py
│   │   └── apply_strategy.py
│   ├── ui/                 # 桌面 GUI（pywebview）
│   │   ├── index.html      # 前端介面 (HTML/CSS/JS)
│   │   ├── api.py          # Python ↔ JS API 橋接
│   │   └── logger.py       # Log 攔截，供前端即時顯示
│   └── utils/              # 工具函式
│       ├── setup.py        # 瀏覽器自動安裝
│       ├── captcha.py      # CAPTCHA 偵測
│       ├── file_io.py      # 檔案讀寫
│       └── human_behavior.py # 人類行為模擬
├── pyproject.toml
└── LICENSE
```

## 輸出

執行結果會儲存在 `output/` 目錄：

- `output/csv/` — CSV 格式
- `output/json/` — JSON 格式
- `output/manual_handle/` — 需手動處理的職缺清單

## 設定

搜尋條件在 `config/constants.py` 的 `DEFAULT_FILTERS` 中設定：

- 地區
- 職務類別
- 薪資下限
- 工作經歷
- 工作性質
- 更新時間

## 開發者筆記

使用 Playwright Codegen 來找 HTML element：

```bash
playwright codegen --load-storage="output/session.json" "https://www.104.com.tw"
```

## License

MIT License
