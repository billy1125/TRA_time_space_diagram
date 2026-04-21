# AGENTS.md

## Project overview
- 此專案將台鐵公開資料（JSON 時刻表）轉換為鐵路運行圖（SVG），供研究與參考。
- 主要入口為 `batch.py`：負責讀取設定、掃描 JSON、轉檔流程控制、輸出與備份。
- 核心模組：
  - `read_tra_json.py`：讀取與篩選台鐵 JSON。
  - `train_space_time.py`：將列車停靠資料換算為時間/空間座標資料。
  - `diagram_process.py`：彙整各車次資料並分營運線繪圖。
  - `diagram.py`：實際產生 SVG（背景格線、站線、車次路徑與標註）。
  - `environment_variable.py`：全域參數、路線與車種對照等設定。
- 重要資料流 / 控制流：
  1. `batch.py` 掃描 `JsonFolder` 中的 `.json`。
  2. 透過 `read_tra_json` 解析與（可選）車次篩選。
  3. 每個車次交給 `SpaceTime.CalculateSpaceTime` 產生繪圖資料。
  4. `diagram_process.draw` 依營運線建立 `Diagram` 物件並畫線。
  5. 輸出 SVG 至 `OutputFolder`，並將已處理 JSON 移到 `BackupFolder`。

## How to work in this repo
- 安裝方式（Python 3.12+ 建議）：
  - 建議先建立虛擬環境再安裝依賴。
  - 依 README 所述主要依賴：`pandas`、`beautifulsoup4`。
- 啟動方式：
  - 互動模式：`python batch.py`
  - 批次模式：`python batch.py -b`
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
  - `train_space_time.py`（時間/里程換算與補點邏輯）
  - `diagram_process.py`（車次切片、標註定位與跨站序處理）
- legacy code：
  - `diagram.py` 以大量字串拼接輸出 SVG，修改時要特別注意 escaping 與座標一致性。
- I/O boundary：
  - `batch.py` 的資料夾掃描、檔案搬移（`JSON` -> `JSON_BACKUP`）與 `config.ini` 路徑設定。
  - `JSON/download_json.py` 的外部網站抓取行為與失敗重試策略。
- migration / schema / deploy 相關區域：
  - 本專案無資料庫 migration；但 CSV/JSON 欄位結構可視為「資料 schema」，調整前需確認向下相容。

## Definition of done
- tests pass（至少完成可重現的流程驗證；若有自動化測試需全綠）。
- lint pass（若該 PR 有引入 lint 工具，需通過）。
- 沒有未說明的行為變更（輸出檔名、路徑、格式、過濾規則需在 PR 說明）。
- 回報風險與未覆蓋情境（例如特定路線、跨午夜車次、缺漏欄位 JSON）。
