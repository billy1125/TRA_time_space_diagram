# 運行圖SVG繪製
# 部分程式碼為 nedwu (https://github.com/nedwu) 所啟發，並且參考其專案部分程式碼 (https://github.com/nedwu/TRAOpenDataDiagramer)。

import csv
import time

dict_car_kind = {
    '1131': 'local',
    '1132': 'local',
    '1100': 'tze_chiang_diesel',
    '1101': 'taroko',
    '1102': 'taroko',
    '1103': 'tze_chiang_diesel',
    '1105': 'tze_chiang',
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
    '1112': 'chu_kuang',
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

    def __init__(self, lines_diagram_setting, all_trains, location, date, diagram_hours, version):

        self.location = location
        self.date = date
        self.offset = diagram_hours[0] * 600  # 將整個圖形往左移動的距離
        self.stations_to_draw = []
        self.stations_loc = {}

        self.diagrams = {}

        for key, value in lines_diagram_setting.items():
            self.diagrams[key] = self.DiagramObject(lines_stations_for_background[key],
                                                    self.location + value[0],
                                                    date,
                                                    value[1],
                                                    1200 * (len(diagram_hours) - 1) + 100,
                                                    value[2],
                                                    diagram_hours,
                                                    version)

        # 繪製各車次線
        for line_kind, train_id, car_class, line_dir, over_night_stn, option_id, train_time_space in all_trains:
            self.draw_train(line_kind, train_id, car_class, line_dir, option_id, train_time_space, self.diagrams)

        for key, value in self.diagrams.items():
            value.save_file()

    # 繪製車次線
    def draw_train(self, line_kind, train_id, car_class, line_dir, option_id, train_time_space, diagrams):

        color = dict_car_kind.get(car_class, 'ordinary')
        dict_filtered_stations = {}

        for item in lines:
            dict_filtered_stations[item] = []

        path = "M"

        for index, row in train_time_space.iterrows():
            x = round(row['Time'] * 10 + 50 - self.offset, 4)
            y = round(row['Loc'] + 50, 4)
            path += str(x) + ',' + str(y) + ' '

        diagrams[line_kind].draw_line(train_id, path, color, option_id)

    class DiagramObject:

        def __init__(self, stations_to_draw, location, date, line, width, height, diagram_hours, version):

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

            self._draw_background(version)

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
        def _draw_background(self, version):
            localtime = time.asctime(time.localtime(time.time()))

            self._add_text("5", "20", dict_line_kind[self.line] + ' 日期：' + self.date +'，運行圖均來自台鐵公開資料所分析，僅供參考，正確資料與實際運轉狀況請以台鐵網站或公告為主。台鐵JSON Open Data轉檔運行圖程式版本：' + version + ' 轉檔時間：' + localtime, "#000000", None, None)

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

            return dict_line_kind[self.line] + ' 日期：' + self.date + ' 運行圖繪製完成 \n'