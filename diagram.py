# 運行圖SVG產出
# 部分程式碼為 nedwu (https://github.com/nedwu) 所啟發，並且參考其專案部分程式碼 (https://github.com/nedwu/TRAOpenDataDiagramer)。

import time
import environment_variable as ev

# 公用參數
Globals = ev.GlobalVariables()

class Diagram:
    
    def __init__(self, stations_to_draw, location, date, line, width, height, diagram_hours):

        self.file_name = location + date + '.svg'
        self.date = date
        self.line = line
        self.width = width
        self.height = height
        self.diagram_hours = diagram_hours
        self.stations_to_draw = stations_to_draw        
        self.fileHandler = open(self.file_name, 'w', encoding='utf-8')
        self.fileHandler.write('<?xml version="1.0" encoding="utf-8" ?>')
        self.fileHandler.write(
            '<?xml-stylesheet href="style.css" type="text/css" title="sometext" alternate="no" media="screen"?>')
        self.fileHandler.write(
            '<svg baseProfile="full" xmlns="http://www.w3.org/2000/svg" xmlns:ev="http://www.w3.org/2001/xml-events" xml'
            'ns:xlink="http://www.w3.org/1999/xlink" style="font-family:Tahoma" width="' + str(self.width) + '" height="' + str(self.height + 100) + '" version="1.1"><defs />')
        self.fileHandler.write('<style>/* 基本設定 */line { stroke-width: .3; font-weight: 100 } svg { font-family: Tahoma, Verdana, sans-serif; font-size: 14px } path { transition-property: stroke-width; transition-duration: 1s; transition-timing-function: ease-out; transition-delay: 0s; stroke-linecap: round; stroke-width: 2.5; fill: none } path:hover { stroke-width: 6 } path:focus { stroke-width: 6 } /* 主要基線 */ .hour { fill: #2e2e1f } .hour_midnight { fill: red; font-weight: 700 } .hour_line { stroke: #000 } .min10 { fill: #adad85 } .min10_line { stroke: #a18cfc } .min30 { fill: #5c5c3d } .min30_line { stroke: #0105e0 } .now_time_line { stroke: #ff0000; stroke-width: 1.5; stroke-dasharray: 6, 1; } .station { fill: #000 } .station_line { stroke: #000 } .station_noserv { fill: #bfbfbf } .station_noserv_line { stroke: #bfbfbf } /* 車次線 */ .taroko, .kuaimu { stroke: #20b2aa } .puyuma, .zhongxing, .direct { stroke: red } .tze_chiang, .alishan_local { stroke: orange } .tze_chiang_diesel { stroke: gold } .emu1200 { stroke: #ff008c } .emu300 { stroke: #f44 } .emu3000 { stroke: #000 } .chu_kuang, .chushan1, .chushan2, .skip_stop { stroke: #faab82 } .local, .alishan, .all_stop { stroke: #00f } .local_express { stroke: #00a6ff } .fu_hsing { stroke: #00bfff } .ordinary, .theme { stroke: #006055 } .special { stroke: #ff1493; } .others { stroke: grey; } /* 即時列車位置點 */ .taroko_mark { fill: #20b2aa } .puyuma_mark { fill: red } .tze_chiang_mark { fill: orange } .tze_chiang_diesel_mark { fill: gold } .emu1200_mark { fill: #ff008c } .emu300_mark { fill: #f44 } .emu3000_mark { fill: #000 } .chu_kuang_mark { fill: #faab82 } .local_mark { fill: #00f } .local_express_mark { fill: #00a6ff } .fu_hsing_mark { fill: #00bfff } .ordinary_mark { fill: #006055 } .special_mark { fill: #ff1493 } .others_mark { fill: grey; }</style>')
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
        self.fileHandler.write( '<text><textPath class = "' + _class + '" startOffset = "' + _startOffset + '" href = "#' +
                                _line_id + '"><tspan dy="-3" font-size="80%">' + _train_id + '</tspan></textPath></text>' )

    # 繪製基底圖
    def _draw_background(self):
        localtime = time.asctime(time.localtime(time.time()))

        self._add_text("5", "20",
                       '{0} 日期：{1}，運行圖均來自台鐵公開資料所分析，僅供參考，正確資料與實際運轉狀況請以台鐵網站或公告為主。台鐵JSON Open Data轉檔運行圖程式版本：{2} 轉檔時間：{3}'.format(Globals.OperationLines[self.line]['NAME'], self.date, Globals.Version, localtime),
                       "#000000", None, None)
        # 時間線
        hours = self.diagram_hours
        text_spacing_factor = 500
        # after_midnight = ""

        # 小時
        for i in range(0, len(hours)):
            x = 50 + i * 1200            
            y = 0
            self._add_line(str(x), "50", str(x), str(self.height + 50), None, "hour_line")

            while True:     
                if (hours[i] == 24):
                    after_midnight = "隔日"
                    css = "hour_midnight"
                else:
                    after_midnight = ""
                    css = "hour"

                if y <= self.height:
                    self._add_text(str(x), str(49 + y), "{0:0>2d}00 {1}".format(hours[i], after_midnight), None, css)
                else:
                    break
                y += text_spacing_factor

            if i != len(hours) - 1:  # 每10分鐘
                for j in range(0, 5):
                    x = 50 + i * 1200 + (j + 1) * 200
                    if j != 2:
                        self._add_line(str(x), "50", str(x), str(self.height + 50), None, "min10_line")
                    else:  # 30分鐘顏色不同
                        self._add_line(str(x), "50", str(x), str(self.height + 50), None, "min30_line")
                    y = 0
                    while True:                               
                        if y <= self.height:
                            if j != 2:
                                self._add_text(str(x), str(49 + y), str(j + 1) + "0", None, "min10", None)
                            else:
                                self._add_text(str(x), str(49 + y), str(j + 1) + "0", None, "min30", None)
                        else:
                            break
                        y += text_spacing_factor

        # 車站線
        for item in self.stations_to_draw:
            y = float(item['SVGYAXIS']) + 50
            if item['ID'] != 'NA':
                self._add_line("50", str(y), str(self.width - 50), str(y), None, "station_line")
            else:
                self._add_line("50", str(y), str(self.width - 50), str(y), None, "station_noserv_line")
            for i in range(0, 31):
                if item['ID']  != 'NA':
                    self._add_text(str(5 + i * 1200), str(y - 5), item['DSC'], "#000000", None, None)
                else:
                    self._add_text(str(5 + i * 1200), str(y - 5), item['DSC'], "#c2c2a3", None, None)

    # 繪製線條
    def draw_line(self, train_id, path, text_position, color):

        # if option_id is None:
        #     line_id = train_id
        # elif option_id is not None:
        #     line_id = "{0}-{1}".format(train_id, option_id)

        if path != 'M':  # 避免無資料
            self._add_path(path, train_id, None, color, None)
            for item in text_position:
                self._add_path_text(train_id, train_id, color, str(item))
            # for i in range(0, 5):
            #     self._add_path_text(train_id, train_id, color, str(20 * i) + "%")

    # 存檔
    def save_file(self):

        self.fileHandler.write('</svg>')
        self.fileHandler.close()

        return '{0} 日期：{1} 運行圖繪製完成 \n'.format(Globals.OperationLines[self.line]['NAME'], self.date)
    