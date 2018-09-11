import pandas as pd # 引用套件並縮寫為 pd
import numpy as np

#自訂class與module
import basic_data


#處理所有車站基本資訊(Stations.csv)
stations = basic_data.stations()

#時間轉換(Locate.csv)
time_loc = basic_data.time_loc()

#找出每一個車次的表定經過車站
def find_train_stations(train_no):

    list_start_end_station = {}
    
    for TimeInfos in train_no['TimeInfos']:
        if TimeInfos['Station'] not in list_start_end_station:
            list_start_end_station[TimeInfos['Station']] = [TimeInfos['ArrTime'], TimeInfos['DepTime'], TimeInfos['Station'], TimeInfos['Order']]
        elif TimeInfos['Station'] in list_start_end_station:
            list_start_end_station['End'] = [TimeInfos['ArrTime'], TimeInfos['DepTime'], TimeInfos['Station'], TimeInfos['Order']]

    return list_start_end_station

    
#找出每一個車次所有會經過的車站，無論是否會停靠
def find_stations(list_start_end_station, line, line_dir):

    #起終點車站代碼
    end_station_number = len(list_start_end_station) - 1
    start_station = list(list_start_end_station)[0]
    end_station = list(list_start_end_station)[end_station_number]

    #環島列車處理，例如：52車次
    roundabout_train = False
    if end_station == 'End':
        end_station = start_station
        roundabout_train = True

    #判斷是不是成追線，目前均為區間車，並且具備成功、追分二站
    cheng_zhui = False
    if list_start_end_station.__contains__('1118') and list_start_end_station.__contains__('1321'):
        cheng_zhui = True

    #判斷是不是內灣六家線，目前均為區間車，並且具備六家、竹東二站
    neiwan = False
    if list_start_end_station.__contains__('2214') or list_start_end_station.__contains__('2205'):
        neiwan = True

    #判斷是不是平溪深澳線，目前均為區間車，並且具備十分站，十分車站必經過
    pingxi = False
    if list_start_end_station.__contains__('1904'):
        pingxi = True

    #判斷是不是集集線，目前均為區間車，並且具備濁水站，濁水車站必經過
    jiji = False
    if list_start_end_station.__contains__('2703'):
        jiji = True

    #判斷是不是沙崙線，目前均為區間車，並且具備沙崙站，沙崙車站必經過
    shalun = False
    if list_start_end_station.__contains__('5102'):
        shalun = True

    global stations

    temp = []
    station = start_station

    km = 0.0 #計算經過車站里程
        
    while True:

        temp.append([stations[station][0], stations[station][1], stations[station][3], km])
        # print(stations[station][1])
        if line_dir == '1': #逆行
            
            if cheng_zhui == False:
                branch = stations[station][6]
                if branch != '':
                    if station == '1804': #平溪深澳線處理，瑞芳判斷
                        if end_station == '2003':
                            km += float(stations[station][12])
                            station = '6103' #指定到海科館站
                        elif end_station != '2003':
                            km += float(stations[station][10])
                            station = stations[station][4]
                    elif station == '1207': #集集線處理，二水判斷
                        if jiji == True:
                            km += float(stations[station][12])
                            station = '2702'
                        elif jiji == False:
                            km += float(stations[station][10])
                            station = stations[station][4]
                    elif station == '1230': #沙崙線處理，中洲判斷
                        if shalun == True:
                            km += float(stations[station][12])
                            station = '5101'
                        elif shalun == False:
                            km += float(stations[station][10])
                            station = stations[station][4]
                    else:
                        #山海線判斷
                        if line in ['1', '0']: #山線與其他
                            km += float(stations[station][10])
                            station = stations[station][4]
                        elif line == '2': #海線
                            km += float(stations[station][12])
                            station = stations[station][6]
                else:
                    km += float(stations[station][10])
                    station = stations[station][4]
            else: #成追線
                km += float(stations[station][14]) 
                station = stations[station][8] 

        elif line_dir == '0': #順行 

            if cheng_zhui == False:
                branch = stations[station][7]
                if branch != '':
                    if station == '1002': #八堵判斷
                        if end_station != '1001': #終點站非基隆的車次下一車站直接指定為暖暖
                            km += float(stations[station][13])
                            station = stations[station][7]
                        elif end_station == '1001': #終點站為基隆的車次
                            km += float(stations[station][11])
                            station = stations[station][5]
                    elif station == '1826': #蘇澳新判斷
                        if end_station == '1827': #終點站為蘇澳
                            km += float(stations[station][13])
                            station = '1827'
                        elif end_station != '1827': #終點站非蘇澳的車次下一車站直接指定為永樂
                            km += float(stations[station][11])                    
                            station = '1703'
                    elif station in ['1024', '2203']: #內灣六家線處理，北新竹與竹中判斷
                        if neiwan == True: #終點站為六家或內灣
                            km += float(stations[station][13])
                            if station == '1024':
                                station = '2212'
                            elif station == '2203':
                                if end_station in ['2210', '2205']: #若終點站為竹東或內灣，下一站指定為上員(偷懶的方式)
                                    station = '2204'
                                elif end_station == '2214':
                                    station = '2214'
                        elif neiwan == False: #終點站非六家或內灣的車次下一車站直接指定為竹北
                            km += float(stations[station][11])                    
                            station = '1023'
                    elif station == '1806': #平溪深澳線處理，三貂嶺判斷
                        if pingxi == True:
                            km += float(stations[station][13])
                            station = '1903'
                        elif pingxi == False: #終點站非平溪深澳線的車次下一車站直接指定為牡丹
                            km += float(stations[station][11])
                            station = '1807'
                    else: #山海線判斷
                        if line in ['1', '0']: #山線或其他
                            km += float(stations[station][11])
                            station = stations[station][5]
                        elif line == '2': #海線
                            km += float(stations[station][13])
                            station = stations[station][7]
                else:
                    #if station != '2214':
                    km += float(stations[station][11])
                    station = stations[station][5]
            else: #成追線
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
            print(len(temp))
            break
            
    list_passing_stations = temp

    return list_passing_stations

