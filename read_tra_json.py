import json


# 讀取台鐵JSON
def read_json(filename):
    with open('JSON/' + filename, 'r', encoding='utf8') as data_file:
        data = json.load(data_file)

    return data


# 找出每一個車次
def find_trains(data, train_no):
    trains = []

    if train_no == '':
        for x in data['TrainInfos']:  # 逐車次搜尋
            trains.append(x)
    elif train_no != '':
        for x in data['TrainInfos']:  # 逐車次搜尋
            if x['Train'] == train_no:
                trains.append(x)

    return trains