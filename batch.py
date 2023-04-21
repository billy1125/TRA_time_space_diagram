import sys
import os
import io
import shutil
import time
import queue

# 自訂class與module
import read_tra_json as tra_json
import tradata_process as tp
import diagram_process as dp
from progessbar import progress
import environment_variable as ev

Globals = ev.Singleton_GlobalVariables_Instance

# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 程式執行段
def main (argv_json_location, argv_website_svg_location, argv_select_trains, move_file):

    all_after_midnight_data = []

    check_output_folder(argv_website_svg_location)

     # 建立佇列
    json_files_queue = queue.Queue()

    for root, dirs, files in os.walk(argv_json_location + '/'):
        for file in files:
            if file.split('.')[1] == 'json':
                json_files_queue.put(file.split('.')[0])

    total = json_files_queue.qsize()
    print("共有" + str(total) + "個JSON檔案需要轉檔。" + "\n")

    if total != 0:
        while not json_files_queue.empty():
        # for file_date in json_files:
            file_date = json_files_queue.get()
            file_name = file_date + ".json"
            start = time.time()

            print("目前進行日期" + file_date + "轉檔。" + "\n")

            # 讀取 JSON 檔案，可選擇特定車次(argv_select_trains)
            all_trains_json = tra_json.find_trains(tra_json.read_json(file_name), argv_select_trains)

            all_trains_data = []

            for item in all_after_midnight_data:
                all_trains_data.append(item)

            all_after_midnight_data = []

            count = 0
            total = len(all_trains_json)

            for train_no in all_trains_json:

                train_id = train_no['Train']  # 車次號
                car_class = train_no['CarClass']  # 車種
                line = train_no['Line']  # 山線1、海線2、其他0
                over_night_stn = train_no['OverNightStn']  # 跨午夜車站
                line_dir = train_no['LineDir']  # 順逆行

                count += 1
                progress(count, total, "目前製作車次：" + train_id)

                # 查詢表定台鐵時刻表所有「停靠」車站，可查詢特定車次
                dict_start_end_station = tp.find_train_stations(train_no)

                # 查詢特定車次所有「停靠與通過」車站
                list_passing_stations = tp.find_passing_stations(dict_start_end_station,
                                                                 line,
                                                                 line_dir)

                # 推算所有通過車站的時間與位置
                list_train_time_space = tp.estimate_time_space(dict_start_end_station, list_passing_stations)

                for key, value in list_train_time_space[0].items():
                    all_trains_data.append([key, train_id, car_class, line, over_night_stn, None, value])

                for key, value in list_train_time_space[1].items():
                    all_after_midnight_data.append([key, train_id, car_class, line, over_night_stn, "midnight", value])

                for key, value in list_train_time_space[2].items():
                    all_trains_data.append(["LINE_WN", train_id, car_class, line, over_night_stn, key + train_id, value])

            # 繪製運行圖
            dp.Draw(all_trains_data, argv_website_svg_location, file_date)

            if move_file == True:
                if os.path.exists('JSON/' + file_name):
                    shutil.move('JSON/' + file_name, 'JSON_BACKUP/' + file_name)

            end = time.time()

            print("檔案轉換完成！轉換時間共" + str(round(end - start, 2)) + "秒\n")

    else:
        print('無法執行！原因為沒有讀取到 JSON 檔案。\n')

def check_output_folder(path):
    folders = ['west_link_north', 'west_link_south', 'west_link_moutain', 'west_link_sea',
               'pingtung', 'south_link', 'taitung', 'north_link', 'yilan',
               'pingxi', 'neiwan', 'jiji', 'shalun']

    output_folder = os.listdir(path)

    diff = list(set(folders).difference(set(output_folder)))

    if len(diff) > 0:
        for item in diff:
            os.makedirs(path + '/' + item)

def _print_usage(name):
    print( 'usage : ' + name + ' [-d] [-f] [-h] [-i inputfolder] [-o outputfolder] [--delete] [--force] [--help] [--inputfolder inputfolder] [--outputfolder outputfolder] [trainno ...]' )
    exit()

if __name__ == "__main__":
    Parameters = [] # 參數集：參數1: JSON 檔位置, 參數2: 運行圖檔案存檔位置, 參數3: 特定車次繪製

    print('************************************')
    print('台鐵JSON轉檔運行圖程式 - 版本：' + Globals.Version)
    print('************************************\n')

    if len(sys.argv) == 4:
        Parameters.append(sys.argv[1])
        Parameters.append(sys.argv[2])
        Parameters.append(sys.argv[3])
        Parameters.append(True)
    else:
        Parameters.append('JSON')
        Parameters.append('OUTPUT')

        action = input('您需要執行特定車次嗎？不需要請直接輸入Enter，或者輸入 "Y"：\n')
        if action.lower() == 'y':

            select_trains = []

            while True:
                action = input('請問特定車次號碼？(請輸入車次號，如果有多個車次要選擇，請不斷輸入，要結束直接輸入Enter)：\n')

                if action != '':
                    select_trains.append(action)
                if action == '':
                    break

            Parameters.append(select_trains)
        elif action.lower() == 'h':
            _print_usage("1h")
        else:
            Parameters.append('')

        Parameters.append(False)

    if Parameters[2] == 'ALL':
        Parameters[2] = ''

    main(Parameters[0], Parameters[1], Parameters[2], Parameters[3])
