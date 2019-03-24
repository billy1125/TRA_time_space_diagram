import pandas as pd # 引用套件並縮寫為 pd
import numpy as np

# 自訂class與module
import basic_data

# 類別資料檔(Category.csv)
category = basic_data.category()

# 山海線車站，去除竹南與彰化，用於檢查是否是成追線車次
Station_SEA = []
Station_MOUNTAIN = []

for item in category:
    if item[0] == 'LINE_WSEA':
        if item[1] not in ["1028", "1120"]:
            Station_SEA.append(item[1])
    if item[0] == 'LINE_WM':
        if item[1] not in ["1028", "1120"]:
            Station_MOUNTAIN.append(item[1])

# 處理所有車站基本資訊(Stations.csv)
stations = basic_data.stations()

# 時間轉換(Locate.csv)
time_loc = basic_data.time_loc()


# 找出每一個車次的表定經過車站
def find_train_stations(train_no):

    dict_start_end_station = {}
    
    for TimeInfos in train_no['TimeInfos']:
        if TimeInfos['Station'] not in dict_start_end_station:
            dict_start_end_station[TimeInfos['Station']] = [TimeInfos['ArrTime'], TimeInfos['DepTime'], TimeInfos['Station'], TimeInfos['Order']]
        elif TimeInfos['Station'] in dict_start_end_station:
            dict_start_end_station['End'] = [TimeInfos['ArrTime'], TimeInfos['DepTime'], TimeInfos['Station'], TimeInfos['Order']]

    return dict_start_end_station  # 字典 車站ID: [到站時間, 離站時間, 車站ID, 順序]

    
# 找出每一個車次所有會經過的車站，無論是否會停靠
def find_passing_stations(dict_start_end_station, line, line_dir):

    # 起終點車站代碼
    end_station_number = len(dict_start_end_station) - 1
    start_station = list(dict_start_end_station)[0]
    end_station = list(dict_start_end_station)[end_station_number]

    # 環島列車處理，例如：52車次
    roundabout_train = False
    if end_station == 'End':
        end_station = start_station
        roundabout_train = True

    # 判斷是不是成追線
    cheng_zhui = find_cheng_zhui(dict_start_end_station, start_station, end_station)

    # 判斷是不是內灣六家線，目前均為區間車，並且具備六家、竹東二站
    neiwan = False
    if dict_start_end_station.__contains__('2214') or dict_start_end_station.__contains__('2205'):
        neiwan = True

    # 判斷是不是平溪深澳線，目前均為區間車，並且具備十分站，十分車站必經過
    pingxi = False
    if dict_start_end_station.__contains__('1904'):
        pingxi = True

    # 判斷是不是集集線，目前均為區間車，並且具備濁水站，濁水車站必經過
    jiji = False
    if dict_start_end_station.__contains__('2703'):
        jiji = True

    # 判斷是不是沙崙線，目前均為區間車，並且具備沙崙站，沙崙車站必經過
    shalun = False
    if dict_start_end_station.__contains__('5102'):
        shalun = True

    global stations

    list_passing_stations = []
    temp = []
    station = start_station

    km = 0.0  # 計算經過車站里程
        
    while True:

        temp.append([stations[station][0], stations[station][1], stations[station][3], km])

        if line_dir == '1': # 逆行
            
            if cheng_zhui == False:
                branch = stations[station][6]
                if branch != '':
                    if station == '1804': #平溪深澳線處理，瑞芳判斷
                        if end_station == '2003':
                            km += float(stations[station][12])
                            station = '6103' # 指定到海科館站
                        elif end_station != '2003':
                            km += float(stations[station][10])
                            station = stations[station][4]
                    elif station == '1207': # 集集線處理，二水判斷
                        if jiji == True:
                            km += float(stations[station][12])
                            station = '2702'
                        elif jiji == False:
                            km += float(stations[station][10])
                            station = stations[station][4]
                    elif station == '1230': # 沙崙線處理，中洲判斷
                        if shalun == True:
                            km += float(stations[station][12])
                            station = '5101'
                        elif shalun == False:
                            km += float(stations[station][10])
                            station = stations[station][4]
                    else:
                        # 山海線判斷
                        if line in ['1', '0']: # 山線與其他
                            km += float(stations[station][10])
                            station = stations[station][4]
                        elif line == '2': # 海線
                            km += float(stations[station][12])
                            station = stations[station][6]
                else:
                    km += float(stations[station][10])
                    station = stations[station][4]
            else: # 成追線
                km += float(stations[station][14]) 
                station = stations[station][8] 

        elif line_dir == '0': # 順行

            if cheng_zhui == False:
                branch = stations[station][7]
                if branch != '':
                    if station == '1002': # 八堵判斷
                        if end_station != '1001': # 終點站非基隆的車次下一車站直接指定為暖暖
                            km += float(stations[station][13])
                            station = stations[station][7]
                        elif end_station == '1001': # 終點站為基隆的車次
                            km += float(stations[station][11])
                            station = stations[station][5]
                    elif station == '1826': # 蘇澳新判斷
                        if end_station == '1827': # 終點站為蘇澳
                            km += float(stations[station][13])
                            station = '1827'
                        elif end_station != '1827': # 終點站非蘇澳的車次下一車站直接指定為永樂
                            km += float(stations[station][11])                    
                            station = '1703'
                    elif station in ['1024', '2203']: #內灣六家線處理，北新竹與竹中判斷
                        if neiwan == True: # 終點站為六家或內灣
                            km += float(stations[station][13])
                            if station == '1024':
                                station = '2212'
                            elif station == '2203':
                                if end_station in ['2210', '2205']: # 若終點站為竹東或內灣，下一站指定為上員(偷懶的方式)
                                    station = '2204'
                                elif end_station == '2214':
                                    station = '2214'
                        elif neiwan == False: # 終點站非六家或內灣的車次下一車站直接指定為竹北
                            km += float(stations[station][11])                    
                            station = '1023'
                    elif station == '1806': # 平溪深澳線處理，三貂嶺判斷
                        if pingxi == True:
                            km += float(stations[station][13])
                            station = '1903'
                        elif pingxi == False: # 終點站非平溪深澳線的車次下一車站直接指定為牡丹
                            km += float(stations[station][11])
                            station = '1807'
                    else: # 山海線判斷
                        if line in ['1', '0']: # 山線或其他
                            km += float(stations[station][11])
                            station = stations[station][5]
                        elif line == '2': # 海線
                            km += float(stations[station][13])
                            station = stations[station][7]
                else:
                    #if station != '2214':
                    km += float(stations[station][11])
                    station = stations[station][5]
            else: # 成追線
                km += float(stations[station][15])
                station = stations[station][9]

        if station == end_station:
            if roundabout_train == True:
                temp.append(['End', stations[station][1], stations[station][3], km])
                break
            else:
                temp.append([stations[station][0], stations[station][1], stations[station][3], km])
                break

        if len(temp) > 200:
            ## print(len(temp))
            break

    list_passing_stations = temp

    return list_passing_stations  # 清單: [車站ID, 車站名稱, 里程數, 與下一站相差公里數]


