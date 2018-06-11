#運行圖SVG繪製
import csv
import svgwrite
import time
import pandas as pd # 引用套件並縮寫為 pd
import numpy as np

# dwg = None
# stations_to_draw = []
# stations_loc = {}

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

class Draw:
    def __init__(self, location, date, line, version, height):
        self.location = location
        self.date = date

        filename = ''
        if location == '':
            filename = 'OUTPUT/' + line + '_' + date + '.svg'
        else:
            filename = location + date + '.svg'
        self.file_name = filename
        self.line = line
        

        self.dwg = None
        self.stations_to_draw = []
        self.stations_loc = {}

        self.height = height

        #背景、基本大小
        self.dwg = svgwrite.Drawing(self.file_name, size = (14500, self.height + 100), profile='full', style='background:#b3fff0;font-family:Tahoma')
        self.dwg.add_stylesheet('style.css', title="sometext") 
        #處理所有車站基本資訊(Category.csv)
        with open('CSV/Category.csv', newline='', encoding='utf8') as csvfile:
            
            reader = csv.reader(csvfile)
            
            for row in reader:
                if row[0] == self.line:
                    self.stations_to_draw.append(row)
                    if row[1] != 'NA':
                        self.stations_loc[row[1]] = float(row[3])

        self.draw_background(version)

    #繪製基底圖
    def draw_background(self, version):
        localtime = time.asctime(time.localtime(time.time()))

        self.dwg.add(self.dwg.text(dict_line_kind[self.line] + ' 日期：' + self.date +'，運行圖均來自台鐵公開資料所分析，僅供參考，正確資料與實際運轉狀況請以台鐵網站或公告為主。台鐵JSON Open Data轉檔運行圖程式版本：' + version + ' 轉檔時間：' + localtime, insert=(5, 20), fill='#000000'))

        #時間線

        #小時
        for i in range(0, 25):
            x = 50 + i * 600
            self.dwg.add(self.dwg.line((x, 50), (x, self.height + 50), class_='hour_line'))
            for j in range(0, 11):
                self.dwg.add(self.dwg.text('{:0>2d}'.format(i) + '00', insert=(x, 49 + j * 300), fill='#999966'))
            #每10分鐘
            if i != 24:
                for j in range(0, 5):
                    x = 50 + i * 600 + (j + 1) * 100
                    if j != 2:
                        self.dwg.add(self.dwg.line((x, 50), (x, self.height + 50), class_='min10_line'))
                    else: #30分鐘顏色不同
                        self.dwg.add(self.dwg.line((x, 50), (x, self.height + 50), class_='min30_line'))
                        for k in range(0, 11):
                            self.dwg.add(self.dwg.text('30', insert=(x, 49 + k * 300), fill='#999966'))

        #車站線
        #dwg.add(dwg.line((50, 50), (14450, 50), style=style_01))

        for item in self.stations_to_draw:
            y = float(item[3]) + 50
            if item[1] != 'NA':
                self.dwg.add(self.dwg.line((50, y), (14450, y), class_='station_line'))
            else:
                self.dwg.add(self.dwg.line((50, y), (14450, y), class_='station_noserv_line'))
                
            for i in range(0, 25):
                if item[1] != 'NA':
                    self.dwg.add(self.dwg.text(item[2], insert=(5 + i * 600, y - 5), fill='#000000'))
                else:
                    self.dwg.add(self.dwg.text(item[2], insert=(5 + i * 600, y - 5), fill='#bfbfbf'))

        

    #繪製車次線
    def draw_trains(self, train_time_space, train_id, car_class, line):
        
        to_count_stations = True
        check_number = 0
        midnight = -1
        color = dict_car_kind[car_class]
        midnight_loc = -1
        cheng_zhui_passing = {'1321': 0, '1118': 0}
        cheng_zhui_local = False

        #成追線處理（使用負面表列的方式）
        if self.line == 'LINE_WM' and line == '2': #繪製山線，有標示海線的車次
            to_count_stations = False
        if self.line == 'LINE_WSEA' and line == '1': #繪製海線，有標示山線的車次
            to_count_stations = False

        if to_count_stations == True:
            for i in range(0, len(train_time_space.index)):
                if self.stations_loc.__contains__(train_time_space.iloc[i, 1]):
                    check_number += 1 #確認資料有超過兩筆
                if train_time_space.iloc[i, 1] == '-1' and train_time_space.iloc[i + 1, 1] == '-1':
                    midnight = i #找出跨午夜車次點
                if self.line == 'LINE_WM': #判斷是不是有通過成功與追分
                    if train_time_space.iloc[i, 1] == '1321': #成功
                        cheng_zhui_passing['1321'] = i
                    elif train_time_space.iloc[i, 1] == '1118': #追分
                        cheng_zhui_passing['1118'] = i

        if cheng_zhui_passing['1321'] != 0 and cheng_zhui_passing['1118'] != 0:
            cheng_zhui_local = True 
        
        if cheng_zhui_local == False:
            #處理跨午夜車次，推算跨午夜時的列車位置
            if self.stations_loc.__contains__(train_time_space.iloc[midnight - 1, 1]) and self.stations_loc.__contains__(train_time_space.iloc[midnight + 2, 1]):
                midnight_loc = self.midnight_train_loc(train_time_space, midnight)
                
            if check_number > 2: #資料超過兩筆才繪製，避免只有顯示起點終點車站的車次被繪入
                path = 'M'
                i = 0
                while True:
                    if self.stations_loc.__contains__(train_time_space.iloc[i, 1]):
                        x = round(train_time_space.iloc[i, 2] * 10 + 50, 4)
                        y = round(self.stations_loc[train_time_space.iloc[i, 1]] + 50, 4)
                        path += str(x) + ',' + str(y) + ' '
                        
                    i += 1

                    if i == len(train_time_space.index):
                        break

                    if i == midnight and midnight_loc != -1:
                        #跨午夜前最後一段繪製
                        x = round(14450, 4)
                        y = round(midnight_loc + 50, 4)
                        path += str(x) + ',' + str(y) + ' '
                        break
                
                self.draw_line(train_id, path, color, '')

                if midnight != -1 and midnight_loc != -1: #車站內跨午夜車次處理，跨午夜車次要分成兩段繪製
                    path = 'M'
                    #跨午夜後第一段繪製
                    x = round(50, 4)
                    y = round(midnight_loc + 50, 4)
                    path += str(x) + ',' + str(y) + ' '

                    i = midnight + 1
                    while True:
                        if self.stations_loc.__contains__(train_time_space.iloc[i, 1]):
                            x = round(train_time_space.iloc[i, 2] * 10 + 50, 4)
                            y = round(self.stations_loc[train_time_space.iloc[i, 1]] + 50, 4)
                            path += str(x) + ',' + str(y) + ' '
                        
                        i += 1
                        if i == len(train_time_space.index):
                            break
                        if i == midnight:
                            break
                
                    self.draw_line(train_id, path, color, train_id + '_01')

        elif cheng_zhui_local == True:
            path = self.path_cheng_zhui_passing(train_time_space, cheng_zhui_passing, self.line)
            self.draw_line(train_id, path, color, '')

    #處理跨午夜車次，推算跨午夜時的列車位置
    def midnight_train_loc(self, train_time_space, midnight):
        loc = []
        time = []
        
        loc.append(self.stations_loc[train_time_space.iloc[midnight - 1, 1]])
        loc.append(np.NaN)
        loc.append(self.stations_loc[train_time_space.iloc[midnight + 2, 1]])
        time.append(train_time_space.iloc[midnight - 1, 2])
        time.append(train_time_space.iloc[midnight, 2])
        time.append(train_time_space.iloc[midnight + 2, 2] + 1440)

        dict = {"Time": time, "Loc": loc}
        select_df = pd.DataFrame(dict)
        select_df = select_df.set_index('Time').interpolate(method='index') #估計通過時間

        return select_df.iloc[1, 0]

    #成追線區間車處理
    def path_cheng_zhui_passing(self, train_time_space, cheng_zhui_passing, line):
        line_dir = cheng_zhui_passing['1321'] - cheng_zhui_passing['1118']

        path = 'M'
        i = 0
        end = 0

        if line == 'LINE_WM':
            if line_dir > 0:
                i = cheng_zhui_passing['1321']
                end = len(train_time_space.index)
            elif line_dir < 0:
                i = 0
                end = cheng_zhui_passing['1118']
        # elif line == 'LINE_WSEA':
        #     if line_dir > 0:
        #         i = 0
        #         end = cheng_zhui_passing['1118']
        #     elif line_dir < 0:
        #         i = cheng_zhui_passing['1321']
        #         end = len(train_time_space.index)

        while True:
            if self.stations_loc.__contains__(train_time_space.iloc[i, 1]):
                x = round(train_time_space.iloc[i, 2] * 10 + 50, 4)
                y = round(self.stations_loc[train_time_space.iloc[i, 1]] + 50, 4)
                path += str(x) + ',' + str(y) + ' '
                
            i += 1

            if i == end:
                break
        
        return path
    
    #繪製線條
    def draw_line(self, train_id, path, color, midnight_id):
        # print(path)
        line_id = ''
        #如果跨午夜車次，車次線ID修改，避免跨午夜車次線無車次號的問題
        if midnight_id == '':
            line_id = train_id
        elif midnight_id != '':
            line_id = midnight_id
            
        if path != 'M': #避免無資料
            self.dwg.add(self.dwg.path(id = line_id, d = path, class_=color))
            for i in range(0, 6):
                text = self.dwg.add(svgwrite.text.Text(""))
                text.add(svgwrite.text.TextPath(path='#'+line_id, text=train_id, startOffset=50 + 600 * i, method='align', spacing='exact', class_=color))

    #存檔
    def save(self):
        self.dwg.save()
        return dict_line_kind[self.line] + ' 日期：' + self.date + ' 運行圖繪製完成 \n'
