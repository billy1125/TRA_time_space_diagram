# 運行圖SVG繪製
# 部分程式碼為 nedwu (https://github.com/nedwu) 所啟發，並且參考其專案部分程式碼 (https://github.com/nedwu/TRAOpenDataDiagramer)。

import csv
import time
import pandas as pd # 引用套件並縮寫為 pd
import numpy as np
from progessbar import progress

dict_car_kind = {
    '1131': 'local',
    '1132': 'local',
    '1100': 'tze_chiang_diesel',
    '1101': 'tze_chiang',
    '1102': 'taroko',
    '1103': 'tze_chiang_diesel',
    '1107': 'puyuma',
    '1108': 'tze_chiang',
    '1109': 'tze_chiang',
    '110A': 'tze_chiang',
    '110B': 'emu1200',
    '110C': 'emu300',
    '110D': 'tze_chiang_diesel',
    '110E': 'tze_chiang_diesel',
    '110F': 'tze_chiang_diesel',
    '1110': 'chu_kuang',
    '1111': 'chu_kuang',
    '1114': 'chu_kuang',
    '1115': 'chu_kuang',
    '1120': 'fu_hsing',
    '1140': 'ordinary',
    '0000': 'special'
    }

dict_line_kind = {
    'LINE_WN': '西部幹線北段（基隆-竹南）',
    'LINE_WM': '西部幹線台中線（竹南-彰化，經苗栗）',
    'LINE_WSEA': '西部幹線海岸線（竹南-彰化，經大甲）',
    'LINE_WS': '西部幹線南段（彰化-高雄）',
    'LINE_P': '屏東線（高雄-枋寮）',
    'LINE_S': '南迴線（枋寮-台東）',
    'LINE_T': '台東線（花蓮-台東）',
    'LINE_N': '北迴線（蘇澳新-花蓮）',
    'LINE_I': '宜蘭線（八堵-蘇澳）',
    'LINE_PX': '平溪深澳線（八斗子-菁桐）',
    'LINE_NW': '內灣線（新竹-內灣）',
    'LINE_J': '集集線（二水-車埕）',
    'LINE_SL': '沙崙線（中洲-沙崙',
}

lines = ['LINE_WN', 'LINE_WM', 'LINE_WSEA', 'LINE_WS', 'LINE_P', 'LINE_S', 'LINE_T', 'LINE_N', 'LINE_I', 'LINE_PX', 'LINE_NW', 'LINE_J', 'LINE_SL']
lines_stations = {}  # 各營運路線車站於運行圖中的位置，用於運行線的繪製
lines_stations_for_background = {}  # 各營運路線車站於運行圖中的位置，包含廢站、號誌站等車站

# 處理所有車站基本資訊(Category.csv)
with open('CSV/Category.csv', newline='', encoding='utf8') as csvfile:
    reader = csv.DictReader(csvfile)
    list_csv = []

    for row in reader:
        list_csv.append([row['KIND'], row['ID'], row['DSC'], row['EXTRA1']])

    for line in lines:
        stations_loc = {}
        stations_loc_for_background = []
        log = 0
        for kind, id, dsc, extra1 in list_csv:
            log += 1
            if line == kind:
                if id != 'NA':
                    stations_loc[id] = [float(extra1), dsc]
                stations_loc_for_background.append([kind, id, dsc, extra1])

            lines_stations[line] = stations_loc
            lines_stations_for_background[line] = stations_loc_for_background


