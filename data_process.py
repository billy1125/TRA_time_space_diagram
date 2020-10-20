import pandas as pd  # 引用套件並縮寫為 pd
import numpy as np

# 自訂class與module
import basic_data

GlobalVariables = basic_data.GlobalVariables()

# 處理所有車站基本資訊(Stations.csv)
stations = GlobalVariables.Stations

# 時間轉換(Locate.csv)
time_loc = GlobalVariables.TimeLocation

# 類別資料檔(Category.csv)
category = GlobalVariables.Category

# 各營運路線車站於運行圖中的位置，用於運行線的繪製
lines_stations = GlobalVariables.LinesStations

# 山海線車站，去除竹南與彰化，用於檢查是否是成追線車次
Station_SEA = []
Station_MOUNTAIN = []

for item in category:
    if item[0] == 'LINE_WSEA':
        if item[1] not in ["1250", "3360"]:
            Station_SEA.append(item[1])
    if item[0] == 'LINE_WM':
        if item[1] not in ["1250", "3360"]:
            Station_MOUNTAIN.append(item[1])


# 找出每一個車次的表定經過車站
def find_train_stations(train_no):
    dict_start_end_station = {}

    for TimeInfos in train_no['TimeInfos']:
        if TimeInfos['Station'] not in dict_start_end_station:
            dict_start_end_station[TimeInfos['Station']] = [TimeInfos['ARRTime'], TimeInfos['DEPTime'],
                                                            TimeInfos['Station'], TimeInfos['Order']]

    return dict_start_end_station  # 字典 車站ID: [到站時間, 離站時間, 車站ID, 順序]


# 找出每一個車次所有會經過的車站，無論是否會停靠
def find_passing_stations(dict_start_end_station, line, line_dir):
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
    cheng_zhui = _find_cheng_zhui(dict_start_end_station, start_station, end_station)

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

    global stations

    list_passing_stations = []
    temp = []
    station = start_station

    km = 0.0  # 計算經過車站里程

    while True:

        temp.append([stations[station][0], stations[station][1], stations[station][3], km])

        if line_dir == '2':  # 逆行

            if cheng_zhui == False:
                branch = stations[station][6]
                if branch != '':
                    if station == '7360':  # 平溪深澳線處理，瑞芳判斷
                        if end_station == '7362':
                            km += float(stations[station][12])
                            station = '7361'  # 指定到海科館站
                        elif end_station != '7362':
                            km += float(stations[station][10])
                            station = stations[station][4]
                    elif station == '3430':  # 集集線處理，二水判斷
                        if jiji == True:
                            km += float(stations[station][12])
                            station = '3431'
                        elif jiji == False:
                            km += float(stations[station][10])
                            station = stations[station][4]
                    elif station == '4270':  # 沙崙線處理，中洲判斷
                        if shalun == True:
                            km += float(stations[station][12])
                            station = '4271'
                        elif shalun == False:
                            km += float(stations[station][10])
                            station = stations[station][4]
                    else:
                        # 山海線判斷
                        if line in ['1', '0']:  # 山線與其他
                            km += float(stations[station][10])
                            station = stations[station][4]
                        elif line == '2':  # 海線
                            km += float(stations[station][12])
                            station = stations[station][6]
                else:
                    km += float(stations[station][10])
                    station = stations[station][4]
            else:  # 成追線
                km += float(stations[station][14])
                station = stations[station][8]

        elif line_dir == '1':  # 順行

            if cheng_zhui == False:
                branch = stations[station][7]
                if branch != '':
                    if station == '0920':  # 八堵判斷
                        if end_station != '0900':  # 終點站非基隆的車次下一車站直接指定為暖暖
                            km += float(stations[station][13])
                            station = stations[station][7]
                        elif end_station == '0900':  # 終點站為基隆的車次
                            km += float(stations[station][11])
                            station = stations[station][5]
                    elif station == '7130':  # 蘇澳新判斷
                        if end_station == '7120':  # 終點站為蘇澳
                            km += float(stations[station][13])
                            station = '7120'
                        elif end_station != '7120':  # 終點站非蘇澳的車次下一車站直接指定為永樂
                            km += float(stations[station][11])
                            station = '7110'
                    elif station in ['1190', '1193']:  # 內灣六家線處理，北新竹與竹中判斷
                        if neiwan == True:  # 終點站為六家或內灣
                            km += float(stations[station][13])
                            if station == '1190':
                                station = '1191'
                            elif station == '1193':
                                if end_station in ['1208', '1203']:  # 若終點站為竹東或內灣，下一站指定為上員(偷懶的方式)
                                    station = '1201'
                                elif end_station == '1194':
                                    station = '1194'
                        elif neiwan == False:  # 終點站非六家或內灣的車次下一車站直接指定為竹北
                            km += float(stations[station][11])
                            station = '1180'
                    elif station == '7330':  # 平溪深澳線處理，三貂嶺判斷
                        if pingxi == True:
                            km += float(stations[station][13])
                            station = '7331'
                        elif pingxi == False:  # 終點站非平溪深澳線的車次下一車站直接指定為牡丹
                            km += float(stations[station][11])
                            station = '7320'
                    else:  # 山海線判斷
                        if line in ['1', '0']:  # 山線或其他
                            km += float(stations[station][11])
                            station = stations[station][5]
                        elif line == '2':  # 海線
                            km += float(stations[station][13])
                            station = stations[station][7]
                else:
                    # if station != '2214':
                    km += float(stations[station][11])
                    station = stations[station][5]
            else:  # 成追線
                km += float(stations[station][15])
                station = stations[station][9]

        if station == end_station:
            if roundabout_train == True:
                temp.append(['1001', stations[station][1], stations[station][3], km])
                break
            else:
                temp.append([stations[station][0], stations[station][1], stations[station][3], km])
                break

        if len(temp) > 200:
            ## print(len(temp))
            break

    list_passing_stations = temp

    return list_passing_stations  # 清單: [車站ID, 車站名稱, 里程位置, 與下一站相差公里數]


