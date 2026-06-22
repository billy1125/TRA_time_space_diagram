# 台灣鐵路局公開資料JSON鐵路運行圖繪製程式

> **Taiwan Railway (TRA) Time-Space Diagram / Train Graph Generator** — a Python tool that converts Taiwan Railways Administration open-data JSON timetables into scalable SVG railway diagrams（將台鐵公開資料 JSON 時刻表轉換為 SVG 鐵路運行圖）。

![License](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)
![Version](https://img.shields.io/badge/version-1.3.9-orange.svg)
![Output](https://img.shields.io/badge/output-SVG-ff69b4.svg)
![Data](https://img.shields.io/badge/data-TRA%20Open%20Data-lightgrey.svg)

|項目|內容|
|---|---|
|專案名稱|TRA_time_space_diagram|
|Author|呂卓勳 Cho-Hsun Lu|
|E-mail|billy1125@gmail.com|
|版本|1.3.9|

## 🚆 緣起

鐵道愛好者通常都會使用**鐵路運行圖（Railway Time-Space Diagram，又稱列車運行圖、時空圖、train graph）**，幫助研究鐵道相關事務，雖然有人會出版紙本台鐵鐵路運行圖，但是當台鐵改點，紙本的資訊參考價值就會變低。所以當我知道台鐵已經將**台鐵時刻表**以 JSON 公開於網路上之後，便試圖以 Python 開發一個繪製**台灣鐵路運行圖**的程式。

本專案以**台鐵公開資料（TRA open data）**為基礎，將每日**台鐵時刻表 JSON** 自動轉換為**鐵路運行圖 SVG**，提供鐵道研究、教學與參考使用。

## ⚠️ 限制

本程式鐵路運行圖均來自於台鐵 open data 進行分析整理與繪製。然而**公開資料不等於實際台鐵的運行計畫**，僅是旅客所需的列車到站與離站時間資料，列車的待避或會車狀況無法在運行圖中展示，貨運、迴送等非客運車次也因台鐵並未在公開資料集提供。因此會出現運行圖與實際運行有所差異，以及無法提供非客運車次的運行線。因此實際鐵路運行情況，請以台鐵所公布資訊或鐵路運行實況為準。

## ✨ 程式功能

本程式用於將台鐵公開之時刻表 JSON 格式檔案 (以下稱台鐵 JSON)，轉換為鐵路運行圖，運行圖格式為可縮放向量圖形（Scalable Vector Graphics, SVG）。並且提供一個批次下載台鐵 JSON 之簡易程式。

### 功能特色

|功能|說明|
|---|---|
|🗺️ JSON → SVG 轉檔|將台鐵時刻表 JSON 轉換為可縮放向量圖形（SVG）鐵路運行圖|
|⚡ 批次轉檔模式|`python batch.py -b` 一次轉換整個資料夾的所有 JSON|
|📥 JSON 批次下載|`download_json.py` 從台鐵 ODS 官網批次下載時刻表 JSON|
|🛤️ 14 條營運路線|涵蓋西部幹線、山海線、屏東線、南迴線、東部幹線與各支線|
|🌙 跨午夜與環島|處理跨午夜時間推算與環島列車路徑切片繪製|
|🔀 支線與山海線|自動判斷山線／海線、成追線及各支線的列車路徑|
|🎨 車種分色標號|依車種（太魯閣、自強、莒光、區間車等）以 CSS 分色並標注車次|

### 支援路線一覽

|路線代碼|路線名稱|區間|
|---|---|---|
|`LINE_WN`|西部幹線北段|基隆－竹南|
|`LINE_WM`|西部幹線台中線（山線）|竹南－彰化（經苗栗）|
|`LINE_WSEA`|西部幹線海岸線（海線）|竹南－彰化（經大甲）|
|`LINE_WS`|西部幹線南段|彰化－高雄|
|`LINE_P`|屏東線|高雄－枋寮|
|`LINE_S`|南迴線|枋寮－台東|
|`LINE_T`|台東線|花蓮－台東|
|`LINE_N`|北迴線|蘇澳新－花蓮|
|`LINE_I`|宜蘭線|八堵－蘇澳|
|`LINE_PX`|平溪深澳線|八斗子－菁桐|
|`LINE_LJ`|內灣線|新竹－內灣|
|`LINE_NW`|六家線|新竹－六家|
|`LINE_J`|集集線|二水－車埕|
|`LINE_SL`|沙崙線|中洲－沙崙|

## Python 版本與所需相關程式開發套件

目前本程式基於 Python 3.12.4 開發，除此之外本程式需要以下套件，包括：

* [Pandas](https://github.com/pandas-dev/pandas)：用於列車推算通過車站時間，本程式開發使用版本為 2.2.2
* [NumPy](https://github.com/numpy/numpy)：搭配 Pandas 進行數值運算
* [beautifulsoup4](https://github.com/getanewsletter/BeautifulSoup4)：用於解析台鐵 JSON 下載頁面，本程式開發使用版本為 4.12.3
* [requests](https://github.com/psf/requests)、[urllib3](https://github.com/urllib3/urllib3)：用於批次下載台鐵 JSON 時刻表

進度條程式碼則採用 Vladimir Ignatev 所設計的[程式](https://gist.github.com/davincif/3e1cb5ef1c4007d4f5ca690d68db8e7b)。svg 繪圖部分程式感謝 [nedwu](https://github.com/nedwu)的啟發，並且參考其[專案部分程式碼](https://github.com/nedwu/TRAOpenDataDiagramer)。

> 以上套件為主要開發環境，若您採用非相同版本之 Python 與套件，執行上有任何錯誤歡迎交流。

## 🚀 使用方法

請將所有程式解壓縮到同一檔案夾，包括 CSV、JSON、OUTPUT 等檔案夾均需於同一檔案夾，再將所需要轉檔的台鐵 JSON 檔案，置放於 JSON 檔案夾之中，台鐵 JSON 檔案可至[台鐵公開資料網站](https://ods.railway.gov.tw/tra-ods-web/ods/download/dataResource/railway_schedule/JSON/list/)中下載，或使用本程式提供的 download_json.py 批次下載（詳見下方說明）。

程式以作業系統的命令行 (command-line) 模式執行，執行方式包括一般模式與參數模式，分述如下：

### 一般模式

命令行執行語法

```
$ python batch.py
```

```
************************************
台鐵JSON轉檔運行圖程式 - 版本：1.3.9
************************************
```
之後會顯示本程式的標題，並且顯示版本。
```
請選擇轉檔方式，直接轉檔請直接按Enter鍵，需要轉檔特定車次請輸入「Y」再進行選擇，離開請按「N」：Y
```
詢問您是否需要轉換特定車次，若您需要轉換特定車次，請按`「Y」`，若不需，請直接按下`「ENTER」`即可。
> 請注意！已轉檔的 JSON 檔案將移動到 JSON_BACKUP 檔案夾。
若按下`「ENTER」`，程式將直接就 JSON 檔案夾中所有以「JSON」附檔名之資料進行轉檔，直到所有 JSON 檔案轉換完成為止。
```
請問特定車次號碼？
請輸入車次號後再按Enter鍵。如果有多個車次，請依序輸入各車次，中間以半形空白鍵隔開(例如: 408 426 111)，再按Enter鍵：3671
```
若按下`「Y」`，將繼續顯示以上問題。
請輸入車次號後再按Enter鍵，例如第 3671 車次普快車，請輸入`「3671」`再按Enter鍵，程式將尋找是否有該車次，並且直接繪製運行圖。
如果有多個車次需要繪製，請依序輸入各車次，中間以半形空白鍵隔開(例如: 408 426 111)，輸入結束則直接按下「Enter」即可。
```
共有 60 個JSON 檔案需要轉檔。

目前進行日期「20230623」轉檔。

[==========================================------------------] 70.7% ...目前正在轉換: 車次3671
```
繪製運行圖的過程中，程式將顯示進度條與正在處理的車次。
```
檔案轉換完成！轉換時間共 15.6 秒
```
如果繪製完成，將顯示以上訊息，訊息包括轉換所耗費的時間。

> 附註：轉換時間需視 CPU 效能，保守時間約 1 分鐘內可完成。
```
無法執行！沒有 JSON 檔案，請在 JSON 資料夾中置入台鐵的時刻表 JSON。
```
如果您在置放 JSON 的檔案夾中沒有台鐵 JSON 檔案，則會顯示以上錯誤訊息。
程式繪製完成的運行圖，將依照不同台鐵營運路線，分別置放於 OUTPUT 檔案夾之中，檔名則與轉換的 JSON 檔名相同。

## ⚡ 批次轉檔模式

本程式能以批次模式執行，程式可將 JSON 所在的資料夾逐一批次轉檔，再儲存到輸出資料夾。參數為`「-b」`，可見以下語法：

```
$ python batch.py -b
```

請注意，若您要改動台鐵 JSON 檔案、運行圖輸出與轉檔後 JSON 檔案資料夾位置，請修改檔案`「config.ini」`，檔案內容如下，可依照您的需要修改：

```
[DEFAULT]
JsonFolder = JSON               # 台鐵 JSON 檔案預設資料夾
OutputFolder = OUTPUT           # 運行圖輸出預設資料夾
BackupFolder = JSON_BACKUP      # 轉檔後 JSON 檔案預設資料夾
```

以批次模式執行後，程式將自動將所有置放於您指定的 JSON 檔案夾中的台鐵 JSON 進行轉檔，並且依照不同台鐵營運路線，置放於您指定的 OUTPUT 檔案夾之中，最後將轉檔後的 JSON 資料夾移動至轉檔後 JSON 檔案預設資料夾。

> 檔案夾位置可指定完整的硬碟路徑，請注意：`請勿有中文字元，可能會出現未預期的錯誤`。

## 📥 擷取台鐵 JSON 程式

若您需要批次下載台鐵的 JSON 時刻表，請以命令行模式，執行 JSON 檔案夾中之 download_json.py 程式，執行語法為：

```
$ python download_json.py
```

該程式會先讀取[台鐵公開資料網站](https://ods.railway.gov.tw/tra-ods-web/ods/download/dataResource/railway_schedule/JSON/list/)中可下載的 JSON 檔案清單，並列出讓您選擇，例如：

```
可下載檔案：

  1. 20260614.json
  2. 20260615.json
  3. 20260616.json
  ...

輸入要下載的編號
例如：1-5 或 1,3,8
直接按 Enter = 全部下載
輸入 q = 離開程式

選擇:
```

您可以輸入單一編號、以逗號分隔的多個編號（例如 `1,3,8`）、或以連字號表示的範圍（例如 `1-5`）；直接按下 `Enter` 會下載全部，輸入 `q` 則離開程式。

若下載目標已有同名檔案，程式會詢問是否覆蓋，可選擇 `[y]`是、`[n]`否、`[a]`全部覆蓋、`[s]`全部略過、`[q]`離開。

> 注意：下載的 JSON 檔案會儲存於程式執行目錄下的 `downloads` 子資料夾，若要轉檔請再將檔案移至 `JSON` 資料夾。由於台鐵公開資料站的 SSL 憑證常有異常，本程式預設關閉 SSL 驗證（`verify=False`）。

> 附註：台鐵每日均提供當日至 60 天內每日之時刻表資料，以 JSON 格式提供。如果想要看相關資料定義的說明，可至[政府資料開放平台](https://data.gov.tw/dataset/6138)參考。

## 📖 閱讀運行圖之方法

本程式所轉換之運行圖，檔案副檔名為 **.svg**，請使用瀏覽器直接開啟檔案即可，本程式所轉換之運行圖於 Google Chrome、Mozilla Firefox、Opera、Apple Safari 均能正常顯示，至於其他瀏覽器尚未實地測試，若有問題也歡迎回報。

## 🙏 致謝

* nedwu(https://github.com/nedwu) 的程式碼
* 黃祈恩(https://www.facebook.com/profile.php?id=100051647619113&sk=about) 幫忙將台鐵車站代碼基本資料的 CSV 檔案更正
* 施佩佶(https://www.facebook.com/profile.php?id=100009938435817) 於 2020.10.16 通報 6655、6657 車次錯誤問題
* 張柏皓(https://www.facebook.com/profile.php?id=100066832751160) 於 2023.04.19 通報 6105、6702 車次錯誤問題
* 王羿
(https://www.facebook.com/profile.php?id=100033320060400) 於 2023.06.03 通報 2023.06.22 5374 車次錯誤問題

感謝以上網友對於本程式的建議與錯誤回報，您的協助能讓本程式更臻完整，感謝！