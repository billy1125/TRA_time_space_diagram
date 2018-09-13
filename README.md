# 台灣鐵路局公開資料JSON繪製鐵路運行圖(SVG格式)程式(TRA_time_space_diagram)

|Author|呂卓勳 Cho-Hsun Lu|
|---|---
|E-mail|billy1125@gmail.com

## 緣起

鐵道愛好者通常都會使用**鐵路運行圖(Railway Time-Space Diagram)**，幫助研究鐵道相關事務，雖然有人會出版紙本台鐵鐵路運行圖，但是當台鐵改點，紙本的資訊參考價值就會變低。所以當我知道台鐵已經將時刻資訊以 JSON 公開於網路上之後，便試圖以 Python 開發一個繪製台灣鐵路運行圖的程式。

## 限制

本程式鐵路運行圖均來自於台鐵 open data 進行分析整理與繪製。然而**公開資料不等於實際台鐵的運行計畫**，僅是旅客所需的列車到站與離站時間資料，列車的待避或會車狀況無法在運行圖中展示，因此會出現運行圖與實際運行有所差異的現象。因此實際鐵路運行情況，請以台鐵所公布資訊為準。

## 程式功能

本程式用於將台鐵公開之時刻表 JSON 格式檔案 (以下稱台鐵 JSON)，轉換為鐵路運行圖，運行圖格式為可縮放向量圖形（Scalable Vector Graphics, SVG）。並且提供一個批次下載台鐵 JSON 之簡易程式。

## 執行語言與所需相關套件

目前本程式主要於 Python 3.7 開發，除此之外本程式需要以下套件，包括：

* [Pandas v0.23.4](https://github.com/pandas-dev/pandas) (用於列車推算通過車站時間)
* [svgwrite v1.1.12](https://github.com/mozman/svgwrite) (用於繪製 SVG 格式之圖片)
* [beautifulsoup4 v4.6.3](https://github.com/getanewsletter/BeautifulSoup4) (用於擷取台鐵 JSON)

進度條程式碼則採用 Vladimir Ignatev 所設計的[程式](https://gist.github.com/davincif/3e1cb5ef1c4007d4f5ca690d68db8e7b)。

> 以上套件為主要開發環境，若您採用非相同版本之 Python 與套件，執行上有任何錯誤歡迎交流。

## 使用方法

請將所有程式解壓縮到同一檔案夾，包括 CSV、JSON、OUTPUT 等檔案夾均需於同一檔案夾，再將所需要轉檔的台鐵 JSON 檔案，置放於 JSON 檔案夾之中，台鐵 JSON 檔案可至[台鐵公開資料網站](http://163.29.3.98/json/)中下載。

程式以作業系統的命令行 (command-line) 模式執行，執行方式包括一般模式與參數模式，分述如下：

### 一般模式

命令行執行語法

```
$ python batch.py
```

之後會詢問您是否需要轉換特定車次，若您需要轉換特定車次，請按`「Y」`，若不需，請直接按下`「ENTER」`即可。

```
您需要執行特定車次嗎？不需要請直接輸入Enter，或者輸入 "Y"：Y
```

若按下`「ENTER」`，程式將直接就 JSON 檔案夾中所有以「JSON」附檔名之資料進行轉檔，直到所有 JSON 檔案轉換完成為止。

> 請注意！JSON 檔案將刪除。

若按下`「Y」`，將繼續顯示以下問題：

```
請問特定車次號碼？(請輸入車次號)：3671
```

請再輸入特定車次號即可，例如第 3671 車次普快車，請輸入`「3671」`即可，程式將尋找是否有該車次，並且直接繪製運行圖。

程式繪製完成的運行圖，將依照不同台鐵營運路線，分別置放於 OUTPUT 檔案夾之中，檔名則與轉換的 JSON 檔名相同。

### 參數模式

本程式支援以參數模式執行，您可以直接輸入以下參數，以半形空白隔開，直接執行無須一一回答問題。參數包括：

* 需轉換台鐵 JSON 檔案存放資料夾位置
* 運行圖轉換完成儲存位置
* 特定車次之車次號，若要轉換所有車次，參數為 ALL

若您不改動 JSON 與 OUTPUT 檔案夾位置，並且指定要轉換第 3671 車次普快車，可以這樣輸入：

```
$ python batch.py JSON OUTPUT 3671
```

若您改動 JSON 與 OUTPUT 檔案夾位置，分別為 **/Users/username/Desktop/JSON** 與 **/Users/username/Desktop/OUTPUT**，並且指定要轉換所有車次，可以這樣輸入：

```
$ python batch.py /Users/username/Desktop/JSON /Users/username/Desktop/OUTPUT ALL
```

執行後，程式將自動將所有置放於您指定的 JSON 檔案夾中的台鐵 JSON 進行轉檔，並且依照不同台鐵營運路線，置放於您指定的 OUTPUT 檔案夾之中。

## 擷取台鐵 JSON 程式

若您需要批次下載當日之台鐵所有 JSON 程式，請以命令行模式，執行 JSON 檔案夾中之 download_json.py 程式，執行語法為：

```
$ python download_json.py
```

該程式將直接下載[台鐵公開資料網站](http://163.29.3.98/json/)網站中所有 JSON 檔案，並且置放於 JSON 檔案夾中。

> 附註：台鐵每日均提供當日至 45 天內每日之時刻表資料，以 JSON 格式提供。

## 閱讀運行圖之方法

本程式所轉換之運行圖，檔案副檔名為 **.svg**，請使用瀏覽器直接開啟檔案，請注意，請將 OUTPUT 檔案夾中的 **stlye.css** 檔案與運行圖置放於同一檔案夾中，再以瀏覽器開啟， **stlye.css** 檔案為設定運行圖樣式之 CSS 檔案。

目前為止，本程式所轉換之運行圖於 Google Chrome、Mozilla Firefox、Opera、Apple Safari 均能正常顯示，至於其他瀏覽器尚未實地測試，若有問題也歡迎回報。