class TimeSpaceDiagram:

    def __init__(self, lines_diagram_setting, all_trains, location, date, version):

        self.location = location
        self.date = date

        self.stations_to_draw = []
        self.stations_loc = {}

        self.diagrams = {}

        count = 0
        total = len(all_trains)

        for key, value in lines_diagram_setting.items():
            self.diagrams[key] = DiagramObject(lines_stations_for_background[key], self.location + value[0], date, value[1], 18100, value[2], version)

        # 繪製各車次線
        for train_id, car_class, line, over_night_stn, train_time_space in all_trains:

            count += 1
            progress(count, total, "目前製作車次：" + train_id)

            self.draw_train(train_id, car_class, line, train_time_space, self.diagrams)

        for key, value in self.diagrams.items():
            value.save_file()

    # 繪製車次線
    def draw_train(self, train_id, car_class, line, train_time_space, diagrams):

        color = dict_car_kind.get(car_class, 'ordinary')
        dict_filtered_stations = {}
        list_station_record = []

        for item in lines:
            dict_filtered_stations[item] = []

        for index, row in train_time_space.iterrows():
            for key, value in lines_stations.items():
                    if row['Station ID'] in value:
                        list_station_record.append(row['Station ID'])
                        temp = dict_filtered_stations[key]
                        temp.append([row['Station ID'], row['Time'], value[row['Station ID']][0]])
                        dict_filtered_stations[key] = temp

        for key, value in dict_filtered_stations.items():

            # 處理山海線，如果只有通過彰化與竹南車站，則該路線不繪製
            check_stations = False
            if (key == "LINE_WSEA" or key == "LINE_WM") and len(value) <= 4:
                for item in value:
                    if item[0] != '1028' or item[0] != '1120':
                        check_stations = True

            if len(value) > 2 and check_stations != True:
                path = "M"
                for station_id, time, loc in value:
                    # if station_id == "-1":
                    #     # 跨午夜前最後一段繪製
                    #     x = round(14450, 4)
                    #     y = round(midnight_loc + 50, 4)
                    #     path += str(x) + ',' + str(y) + ' '
                    #     break
                    # else:
                    x = round(time * 10 + 50, 4)
                    y = round(loc + 50, 4)
                    path += str(x) + ',' + str(y) + ' '

                diagrams[key].draw_line(train_id, path, color, '')


