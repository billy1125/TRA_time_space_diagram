# 運行圖SVG產出
# 部分程式碼為 nedwu (https://github.com/nedwu) 所啟發，並且參考其專案部分程式碼 (https://github.com/nedwu/TRAOpenDataDiagramer)。

import time
import environment_variable as ev

Globals = ev.Singleton_GlobalVariables_Instance

class Diagram:
    def __init__(self, stations_to_draw, location, date, line, width, height, diagram_hours):

        self.file_name = location + date + '.svg'
        self.date = date
        self.line = line
        self.width = width
        self.height = height
        self.diagram_hours = diagram_hours
        self.stations_to_draw = stations_to_draw

        # svg檔案描述、背景、基本大小基本設定
        self.fileHandler = open(self.file_name, 'w', encoding='utf-8')
        self.fileHandler.write('<?xml version="1.0" encoding="utf-8" ?>')
        self.fileHandler.write(
            '<?xml-stylesheet href="style.css" type="text/css" title="sometext" alternate="no" media="screen"?>')
        self.fileHandler.write(
            '<svg baseProfile="full" xmlns="http://www.w3.org/2000/svg" xmlns:ev="http://www.w3.org/2001/xml-events" xml'
            'ns:xlink="http://www.w3.org/1999/xlink" style="font-family:Tahoma" width="' + str(self.width) + '" height="' + str(self.height + 100) + '" version="1.1"><defs />')

        self._draw_background()

    def _add_text(self, x, y, string, _color = None, _class = None, transform = None):

        transformStr = ''

        if transform is not None :
            transformStr = ' transform="' + transform + '"'
        if _class is not None :
            self.fileHandler.write( '<text class="' + _class + '" x="' + x + '" y="' + y + '"' + transformStr + '>' + string + '</text>' )
        elif _color is not None :
            self.fileHandler.write( '<text fill="' + _color + '" x="' + x + '" y="' + y + '"' + transformStr + '>' + string + '</text>' )
        else :
            self.fileHandler.write( '<text x="' + x + '" y="' + y + '"' + transformStr + '>' + string + '</text>' )

    def _add_line(self, x1, y1, x2, y2, _color = None, _class = None ) :

        if _class is not None :
            self.fileHandler.write( '<line class="' + _class + '" x1="' + x1 + '" x2="' + x2 + '" y1="' + y1 + '" y2="' + y2 + '" />' )
        elif _color is not None :
            self.fileHandler.write( '<line stroke="' + _color + '" x1="' + x1 + '" x2="' + x2 + '" y1="' + y1 + '" y2="' + y2 + '" />' )
        else :
            self.fileHandler.write( '<line x1="' + x1 + '" x2="' + x2 + '" y1="' + y1 + '" y2="' + y2 + '" />' )

    def _add_path( self, pathList, lineId, _color = None, _class = None, _emphasis = False ) :

        emphasisStr = '" style="stroke-width: 4" />' if _emphasis else '" />'

        if _class is not None :
            self.fileHandler.write( '<path class="' + _class + '" d="' + pathList + '" id="' + lineId + emphasisStr )
        elif _color is not None :
            self.fileHandler.write( '<path stroke="' + _color + '" d="' + pathList + '" id="' + lineId + emphasisStr )
        else :
            self.fileHandler.write( '<path d="' + pathList + '" id="' + lineId + emphasisStr )

    def _add_path_text(self, _line_id, _train_id, _class, _startOffset):
        self.fileHandler.write( '<text><textPath class = "' + _class + '" startOffset = "' + _startOffset + '" xlink:href = "#' +
                                _line_id + '"><tspan dy="-3" font-size="80%">' + _train_id + '</tspan></textPath></text>' )

    # 繪製基底圖
    def _draw_background(self):
        localtime = time.asctime(time.localtime(time.time()))

        self._add_text("5", "20", Globals.LineDescription[self.line] + ' 日期：' + self.date +'，運行圖均來自台鐵公開資料所分析，僅供參考，正確資料與實際運轉狀況請以台鐵網站或公告為主。台鐵JSON Open Data轉檔運行圖程式版本：' + Globals.Version + ' 轉檔時間：' + localtime, "#000000", None, None)

        # 時間線
        hours = self.diagram_hours
        text_spacing_factor = 500
        if self.height <= 1500:  # 較小的運行圖高度，小時顯示的間距設定較窄
            text_location_factor = 250
        # 小時
        for i in range(0, len(hours)):
            x = 50 + i * 1200
            self._add_line(str(x), "50", str(x), str(self.height + 50), None, "hour_line")

            for j in range(0, 21):
                y = j * text_spacing_factor
                if y <= self.height:
                    self._add_text(str(x), str(49 + y), '{:0>2d}'.format(hours[i]) + '00', "#2e2e1f")

            if i != len(hours) - 1:  # 每10分鐘
                for j in range(0, 5):
                    x = 50 + i * 1200 + (j + 1) * 200
                    if j != 2:
                        self._add_line(str(x), "50", str(x), str(self.height + 50), None, "min10_line")
                    else:  # 30分鐘顏色不同
                        self._add_line(str(x), "50", str(x), str(self.height + 50), None, "min30_line")

                    for k in range(0, 21):
                        y = k * text_spacing_factor
                        if y <= self.height:
                            if j != 2:
                                self._add_text(str(x), str(49 + y), str(j + 1) + "0", "#adad85", None, None)
                            else:
                                self._add_text(str(x), str(49 + y), str(j + 1) + "0", "#5c5c3d", None, None)

        # 車站線
        for LineName, StationNumber, StationName, StationLoc in self.stations_to_draw:
            y = float(StationLoc) + 50
            if StationNumber != 'NA':
                self._add_line("50", str(y), str(self.width - 50), str(y), None, "station_line")
            else:
                self._add_line("50", str(y), str(self.width - 50), str(y), None, "station_noserv_line")
            for i in range(0, 31):
                if StationNumber != 'NA':
                    self._add_text(str(5 + i * 1200), str(y - 5), StationName, "#000000", None, None)
                else:
                    self._add_text(str(5 + i * 1200), str(y - 5), StationName, "#c2c2a3", None, None)

    # 繪製線條
    def draw_line(self, train_id, path, color, option_id = None):

        if option_id is None:
            line_id = train_id
        elif option_id is not None:
            line_id = train_id + "_" + option_id

        if path != 'M':  # 避免無資料
            self._add_path(path, line_id, None, color, None)
            for i in range(0, 6):
                self._add_path_text(line_id, train_id, color, str(50 + 600 * i))
            # for i in range(0, 5):
            #     self._add_path_text(line_id, train_id, color, str(20 * i) + "%")

    # 存檔
    def save_file(self):

        self.fileHandler.write('</svg>')
        self.fileHandler.close()

        return Globals.LineDescription[self.line] + ' 日期：' + self.date + ' 運行圖繪製完成 \n'
    