#將所有經過車站找出，並且將通過車站的時間點估計出來
def train_time_to_stations(list_start_end_station, list_passing_stations, nidmight_km):
    
    global time_loc

    station = []
    station_id = []
    time = []
    loc = []

    midnightOK = False

    for item in list_passing_stations:

        if nidmight_km != 0: #非車站內跨午夜處理，將跨午夜車站通過時間增加1440與0，之後在svg_save重複繪製兩次
            if item[3] > float(nidmight_km) and midnightOK == False:
                station_id.append('-1')
                station.append('跨午夜')
                loc.append(nidmight_km)
                time.append(1440)

                station_id.append('-1')
                station.append('跨午夜')
                loc.append(nidmight_km)
                time.append(0)
                midnightOK = True
            
        if item[0] == 'End':
            station_id.append(list_passing_stations[0][0])
        else:
            station_id.append(item[0])
        station.append(item[1])
        loc.append(item[3])

        if list_start_end_station.__contains__(item[0]): #如果經過車站清單中包括停靠車站，則將出發時間再加入
            #list_passing_stations[index].append(int(list_station[item[0]].replace(':','')))
            ArrTime = int(time_loc[list_start_end_station[item[0]][0]])
            DepTime = int(time_loc[list_start_end_station[item[0]][1]])

            time.append(ArrTime)

            if ArrTime > DepTime: #車站內跨午夜處理，將跨午夜車站通過時間增加1440與0，之後在svg_save重複繪製兩次
                station_id.append('-1')
                station.append('跨午夜')
                loc.append(item[3])
                time.append(1440)

                station_id.append('-1')
                station.append('跨午夜')
                loc.append(item[3])
                time.append(0)

            if item[0] == 'End':
                station_id.append(list_passing_stations[0][0])
            else:
                station_id.append(item[0])
            station.append(item[1])
            loc.append(item[3])
            time.append(DepTime)
        else:
            #list_passing_stations[index].append(np.NaN)
            time.append(np.NaN)

    dict = {"Station": station, "Time": time, "Loc": loc, "Station ID": station_id}
    
    select_df = pd.DataFrame(dict)
    #select_df = select_df.sort_values(by = 'Loc')
    
    select_df = select_df.set_index('Loc').interpolate(method='index') #估計通過時間

    return select_df