# 判斷成追線車次
def _find_cheng_zhui(list_start_end_station, start_station, end_station):
    result = False

    if list_start_end_station.__contains__('2260') and list_start_end_station.__contains__('3350'):  # 區間車，具備成功、追分二站
        result = True
    elif (start_station in Station_SEA and end_station in Station_MOUNTAIN) or (
            start_station in Station_MOUNTAIN and end_station in Station_SEA):  # 區間快，起訖車站為山海線兩端車站
        result = True

    return result


# 推算所有通過車站的時間
def estimate_time_space(dict_start_end_station, list_passing_stations):
    global time_loc

    station = []
    station_id = []
    time = []
    loc = []

    is_roundabout_train = False

    _after_midnight_train = {}
    _dict_lines_operation = {}

    for key, value in lines_stations.items():
        _dict_lines_operation[key] = [[], [], [], []]

    _dict_roundabout = {}

    # 判斷是不是環島車次
    if list_passing_stations[len(list_passing_stations) - 1][0] == "1001":
        is_roundabout_train = True

    # 將通過車站資料逐一轉成 dataframe
    for StationId, StationName, LocationKM, KM in list_passing_stations:
        if dict_start_end_station.__contains__(StationId):

            ARRTime = float(time_loc[dict_start_end_station[StationId][0]])
            DEPTime = float(time_loc[dict_start_end_station[StationId][1]])

            station_id.append(StationId)
            station.append(StationName)
            loc.append(float(KM))
            time.append(ARRTime)

            station_id.append(StationId)
            station.append(StationName)
            loc.append(float(KM))
            time.append(DEPTime)

        else:  # 通過不停靠之車站處理

            station_id.append(StationId)
            station.append(StationName)
            loc.append(float(KM))
            time.append(np.NaN)

    dict_temp = {"Station": station, "Time": time, "Loc": loc, "StationID": station_id}

    select_df = pd.DataFrame(dict_temp)

    # 將超過午夜的時間一律加上 2880，並且依據車站位置估計通過時間
    last_time_value = -1
    add_midnight = False

    for index, row in select_df.iterrows():

        if np.isnan(row['Time']) == False:

            if row['Time'] < last_time_value:
                add_midnight = True

            if add_midnight == True:
                select_df.loc[index, "Time"] = row['Time'] + 2880

            last_time_value = row['Time']

    select_df = select_df.set_index('Loc').interpolate(method='index')
    select_df = select_df.reset_index()

    # _將通過的估計時間弄進暫存的各營運路線表格
    for index, row in select_df.iterrows():
        for key, value in lines_stations.items():
            if row['StationID'] in value:
                _dict_lines_operation[key][0].append(row['Station'])
                _dict_lines_operation[key][1].append(row['StationID'])
                _dict_lines_operation[key][2].append(row['Time'])
                _dict_lines_operation[key][3].append(float(value[row['StationID']][0]))

    for key, value in _dict_lines_operation.items():
        dict_temp = {"Station": value[0], "StationID": value[1], "Time": value[2], "Loc": value[3]}
        select_df = pd.DataFrame(dict_temp)
        _dict_lines_operation[key] = select_df

    # 資料刪減整理
    drop_key = []
    for key, value in _dict_lines_operation.items():
        if len(value) < 3: # 資料不足者直接刪除
            drop_key.append(key)

        elif key == "LINE_WM" or key == "LINE_WSEA": # 部分成追線車次出現追分或成功直達竹南的現象，將竹南車站資料刪除
            for item in ['3350', '2260']:
                indexes = value[(value.StationID == item) | (value.StationID == '1250')].index.tolist()
                if len(indexes) > 2:
                    indexes.sort()
                    last_index = indexes[len(indexes) - 1]
                    test_index = list(range(indexes[0], indexes[0] + len(indexes)))

                    if test_index[len(test_index) - 1] == last_index:
                        index_1028 = value[value.StationID == '1250'].index.tolist()
                        df = value.copy()
                        df.drop(df.index[index_1028], inplace=True)
                        _dict_lines_operation[key] = df

            # 將未通過山海線（竹南、彰化二車站順序為相連）資料刪除
            index_temp = value[(value.StationID == '3360') | (value.StationID == '1250')].index.tolist()
            if index_temp == [0, 1, 2] or index_temp == [0, 1, 2, 3]:
                drop_key.append(key)

    for item in drop_key:
        _dict_lines_operation.pop(item)

    # 跨午夜車次擷取午夜後的運行資料
    for key, value in _dict_lines_operation.items():
        index_label = value.query('Time >= 2880').index.tolist()
        if len(index_label) >= 2:
            row_value = ['跨午夜', "-1", 2880, np.NaN]
            select_df = _insert_row(index_label[0], value, row_value)  # 插入一個虛擬的跨午夜車站

            select_df = select_df.set_index('Time').interpolate(method='index')  # 依據時間估計跨午夜的位置
            select_df = select_df.reset_index()

            df_after_midnight_train = select_df[index_label[0]:].copy()
            for index, row in df_after_midnight_train.iterrows():
                df_after_midnight_train.loc[index, 'Time'] = row['Time'] - 2880

            _after_midnight_train[key] = df_after_midnight_train

    # 環島車次處理，基本邏輯：如果該車次車站順序竹南與八堵車站為相鄰，需要拆開來為兩段
    if is_roundabout_train == True:

        df_line_wn = _dict_lines_operation["LINE_WN"]
        _dict_lines_operation.pop("LINE_WN")

        indexes_of_0920and1250 = df_line_wn[
            (df_line_wn.StationID == '0920') | (df_line_wn.StationID == '1250')].index.tolist()

        if abs(indexes_of_0920and1250[0] - indexes_of_0920and1250[1]) == 1:
            df1 = df_line_wn[0:indexes_of_0920and1250[1]].copy()
            df2 = df_line_wn[indexes_of_0920and1250[1]:]

            _dict_roundabout["LINE_WN_01"] = df1
            _dict_roundabout["LINE_WN_02"] = df2

    return _dict_lines_operation, _after_midnight_train, _dict_roundabout  # 本日車次運行資料, 跨午夜車次午夜後的運行資料, 環島車次在西部幹線北段的運行資料


# 在 dataframe 插入一列，參考自：https://www.geeksforgeeks.org/insert-row-at-given-position-in-pandas-dataframe/
def _insert_row(row_number, df, row_value):
    df1 = df[0:row_number].copy()
    df2 = df[row_number:]

    df1.loc[row_number] = row_value
    df_result = pd.concat([df1, df2])

    df_result.index = [*range(df_result.shape[0])]

    return df_result
