# 環境變數

import csv

class GlobalVariables:

    _instance = None

    def __new__(cls, *args, **kwargs): 
        if cls._instance is None: 
            cls._instance = super().__new__(cls) 
        return cls._instance 

    def __init__(self):
        self.Version = "1.3.6"
        self.Lines = ('LINE_WN', 'LINE_WM', 'LINE_WSEA', 'LINE_WS', 'LINE_P', 'LINE_S', 'LINE_T', 'LINE_N', 'LINE_I', 'LINE_PX', 'LINE_LJ', 'LINE_NW', 'LINE_J', 'LINE_SL')
        self.LinesStations = {}  # 各營運路線車站於運行圖中的位置，用於運行線的繪製
        self.LinesStationsForBackground = {}  # 各營運路線車站於運行圖中的位置，包含廢站、號誌站等車站
        self.SVG_X_Axis = {}
        self.Route = {}
        self.DiagramHours = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 1, 2, 3, 4, 5, 6) # 一天每一小時的文字清單
        self.CarKind = {
                        '1131': 'local',
                        '1132': 'local',
                        '1100': 'tze_chiang_diesel',
                        '1101': 'taroko',
                        '1102': 'taroko',
                        '1103': 'tze_chiang_diesel',
                        '1104': 'special',
                        '1105': 'tze_chiang',
                        '1106': 'tze_chiang',
                        '1107': 'puyuma',
                        '1108': 'tze_chiang',
                        '1109': 'tze_chiang',
                        '110A': 'tze_chiang',
                        '110B': 'emu1200',
                        '110C': 'emu300',
                        '110D': 'tze_chiang_diesel',
                        '110E': 'tze_chiang_diesel',
                        '110F': 'tze_chiang_diesel',
                        '110G': 'emu3000',
                        '110H': 'emu3000',
                        '1110': 'chu_kuang',
                        '1111': 'chu_kuang',
                        '1112': 'chu_kuang',
                        '1114': 'chu_kuang',
                        '1115': 'chu_kuang',
                        '1120': 'fu_hsing',
                        '1140': 'ordinary',
                        '0000': 'special'
                        }
        self.LineDescription = {
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
                        'LINE_LJ': '六家線（新竹-六家）',
                        'LINE_J': '集集線（二水-車埕）',
                        'LINE_SL': '沙崙線（中洲-沙崙)'
                        }
        self.LinesDiagramSetting = {'LINE_WN': ('/west_link_north/WESTNORTH_', 'LINE_WN', 3000),
                         'LINE_WM': ('/west_link_moutain/WESTMOUNTAIN_', 'LINE_WM', 2000),
                         'LINE_WSEA': ('/west_link_sea/WESTSEA_', 'LINE_WSEA', 2000),
                         'LINE_WS': ('/west_link_south/WESTSOUTH_', 'LINE_WS', 4000),
                         'LINE_P': ('/pingtung/PINGTUNG_', 'LINE_P', 1500),
                         'LINE_S': ('/south_link/SOUTHLINK_', 'LINE_S', 2000),
                         'LINE_T': ('/taitung/TAITUNG_', 'LINE_T', 2000),
                         'LINE_N': ('/north_link/NORTHLINK_', 'LINE_N', 1500),
                         'LINE_I': ('/yilan/YILAN_', 'LINE_I', 2000),
                         'LINE_PX': ('/pingxi/PINGXI_', 'LINE_PX', 1250),
                         'LINE_NW': ('/neiwan/NEIWAN_', 'LINE_NW', 1250),
                         'LINE_LJ': ('/liujia/LIUJIA_', 'LINE_LJ', 500),
                         'LINE_J': ('/jiji/JIJI_', 'LINE_J', 1250),
                         'LINE_SL': ('/shalun/SHALUN_', 'LINE_SL', 650)}
        
        self.Folders = ('west_link_north', 'west_link_south', 'west_link_moutain', 'west_link_sea',
                        'pingtung', 'south_link', 'taitung', 'north_link', 'yilan',
                        'pingxi', 'neiwan', 'liujia', 'jiji', 'shalun')

        # 車次路徑(Route.csv)，該資料具有每一個車站與上下行連結的車站資訊，用於找出每一個車次會停靠或通過的所有車站
        with open('CSV/Route.csv', newline='', encoding='utf8') as csvfile:

            reader = csv.reader(csvfile)

            for row in reader:
                # print(row[0])
                self.Route[row[0]] = tuple(row)

        # 時間轉換(SVG_X_Axis.csv)，該資料用於轉換時間與SVG檔的X軸數值
        with open('CSV/SVG_X_Axis.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile)

            for row in reader:
                # print(row[0])
                self.SVG_X_Axis[row[0]] = row[2]

        # 台鐵營運路線的車站基本資訊(SVG_Y_Axis.csv)，該資料用於繪製運行圖的車站線、JSON資料轉換至繪製運行圖的中介資料，包括路線代碼、車站代碼、站名、SVG檔Y軸數值與是否為端點車站
        with open('CSV/SVG_Y_Axis.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.DictReader(csvfile)
            list_csv = []

            for row in reader:
                list_csv.append((row['KIND'], row['ID'], row['DSC'], row['SVGYAXIS'], row['TERMINAL']))

            for line in self.Lines:
                stations_loc = {}
                stations_loc_for_background = []
                log = 0
                for kind, id, dsc, svgyaxis, terminal in list_csv:
                    log += 1
                    if line == kind:
                        if id != 'NA':
                            stations_loc[id] = (float(svgyaxis), dsc, terminal)
                        stations_loc_for_background.append((kind, id, dsc, svgyaxis))

                    self.LinesStations[line] = stations_loc
                    self.LinesStationsForBackground[line] = tuple(stations_loc_for_background)