class DiagramObject:

    def __init__(self, stations_to_draw, location, date, line, width, height, version):

        self.file_name = location + date + '.svg'
        self.date = date
        self.line = line
        self.width = width
        self.height = height
        self.stations_to_draw = stations_to_draw

        # svg檔案描述、背景、基本大小基本設定
        self.fileHandler = open(self.file_name, 'w', encoding='utf-8')
        self.fileHandler.write('<?xml version="1.0" encoding="utf-8" ?>')
        self.fileHandler.write(
            '<?xml-stylesheet href="style.css" type="text/css" title="sometext" alternate="no" media="screen"?>')
        self.fileHandler.write(
            '<svg baseProfile="full" xmlns="http://www.w3.org/2000/svg" xmlns:ev="http://www.w3.org/2001/xml-events" xml'
            'ns:xlink="http://www.w3.org/1999/xlink" style="font-family:Tahoma" width="' + str(self.width) + '" height="' + str(self.height + 100) + '" version="1.1"><defs />')

        self.draw_background(version)

    def add_text(self, x, y, string, _color = None, _class = None, transform = None):

        transformStr = ''

        if transform is not None :
            transformStr = ' transform="' + transform + '"'
        if _class is not None :
            self.fileHandler.write( '<text class="' + _class + '" x="' + x + '" y="' + y + '"' + transformStr + '>' + string + '</text>' )
        elif _color is not None :
            self.fileHandler.write( '<text fill="' + _color + '" x="' + x + '" y="' + y + '"' + transformStr + '>' + string + '</text>' )
        else :
            self.fileHandler.write( '<text x="' + x + '" y="' + y + '"' + transformStr + '>' + string + '</text>' )

    def add_line( self, x1, y1, x2, y2, _color = None, _class = None ) :

        if _class is not None :
            self.fileHandler.write( '<line class="' + _class + '" x1="' + x1 + '" x2="' + x2 + '" y1="' + y1 + '" y2="' + y2 + '" />' )
        elif _color is not None :
            self.fileHandler.write( '<line stroke="' + _color + '" x1="' + x1 + '" x2="' + x2 + '" y1="' + y1 + '" y2="' + y2 + '" />' )
        else :
            self.fileHandler.write( '<line x1="' + x1 + '" x2="' + x2 + '" y1="' + y1 + '" y2="' + y2 + '" />' )

    def add_path( self, pathList, lineId, _color = None, _class = None, _emphasis = False ) :

        emphasisStr = '" style="stroke-width: 4" />' if _emphasis else '" />'

        if _class is not None :
            self.fileHandler.write( '<path class="' + _class + '" d="' + pathList + '" id="' + lineId + emphasisStr )
        elif _color is not None :
            self.fileHandler.write( '<path stroke="' + _color + '" d="' + pathList + '" id="' + lineId + emphasisStr )
        else :
            self.fileHandler.write( '<path d="' + pathList + '" id="' + lineId + emphasisStr )

    def add_path_text(self, _line_id, _train_id, _class, _startOffset):
        self.fileHandler.write( '<text><textPath class = "' + _class + '" startOffset = "' + _startOffset + '" xlink:href = "#' +
                                _train_id + '">' + _train_id + '</textPath></text>' )

    # 繪製基底圖
    def draw_background(self, version):
        localtime = time.asctime(time.localtime(time.time()))

        self.add_text("5", "20", dict_line_kind[self.line] + ' 日期：' + self.date +'，運行圖均來自台鐵公開資料所分析，僅供參考，正確資料與實際運轉狀況請以台鐵網站或公告為主。台鐵JSON Open Data轉檔運行圖程式版本：' + version + ' 轉檔時間：' + localtime, "#000000", None, None)

        # 時間線

        # 小時
        for i in range(0, 31):
            x = 50 + i * 600
            self.add_line(str(x), "50", str(x), str(self.height + 50), None, "hour_line")

            if i > 24:
                hour_text = i - 24
            else:
                hour_text = i

            for j in range(0, 11):
                self.add_text(str(x), str(49 + j * 300), '{:0>2d}'.format(hour_text) + '00', "#999966")

            # 每10分鐘
            if i != 30:
                for j in range(0, 5):
                    x = 50 + i * 600 + (j + 1) * 100
                    if j != 2:
                        self.add_line(str(x), "50", str(x), str(self.height + 50), None, "min10_line")
                    else:  # 30分鐘顏色不同
                        self.add_line(str(x), "50", str(x), str(self.height + 50), None, "min30_line")
                        for k in range(0, 11):
                            self.add_text(str(x), str(49 + k * 300), "30", "#999966", None, None)

        # 車站線
        for LineName, StationNumber, StationName, StationLoc in self.stations_to_draw:
            y = float(StationLoc) + 50
            if StationNumber != 'NA':
                self.add_line("50", str(y), str(self.width - 50), str(y), None, "station_line")
            else:
                self.add_line("50", str(y), str(self.width - 50), str(y), None, "station_noserv_line")
            for i in range(0, 31):
                if StationNumber != 'NA':
                    self.add_text(str(5 + i * 600), str(y - 5), StationName, "#000000", None, None)
                else:
                    self.add_text(str(5 + i * 600), str(y - 5), StationName, "#bfbfbf", None, None)

    # 繪製線條
    def draw_line(self, train_id, path, color, midnight_id):
        # print(path)
        line_id = ''
        # # 如果跨午夜車次，車次線ID修改，避免跨午夜車次線無車次號的問題
        # if midnight_id == '':
        #     line_id = train_id
        # elif midnight_id != '':
        #     line_id = midnight_id

        if path != 'M':  # 避免無資料
            self.add_path(path, train_id, None, color, None)
            for i in range(0, 6):
                self.add_path_text(line_id, train_id, color, str(50 + 600 * i))

    # 存檔
    def save_file(self):

        self.fileHandler.write('</svg>')
        self.fileHandler.close()

        return dict_line_kind[self.line] + ' 日期：' + self.date + ' 運行圖繪製完成 \n'
