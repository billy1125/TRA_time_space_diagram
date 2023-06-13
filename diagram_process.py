# 台鐵資料轉換後繪製程序
from math import dist
import queue

# 自訂class與module
import environment_variable as ev
import diagram as dm

# 公用參數
Globals = ev.GlobalVariables()

# 繪製各路線的車次線
def draw(all_trains, location, date):
    diagrams = {} # 各營運線運行圖

    for key, value in Globals.OperationLines.items():
        diagrams[key] = dm.Diagram(Globals.LinesStationsForBackground[key],
                                    "{0}/{1}/{2}".format(location, value['FOLDER'], value['PREFIX']),
                                    date,
                                    key,
                                    1200 * (len(Globals.DiagramHours) - 1) + 100,
                                    int(value["MAX_X_AXIS"]),
                                    Globals.DiagramHours)

    for train in all_trains:
        for line_kind, train_id, car_class, line_dir, train_time_space in train:
            set_train_path(line_kind, train_id, car_class, train_time_space, diagrams)

    for key, value in diagrams.items():
        value.save_file()

# 找出停靠順序碼(StopOrder)不連貫的車站在dataframe是第幾列？如果停靠順序碼是連貫的，則回傳dataframe的長度
def check_undiscontinuous_order(train_time_space):
    # 運算的方式：把train_time_space的停靠碼抓出來成為一個清單，另一個清單則是把所有元素提前一個位址，第一個元素則排到最後一個去
    # 兩個清單相減，就能找出在哪一個位址是不連續的，如果兩個清單就是連貫的，那就是最後一個元素
    list1 = train_time_space['StopOrder'].tolist()
    list2 = train_time_space['StopOrder'][1:].tolist()
    list2.append(list1[0])
    subtract_list = [a - b for a, b in zip(list2, list1)]
    i = 0
    while i < len(subtract_list):
        if subtract_list[i] != 1:
            return i
        i += 1

# 車次線路徑與車次號標註
def set_train_path(line_kind, train_id, car_class, train_time_space, diagrams):

    color = Globals.CarKind.get(car_class, 'special')
    # svg線條資訊，藉由每一個要通過時間與地點建立svg座標值
    undiscontinuous_order_number = check_undiscontinuous_order(train_time_space)
    df_length = train_time_space.shape[0]
    train_time_space_slices = []
    if df_length != undiscontinuous_order_number:
        train_time_space_slices.append(train_time_space.iloc[:undiscontinuous_order_number + 1, :])
        train_time_space_slices.append(train_time_space.iloc[undiscontinuous_order_number + 1:, :])

    for index, item in enumerate(train_time_space_slices):    
        if item.shape[0] > 2:
            coordinates = queue.Queue()  # 用來置放每一個轉折點的座標值
            path = "M"
            for item_index, row in item.iterrows():        
                if row['StopStation'] != -1 or Globals.LinesStationsForBackground[line_kind][row['StationID']]['TERMINAL'] == "Y":
                    x = round(row['Time'] * 10 - 1200 * Globals.DiagramHours[0] + 50, 4)
                    y = round(row['Loc'] + 50, 4)
                    path += str(x) + ',' + str(y) + ' '
                    coordinates.put((x, y)) 

            # 依據每一個轉折點座標，計算每一個轉折點之間的長度
            coordinates_pairs_temp = []          
            coordinates_distance = []   # 用來置放每一個轉折點之間的長度
            while not coordinates.empty():  
                if len(coordinates_pairs_temp) == 2:            
                    coordinates_distance.append(dist(coordinates_pairs_temp[0], coordinates_pairs_temp[1]))
                    coordinates_pairs_temp[0] = coordinates_pairs_temp[1]
                    coordinates_pairs_temp[1] = coordinates.get()
                elif len(coordinates_pairs_temp) == 1: 
                    coordinates_pairs_temp.append(coordinates.get())
                elif len(coordinates_pairs_temp) == 0: 
                    coordinates_pairs_temp.append(coordinates.get())
            if len(coordinates_pairs_temp) == 2:
                coordinates_distance.append(dist(coordinates_pairs_temp[0], coordinates_pairs_temp[1]))
            
            # 區間車標號方式：各段長度長於60，偶數位的進行標註，其他車種：100-500的長度在中間標註，大於500則是在中間標註兩次
            text_position = []   # 用來置放標號定位點
            accumulate_dist = 0  # 所有轉折點的長度累進
            if color == "local":       
                new_text_position = []
                for item in coordinates_distance:        
                    if item > 60:
                        pos = accumulate_dist + item / 4
                        text_position.append(pos)
                    accumulate_dist += item
                for i in range(0, len(text_position)):        
                    if i % 2 == 0:
                        new_text_position.append(text_position[i])
                text_position = new_text_position
            else:
                for item in coordinates_distance:        
                    if item > 60 and item < 100:
                        text_position.append(0)
                    elif item >= 100 and item <= 500:
                        pos = accumulate_dist + item / 2
                        text_position.append(pos)
                    elif item > 500:
                        for i in range(1, 3):
                            pos = accumulate_dist + i * (item / 3)
                            text_position.append(pos)
                    accumulate_dist += item

            # 列車號標示的處理
            if index == 1:
                train_id = "{0}-{1}".format(train_id, "環島")
            # if is_midnight == True:
            #     train_id = "{0}-{1}".format(train_id, "跨午夜")

            diagrams[line_kind].draw_line(train_id, path, text_position, color)
