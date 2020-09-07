import csv

lines = ['LINE_WN', 'LINE_WM', 'LINE_WSEA', 'LINE_WS', 'LINE_P', 'LINE_S',
         'LINE_T', 'LINE_N', 'LINE_I', 'LINE_PX', 'LINE_NW', 'LINE_J', 'LINE_SL']


class GlobalVariables:

    def __init__(self):

        self.LinesStations = {}  # 各營運路線車站於運行圖中的位置，用於運行線的繪製
        self.LinesStationsForBackground = {}  # 各營運路線車站於運行圖中的位置，包含廢站、號誌站等車站
        self.Category = []
        self.Stations = {}
        self.TimeLocation = {}

        # 處理所有基本資訊(Category.csv)
        with open('CSV/Category.csv', newline='', encoding='utf8') as csvfile:

            reader = csv.reader(csvfile)

            for row in reader:
                self.Category.append(row)

        # 處理所有車站基本資訊(Stations.csv)
        with open('CSV/Stations.csv', newline='', encoding='utf8') as csvfile:

            reader = csv.reader(csvfile)

            for row in reader:
                # print(row[0])
                self.Stations[row[0]] = row

        # 時間轉換(Locate.csv)
        with open('CSV/Locate.csv', newline='', encoding='big5') as csvfile:
            reader = csv.reader(csvfile)

            for row in reader:
                # print(row[0])
                self.TimeLocation[row[0]] = row[2]

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

                    self.LinesStations[line] = stations_loc
                    self.LinesStationsForBackground[line] = stations_loc_for_background