# 判斷成追線車次
def find_cheng_zhui(list_start_end_station, start_station, end_station):

    result = False

    if list_start_end_station.__contains__('1118') and list_start_end_station.__contains__('1321'):  # 區間車，具備成功、追分二站
        result = True
    elif (start_station in Station_SEA and end_station in Station_MOUNTAIN) or (
                    start_station in Station_MOUNTAIN and end_station in Station_SEA):  # 區間快，起訖車站為山海線兩端車站
        result = True

    return result

# 推算所有通過車站的時間
def estimate_time_space(dict_start_end_station, list_passing_stations, line_dir):

    global time_loc

    station = []
    station_id = []
    time = []
    loc = []

    is_roundabout_train = False

    return_list_df = []

    # 判斷是不是環島車次
    if list_passing_stations[len(list_passing_stations) - 1][0] == "End":
        is_roundabout_train = True

    # 將通過車站資料逐一轉成 dataframe
    for StationId, StationName, LocationKM, KM in list_passing_stations:
        if dict_start_end_station.__contains__(StationId):

            ArrTime = float(time_loc[dict_start_end_station[StationId][0]])
            DepTime = float(time_loc[dict_start_end_station[StationId][1]])

            station_id.append(StationId)
            station.append(StationName)
            loc.append(float(KM))
            time.append(ArrTime)

            station_id.append(StationId)
            station.append(StationName)
            loc.append(float(KM))
            time.append(DepTime)

        else:  # 通過不停靠之車站處理

            station_id.append(StationId)
            station.append(StationName)
            loc.append(float(KM))
            time.append(np.NaN)

    dict_temp = {"Station": station, "Time": time, "Loc": loc, "Station ID": station_id}

    select_df = pd.DataFrame(dict_temp)

    # if over_night_stn != "0":

    last_time_value = -1
    add_midnight = False

    # 將超過午夜的時間一律加上 1440
    for index, row in select_df.iterrows():

        if np.isnan(row['Time']) == False:

            if row['Time'] < last_time_value:
                add_midnight = True

            if add_midnight == True:
                select_df.loc[index, "Time"] = row['Time'] + 1440

            last_time_value = row['Time']

    select_df = select_df.set_index('Loc').interpolate(method='index')  # 依據車站位置估計通過時間

    select_df = select_df.reset_index()

    # 環島車次處理，基本邏輯：將整個路線拆成三段，以八堵與竹南車站作為三段分界點
    if is_roundabout_train == True:
        station_1002_loc = select_df[select_df["Station ID"].isin(["1002"])].iloc[0, 2]
        station_1028_loc = select_df[select_df["Station ID"].isin(["1028"])].iloc[0, 2]

        if line_dir == "0":
            return_list_df.append(select_df[select_df["Time"] <= station_1002_loc])
            return_list_df.append(select_df[(select_df["Time"] >= station_1002_loc) & (select_df["Time"] <= station_1028_loc)])
            return_list_df.append(select_df[select_df["Time"] >= station_1028_loc])
        elif line_dir == "1":
            return_list_df.append(select_df[select_df["Time"] <= station_1028_loc])
            return_list_df.append(
                select_df[(select_df["Time"] >= station_1028_loc) & (select_df["Time"] <= station_1002_loc)])
            return_list_df.append(select_df[select_df["Time"] >= station_1002_loc])

    elif is_roundabout_train == False:
        return_list_df.append(select_df)

    return return_list_df
