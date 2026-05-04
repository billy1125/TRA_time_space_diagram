# CLAUDE.md

## Project overview
- 此專案將台鐵公開資料（JSON 時刻表）轉換為鐵路運行圖（SVG），供研究與參考。
- 目前版本：`1.3.9`（定義於 `environment_variable.py` `GlobalVariables.Version`）。
- 主要入口為 `batch.py`：負責讀取 `config.ini` 設定、掃描 JSON、轉檔流程控制、輸出與備份。
- 核心模組：
  - `read_tra_json.py`：讀取與篩選台鐵 JSON（`read_json`、`find_trains`）。
  - `train_space_time.py`：將列車停靠資料換算為時間/空間座標資料（`SpaceTime.CalculateSpaceTime`）。
  - `diagram_process.py`：彙整各車次資料並分營運線繪圖（`draw`、`set_train_path`、`check_undiscontinuous_order`）。
  - `diagram.py`：實際產生 SVG（`Diagram` class；背景格線、站線、車次路徑 `<path>` 與標號 `<textPath>`）。
  - `environment_variable.py`：單例 `GlobalVariables`，載入所有 CSV 設定表；包含路線、車種、座標對照等。
  - `progessbar.py`：終端機進度列（MIT License，第三方程式碼）。
  - `JSON/download_json.py`：從台鐵 ODS 網站（`ods.railway.gov.tw`）下載 JSON 時刻表，下載至 `JSON/downloads/`，SSL 驗證預設關閉（官方站 SSL 異常）。

## Data / config schema

### `config.ini`（必要，程式啟動即讀取）
```ini
[DEFAULT]
JsonFolder  = JSON          # 輸入 JSON 所在資料夾
OutputFolder = OUTPUT       # SVG 輸出根資料夾
BackupFolder = JSON_BACKUP  # 轉換後 JSON 備份資料夾
```

### `CSV/` 資料表（資料 schema，異動須確認向下相容）
| 檔案 | 說明 | 主鍵 / 重要欄位 |
|---|---|---|
| `OperationLines.csv` | 14 條營運路線基本資訊 | `LINE`（如 `LINE_WN`）、`FOLDER`、`PREFIX`、`MAX_X_AXIS` |
| `CarKind.csv` | 車種代碼 → CSS class 對照 | `CAR_CODE` → `CAR_TAG`（如 `taroko`、`local`、`tze_chiang`） |
| `Route.csv` | 路網拓樸（每站的順/逆行下一站、里程） | `ID`、`CW`/`CCW`（下一站）、`CW_KM`/`CCW_KM`（里程）、支線欄位 |
| `SVG_X_Axis.csv` | 時間（HHmm）→ SVG X 軸座標 | row[0]=時間字串, row[2]=座標值 |
| `SVG_Y_Axis.csv` | 各路線各站 SVG Y 軸座標 | `KIND`（路線代碼）、`ID`（車站代碼）、`SVGYAXIS`、`TERMINAL`（端點站 `Y`/空） |

### 支援路線一覽
```
LINE_WN   西部幹線北段（基隆-竹南）
LINE_WM   西部幹線台中線（竹南-彰化，經苗栗）
LINE_WSEA 西部幹線海岸線（竹南-彰化，經大甲）
LINE_WS   西部幹線南段（彰化-高雄）
LINE_P    屏東線（高雄-枋寮）
LINE_S    南迴線（枋寮-台東）
LINE_T    台東線（花蓮-台東）
LINE_N    北迴線（蘇澳新-花蓮）
LINE_I    宜蘭線（八堵-蘇澳）
LINE_PX   平溪深澳線（八斗子-菁桐）
LINE_LJ   內灣線（新竹-內灣）
LINE_NW   六家線（新竹-六家）
LINE_J    集集線（二水-車埕）
LINE_SL   沙崙線（中洲-沙崙）
```

## 資料流 / 控制流

1. `batch.py` 讀取 `config.ini`，掃描 `JsonFolder` 中的 `.json`（用 `queue.Queue` 管理）。
2. 對每個 JSON 檔：
   - `read_tra_json.read_json` 讀檔 → `find_trains` 篩選車次（可指定特定車次號）。
   - 每個車次呼叫 `SpaceTime.CalculateSpaceTime`：
     - `_find_train_timetable`：取出表定停靠站時刻。
     - `_find_passing_stations`：沿路網圖走訪出所有通過站（含山海線/成追線/支線判斷）。
     - `_estimate_time_space`：插補通過但不停靠站的時間（線性插值；跨午夜時間加 2880）。
     - `_time_space_to_operation_lines`：依 14 條路線切分，產生 per-line DataFrame。
   - 回傳 `Train_Data`（跨午夜功能目前已註解停用）。
