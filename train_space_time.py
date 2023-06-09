# 台鐵公開資料(JSON)轉換
# 這個類別主要將台鐵的JSON各車次時刻表，推算通過與停靠所有車站的時間，並且依照順序增加順序碼
# 再轉為車次會在各運行路線的時間與位置資料

import pandas as pd  
import numpy as np

# 自訂class與module
import environment_variable as ev

Globals = ev.GlobalVariables()
Route = Globals.Route                   # 列車路徑基本資料
SVG_X_Axis = Globals.SVG_X_Axis         # 時間空間基本資料
lines_stations = Globals.LinesStations  # 各營運路線車站於運行圖中的位置，用於運行線的繪製

class SpaceTime:           

    def CalculateSpaceTime(self, _train):

        trains_data = []                         # 台鐵各車次時刻表轉換整理後資料
        after_midnight_data = []                 # 跨午夜車次的資料

        train_id = _train['Train']               # 車次代碼
        car_class = _train['CarClass']           # 車種代碼
        line = _train['Line']                    # 山線1、海線2、成追線3，東部幹線則為0
        over_night_stn = _train['OverNightStn']  # 跨午夜車站
        line_dir = _train['LineDir']             # 順行1、逆行2
        
        # 將這個車次表定台鐵時刻表所有「停靠」車站轉出
        timetable = self._find_train_timetable(_train)

        # 查詢車次會「停靠與通過」的所有車站
        passing_stations = self._find_passing_stations(timetable, line, line_dir)

        # 推算車次會通過的所有車站到站與離站時間
        time_space = self._estimate_time_space(timetable, passing_stations, over_night_stn)

        # 將車次通過車站時間轉入各營運路線的資料，設定通過車站的順序碼，並且推算跨午夜車次的距離
        operation_lines = self._time_space_to_operation_lines(time_space)

        # 將車次的各營運線資料整理好之後，增加到trains_data清單中
        for key, value in operation_lines[0].items():
            trains_data.append([key, train_id, car_class, line, over_night_stn, None, value])

        # 將車次跨午夜的各營運線資料整理好之後，增加到after_midnight_data清單中
        for key, value in operation_lines[1].items():
            after_midnight_data.append([key, train_id, car_class, line, over_night_stn, "midnight", value])

        return [trains_data, after_midnight_data]

    # 查詢表定台鐵時刻表所有「停靠」車站，可查詢特定車次
    def _find_train_timetable(self, train_no):
        timetable = {}

        for TimeInfos in train_no['TimeInfos']:
            timetable[TimeInfos['Station']] = [TimeInfos['ARRTime'], TimeInfos['DEPTime'], 
                                               TimeInfos['Station'], TimeInfos['Order']]

        return timetable  # 字典 車站ID: [到站時間, 離站時間, 車站ID, 順序]

    # 查詢車次會「停靠與通過」的所有車站
    def _find_passing_stations(self, dict_start_end_station, line, line_dir):
        # 起終點車站代碼
        end_station_number = len(dict_start_end_station) - 1
        start_station = list(dict_start_end_station)[0]
        end_station = list(dict_start_end_station)[end_station_number]

        # 環島列車處理，例如：52車次
        roundabout_train = False
        if end_station == '1001':
            end_station = start_station
            roundabout_train = True

        # 判斷是不是成追線
        cheng_zhui = self._find_cheng_zhui(line, dict_start_end_station, start_station, end_station)

        # 判斷是不是內灣六家線，目前均為區間車，並且具備六家、竹東二站
        neiwan = False
        if dict_start_end_station.__contains__('1194') or dict_start_end_station.__contains__('1203'):
            neiwan = True

        # 判斷是不是平溪深澳線，目前均為區間車，並且具備十分站，十分車站必經過
        pingxi = False
        if dict_start_end_station.__contains__('7332'):
            pingxi = True

        # 判斷是不是集集線，目前均為區間車，並且具備濁水站或源泉，濁水車站必經過
        jiji = False
        if dict_start_end_station.__contains__('3432') or dict_start_end_station.__contains__('3431'):
            jiji = True

        # 判斷是不是沙崙線，目前均為區間車，並且具備沙崙站，沙崙車站必經過
        shalun = False
        if dict_start_end_station.__contains__('4272'):
            shalun = True

        passing_stations = []
        temp = []
        station = start_station

        km = 0.0  # 計算經過車站里程

        while True:

            temp.append([Route[station][0], Route[station][1], Route[station][3], km])

            if line_dir == '2':  # 逆行

                if cheng_zhui == False:
                    branch = Route[station][6]
                    if branch != '':
                        if station == '7360':  # 平溪深澳線處理，瑞芳判斷
                            if end_station == '7362':
                                km += float(Route[station][12])
                                station = '7361'  # 指定到海科館站
                            elif end_station != '7362':
                                km += float(Route[station][10])
                                station = Route[station][4]
                        elif station == '3430':  # 集集線處理，二水判斷
                            if jiji == True:
                                km += float(Route[station][12])
                                station = '3431'
                            elif jiji == False:
                                km += float(Route[station][10])
                                station = Route[station][4]
                        elif station == '4270':  # 沙崙線處理，中洲判斷
                            if shalun == True:
                                km += float(Route[station][12])
                                station = '4271'
                            elif shalun == False:
                                km += float(Route[station][10])
                                station = Route[station][4]
                        else:
                            # 山海線判斷
                            if line in ['1', '0']:  # 山線與其他
                                km += float(Route[station][10])
                                station = Route[station][4]
                            elif line == '2':  # 海線
                                km += float(Route[station][12])
                                station = Route[station][6]
                    else:
                        km += float(Route[station][10])
                        station = Route[station][4]
                else:  # 成追線
                    km += float(Route[station][14])
                    station = Route[station][8]

            elif line_dir == '1':  # 順行

                if cheng_zhui == False:
                    branch = Route[station][7]
                    if branch != '':
                        if station == '0920':  # 八堵判斷
                            if end_station != '0900':  # 終點站非基隆的車次下一車站直接指定為暖暖
                                km += float(Route[station][13])
                                station = Route[station][7]
                            elif end_station == '0900':  # 終點站為基隆的車次
                                km += float(Route[station][11])
                                station = Route[station][5]
                        elif station == '7130':  # 蘇澳新判斷
                            if end_station == '7120':  # 終點站為蘇澳
                                km += float(Route[station][13])
                                station = '7120'
                            elif end_station != '7120':  # 終點站非蘇澳的車次下一車站直接指定為永樂
                                km += float(Route[station][11])
                                station = '7110'
                        elif station in ['1190', '1193']:  # 內灣六家線處理，北新竹與竹中判斷
                            if neiwan == True:  # 終點站為六家或內灣
                                km += float(Route[station][13])
                                if station == '1190':
                                    station = '1191'
                                elif station == '1193':
                                    if end_station in ['1208', '1203']:  # 若終點站為竹東或內灣，下一站指定為上員(偷懶的方式)
                                        station = '1201'
                                    elif end_station == '1194':
                                        station = '1194'
                            elif neiwan == False:  # 終點站非六家或內灣的車次下一車站直接指定為竹北
                                km += float(Route[station][11])
                                station = '1180'
                        elif station == '7330':  # 平溪深澳線處理，三貂嶺判斷
                            if pingxi == True:
                                km += float(Route[station][13])
                                station = '7331'
                            elif pingxi == False:  # 終點站非平溪深澳線的車次下一車站直接指定為牡丹
                                km += float(Route[station][11])
                                station = '7320'
                        else:  # 山海線判斷
                            if line in ['1', '0']:  # 山線或其他
                                km += float(Route[station][11])
                                station = Route[station][5]
                            elif line == '2':  # 海線
                                km += float(Route[station][13])
                                station = Route[station][7]
                    else:
                        # if station != '2214':
                        km += float(Route[station][11])
                        station = Route[station][5]
                else:  # 成追線
                    km += float(Route[station][15])
                    station = Route[station][9]

            if station == end_station:
                if roundabout_train == True:
                    temp.append(['1001', Route[station][1], Route[station][3], km])
                    break
                else:
                    temp.append([Route[station][0], Route[station][1], Route[station][3], km])
                    break

            if len(temp) > 200:
                ## print(len(temp))
                break

        passing_stations = temp

        return passing_stations  # 清單: [車站ID, 車站名稱, 里程位置, 與下一站相差公里數], 清單: 屬於哪一個支線


    # 判斷成追線車次
    def _find_cheng_zhui(self, line, list_start_end_station, start_station, end_station):
        result = False

        if (line == "3"):
            result = True
        elif list_start_end_station.__contains__('2260') and list_start_end_station.__contains__('3350'):  # 區間車，具備成功、追分二站
            result = True
        # elif (start_station in Station_SEA and end_station in Station_MOUNTAIN) or (
        #         start_station in Station_MOUNTAIN and end_station in Station_SEA):  # 區間快，起訖車站為山海線兩端車站(暫時保留)
        #     result = True

        return result


    # 推算車次會通過的所有車站到站與離站時間
    def _estimate_time_space(self, dict_start_end_station, list_passing_stations, over_night_stn):

        station = []
        station_id = []
        time = []
        loc = []
        stop_station_order = []
        is_roundabout_train = False

        # 判斷是不是環島車次
        if list_passing_stations[len(list_passing_stations) - 1][0] == "1001":
            is_roundabout_train = True

        # 將通過車站資料逐一轉成 dataframe
        for StationId, StationName, LocationKM, KM in list_passing_stations:
            if dict_start_end_station.__contains__(StationId):

                ARRTime = float(SVG_X_Axis[dict_start_end_station[StationId][0]])
                DEPTime = float(SVG_X_Axis[dict_start_end_station[StationId][1]])
                Order = int(dict_start_end_station[StationId][3])

                station_id.append(StationId)
                station.append(StationName)
                loc.append(float(KM))
                time.append(ARRTime)
                stop_station_order.append(Order)
 
                station_id.append(StationId)
                station.append(StationName)
                loc.append(float(KM))
                time.append(DEPTime)
                stop_station_order.append(Order)

            else:  # 通過不停靠之車站處理

                station_id.append(StationId)
                station.append(StationName)
                loc.append(float(KM))
                time.append(np.NaN)
                stop_station_order.append(-1)

        dict_temp = {"Station": station, "Time": time, "Loc": loc, "StationID": station_id, "StopStation": stop_station_order}
        select_df = pd.DataFrame(dict_temp)

        # 如果是環島車次，將原來終點站台北車站的代碼改為1000
        if is_roundabout_train == True:
            row_index = select_df[select_df['StationID'] == "1001"].index
            for item in row_index:
                select_df.at[item, 'StationID'] = "1000"

        # 跨午夜車次處理：將超過午夜的時間一律加上 2880
        row_index = select_df[select_df['StationID'] == over_night_stn].index
        if (len(row_index) > 0):
            for index, row in select_df.iterrows():
                if np.isnan(row['Time']) == False:
                    if index >= row_index[0]:
                        select_df.loc[index, "Time"] = row['Time'] + 2880

        # select_df.set_index('Loc', inplace=True)
        # select_df.interpolate(method='index' , inplace=True)
        select_df.interpolate(method='linear' , inplace=True)
        select_df.reset_index()

        return select_df
      
    # 將車次通過車站時間轉入各營運路線的資料，設定通過車站的順序碼，並且推算跨午夜車次的距離
    def _time_space_to_operation_lines(self, select_df):
        stop_order = 0
        operation_lines = {}
        after_midnight_train = {}

        for key, value in lines_stations.items():
            operation_lines[key] = [[], [], [], [], [], []]
        for index, row in select_df.iterrows():
            for key, value in lines_stations.items():
                if row['StationID'] in value:
                    operation_lines[key][0].append(row['Station'])
                    operation_lines[key][1].append(row['StationID'])
                    operation_lines[key][2].append(row['Time'])
                    operation_lines[key][3].append(float(value[row['StationID']][0]))
                    operation_lines[key][4].append(row['StopStation'])
                    operation_lines[key][5].append(stop_order)
            stop_order += 1

        for key, value in operation_lines.items():
            dict_temp = {"Station": value[0], "StationID": value[1], "Time": value[2], "Loc": value[3], "StopStation": value[4], "StopOrder": value[5]}
            select_df = pd.DataFrame(dict_temp)
            operation_lines[key] = select_df

        # 資料刪減整理，如果營運路線沒有資料就移除
        drop_key = []
        for key, value in operation_lines.items():
            if value.shape[0] == 0: # 資料不足者直接刪除
                drop_key.append(key)

                # 將未通過山海線（竹南、彰化二車站順序為相連）車次的營運路線刪除(可能可以移除)
                index_temp = value[(value.StationID == '3360') | (value.StationID == '1250')].index.tolist()
                if index_temp == [0, 1, 2] or index_temp == [0, 1, 2, 3]:
                    drop_key.append(key)

        for item in drop_key:
            operation_lines.pop(item)

        # 跨午夜車次處理：首先插入一個虛擬跨午夜車站，推算運行圖SVG Y軸數值，再獨立午夜後的運行資料存入after_midnight_train
        for key, value in operation_lines.items():
            index_label = value.query('Time >= 2880').index.tolist()
            if len(index_label) >= 2:
                row_value = ['跨午夜', "-1", 2880, np.NaN, "Y", value.loc[index_label[0], 'StopOrder'] - 1]
                select_df = self._insert_row(index_label[0], value, row_value)  # 插入一個虛擬的跨午夜車站

                select_df = select_df.set_index('Time').interpolate(method='index')  # 依據時間估計跨午夜的位置
                select_df = select_df.reset_index()

                df_after_midnight_train = select_df[index_label[0]:].copy()
                df_after_midnight_train.loc[:, 'Time'] = df_after_midnight_train.loc[:, 'Time'].apply(lambda x : x - 2880) # 每一個時間資料都減2880

                after_midnight_train[key] = df_after_midnight_train

        return operation_lines, after_midnight_train  # 本日車次運行資料, 跨午夜車次午夜後的運行資料


    # 在 dataframe 插入一列，參考自：https://www.geeksforgeeks.org/insert-row-at-given-position-in-pandas-dataframe/
    def _insert_row(self, row_number, df, row_value):
        df1 = df[0:row_number].copy()
        df2 = df[row_number:]

        df1.loc[row_number] = row_value
        df_result = pd.concat([df1, df2])

        df_result.index = [*range(df_result.shape[0])]

        return df_result

# 山海線車站，去除竹南與彰化，用於檢查是否是成追線車次(暫時保留)
# Station_SEA = []
# Station_MOUNTAIN = []

# for item in statons:
#     if item[0] == 'LINE_WSEA':
#         if item[1] not in ["1250", "3360"]:
#             Station_SEA.append(item[1])
#     if item[0] == 'LINE_WM':
#         if item[1] not in ["1250", "3360"]:
#             Station_MOUNTAIN.append(item[1])
