import csv

class GlobalVariables:
    _instance = None

    def __new__(cls, *args, **kwargs): 
        if cls._instance is None: 
            cls._instance = super().__new__(cls) 
        return cls._instance 

    def __init__(self):
        self.Version = "1.3.7"                # 版本號
        self.JsonFolder = "JSON"              # 台鐵時刻表JSON預設置放資料夾
        self.OutputFolder = "OUTPUT"          # 運行圖檔案預設匯出目標資料夾
        self.DiagramHours = (4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 1, 2, 3, 4, 5, 6) # 一天每一小時的文字清單
 
        self.OperationLines = {}              # 各營運路線的基本資料(OperationLines.csv)，用於名稱顯示、轉檔後資料夾設定、運行圖大小設定等
        self.CarKind = {}                     # 車種代碼轉換成CSS用的標籤(CarKind.csv)
        self.Route = {}                       # 車次路徑(Route.csv)，該資料具有每一個車站與上下行連結的車站資訊，用於找出每一個車次會停靠或通過的所有車站
        self.SVG_X_Axis = {}                  # 時間轉換(SVG_X_Axis.csv)，該資料用於轉換時間與SVG檔的X軸數值

        # 台鐵營運路線的車站基本資訊(SVG_Y_Axis.csv)，該資料用於繪製運行圖的車站線、JSON資料轉換至繪製運行圖的中介資料，包括路線代碼、車站代碼、站名、SVG檔Y軸數值與是否為端點車站
        self.LinesStations = {}               # 各營運路線車站於運行圖中的位置，用於中介資料的推算
        self.LinesStationsForBackground = {}  # 各營運路線車站於運行圖中的位置，包含廢站、號誌站等車站，用於運行線圖形的車站線

        with open('CSV/OperationLines.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.OperationLines[row['LINE']] = row

        with open('CSV/CarKind.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.CarKind[row['CAR_CODE']] = row['CAR_TAG']
        
        with open('CSV/Route.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.Route[row['ID']] = row
       
        with open('CSV/SVG_X_Axis.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                self.SVG_X_Axis[row[0]] = row[2]

        with open('CSV/SVG_Y_Axis.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.DictReader(csvfile)
            list_csv = []

            for row in reader:
                list_csv.append((row['KIND'], row['ID'], row['DSC'], row['SVGYAXIS'], row['TERMINAL'])) # 仍要擷取車站名稱是為了除錯便利

            for key, value in self.OperationLines.items():
                stations_loc = {}
                stations_loc_for_background = {}

                for kind, id, dsc, svgyaxis, terminal in list_csv:
                    if key == kind:
                        if id != 'NA':
                            stations_loc[id] = {'DSC': dsc, 'SVGYAXIS': svgyaxis}
                        stations_loc_for_background[id] = {'DSC': dsc, 'SVGYAXIS': svgyaxis, 'TERMINAL': terminal}

                    self.LinesStations[key] = stations_loc
                    self.LinesStationsForBackground[key] = stations_loc_for_background