3. `diagram_process.draw` 為每條路線建立 `Diagram` 物件，逐車次呼叫 `set_train_path`：
   - `check_undiscontinuous_order` 偵測環島車次斷點，切片分段繪製。
   - 標號定位：區間車（`local`）每段 >60px 奇偶交錯；其他車種依段長加密標注。
4. `Diagram.save_file` 完成 SVG 輸出，`batch.py` 將 JSON 移至 `BackupFolder`。

## How to work in this repo
- 安裝方式（Python 3.12+ 建議）：
  - 建議先建立虛擬環境再安裝依賴。
  - 主要依賴：`pandas`、`numpy`、`beautifulsoup4`、`requests`、`urllib3`。
- 啟動方式：
  - 互動模式：`python batch.py`（可選擇全部轉檔或指定車次）。
  - 批次模式：`python batch.py -b`（直接全部轉檔，不等待輸入）。
  - 下載 JSON：`python JSON/download_json.py`（互動式，可選擇要下載的日期）。
- 測試方式：
  - 目前 repo 尚未提供正式自動化測試框架；建議以小型 JSON 樣本執行 `python batch.py -b` 做基本驗證。
- lint / format 指令：
  - 目前 repo 未內建 lint/format 設定；若需導入，建議以 `ruff` + `black` 漸進導入，避免一次性大改造成噪音 diff。

## Engineering rules
- 優先維持 public API 穩定（例如 `batch.py` 參數介面與輸出檔案結構）。
- 優先新增測試再重構（若新增測試基礎設施，先覆蓋既有流程再調整實作）。
- 限制一次修改範圍（單次 PR 優先聚焦單一問題）。
- 若需大改，先提出 plan 再改（說明影響模組、相容性風險與回滾策略）。

## Files / areas to treat carefully
- 高風險模組：
  - `train_space_time.py`（時間/里程換算、路網走訪、跨午夜 +2880 邏輯、線性插值補點）。
  - `diagram_process.py`（車次切片、`StopOrder` 連續性判斷、標號定位距離計算）。
- 特殊車次處理邏輯（集中在 `_find_passing_stations`，修改前務必對照實際車次測試）：
  - 環島列車（車次 52，終點站 `1001`）。
  - 成追線（`line == '3'` 或同時有成功/追分二站）。
  - 山線 `1` / 海線 `2` / 其他 `0`（`LineDir` 順/逆行判斷）。
  - 平溪深澳線（十分站 `7332`）、內灣六家線（`1194`/`1203`）、集集線（`3432`/`3431`）、沙崙線（`4272`）。
- legacy code：
  - `diagram.py` 以大量字串拼接輸出 SVG，修改時要特別注意 escaping 與座標一致性。
  - SVG 內嵌 CSS 以單一大字串硬編碼（`Diagram.__init__`），新增車種需同步更新 `CarKind.csv` 與 CSS。
- I/O boundary：
  - `batch.py` 的資料夾掃描、檔案搬移（`JSON` → `JSON_BACKUP`）與 `config.ini` 路徑設定。
  - `JSON/download_json.py` 的外部網站抓取行為（SSL 驗證已關閉）、下載到 `JSON/downloads/`（非 `JSON/`，需手動移檔）。
- CSV 資料 schema：
  - 本專案無資料庫 migration；但 CSV 欄位結構可視為「資料 schema」，調整前需確認向下相容。
  - `GlobalVariables` 為 singleton，程式啟動時載入所有 CSV；執行期不重新讀取。

## Definition of done
- tests pass（至少完成可重現的流程驗證；若有自動化測試需全綠）。
- lint pass（若該 PR 有引入 lint 工具，需通過）。
- 沒有未說明的行為變更（輸出檔名、路徑、格式、過濾規則需在 PR 說明）。
- 回報風險與未覆蓋情境（例如特定路線、跨午夜車次、環島車次、支線切換、缺漏欄位 JSON）。