#跨午夜車次處理，基本邏輯，非車站內跨午夜則必須估計出午夜十二點的位置
def midnight_train(list_start_end_station, list_passing_stations, over_night_stn):
    
    global time_loc

    nidmight_km = 0

    midnight_in_station = False

    station = []
    station_id = []
    time = []
    loc = []

    i = 0

    while True:
        item = list_passing_stations[i]
        if list_start_end_station.__contains__(item[0]):
            ArrTime = int(time_loc[list_start_end_station[item[0]][0]])
            DepTime = int(time_loc[list_start_end_station[item[0]][1]])
                
            if item[0] == over_night_stn:

                if DepTime >= ArrTime: #插入一個跨午夜的虛擬車站，藉此估計列車所在的里程數
                    station_id.append('-1')
                    station.append('跨午夜')
                    loc.append(np.NaN)
                    time.append(1440)

                    station_id.append(item[0])
                    station.append(item[1])
                    loc.append(float(item[3]))
                    time.append(ArrTime + 1440) #要將跨午夜車站的時間加上1440估計較為適當

                elif DepTime < ArrTime: #車站內跨日則跳過處理，於train_time_to_stations函數進行處理即可
                    midnight_in_station = True
                    
            else:
                station_id.append(item[0])
                station.append(item[1])
                loc.append(float(item[3]))
                time.append(ArrTime)

                station_id.append(item[0])
                station.append(item[1])
                loc.append(float(item[3]))
                time.append(DepTime)

        i += 1
        if item[0] == over_night_stn:
            break

    dict = {"Station": station, "Time": time, "Loc": loc, "Station ID": station_id}

    select_df = pd.DataFrame(dict)
    # print(select_df)
    select_df = select_df.interpolate(method='index') #估計午夜通過里程
    
    # print(select_df[select_df.loc[:,"Station ID"] == '-1'].iloc[0, 0])

    if midnight_in_station == False: #如果跨午夜車次不是在車站內跨夜，才將資料帶出
        nidmight_km = select_df[select_df.loc[:,"Station ID"] == '-1'].iloc[0, 2]

    return nidmight_km

#環島列車處理，例如：51、52車次，直接拆成兩條路線處理，以八堵車站、竹南車站為分界點
def roundabout_train(train_time_space, line_dir):
    output = []
    row_number = -1

    number1 = ''
    number2 = ''

    if line_dir == '0':
        number1 = '1002'  # 八堵
        number2 = '1028'  # 竹南
    elif line_dir == '1':
        number1 = '1028'
        number2 = '1002'

    train_time_space['Loc'] = train_time_space.index

    for i in range(0, 3):
        station = []
        station_id = []
        time = []
        loc = []
        temp = []

        if i in [1, 2]:
            row_number -= 1
        while True:
            row_number += 1
            temp.append(train_time_space.iloc[row_number])

            station.append(train_time_space.iloc[row_number, 0])
            time.append(train_time_space.iloc[row_number, 1])
            station_id.append(train_time_space.iloc[row_number, 2])
            loc.append(train_time_space.iloc[row_number, 3])

            if i == 2 and row_number == len(train_time_space) - 1:
                break
            if i == 0 and train_time_space.iloc[row_number, 2] == number1:
                break
            if i == 1 and train_time_space.iloc[row_number, 2] == number2:
                break

        dict = {"Station": station, "Time": time, "Loc": loc, "Station ID": station_id}

        select_df = pd.DataFrame(dict)
        select_df = select_df.set_index('Loc').interpolate(method='index')  # 估計通過時間

        output.append(select_df)

    return output