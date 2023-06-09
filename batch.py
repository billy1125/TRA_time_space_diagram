import sys
import os
# import io
import shutil
import time
import queue

# 自訂class與module
import read_tra_json as rtj
import train_space_time as tps
import diagram_process as dp
import progessbar as pb 
import environment_variable as ev

Globals = ev.GlobalVariables()
Spacetime = tps.SpaceTime()

# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 程式執行段
def main (argv_json_location, argv_website_svg_location, argv_select_trains, move_file):

    all_after_midnight_data = []
    json_files_queue = queue.Queue()

    _check_output_folder(argv_website_svg_location)
    
    # 擷取台鐵JSON檔
    for root, dirs, files in os.walk(argv_json_location + '/'):
        for file in files:
            if file.split('.')[1] == 'json':
                json_files_queue.put(file.split('.')[0])

    total = json_files_queue.qsize()
    print("共有 {0} 個 JSON 檔案需要轉檔。\n".format(str(total)))   

    if total != 0:
        while not json_files_queue.empty():            
            # try:
                file_date = json_files_queue.get()
                print("目前進行日期「{0}」轉檔。\n".format(file_date))            
                
                file_name = file_date + ".json"
                start = time.time()            

                all_trains_json = rtj.find_trains(rtj.read_json(file_name), argv_select_trains)  # 讀取 JSON 檔案，可選擇特定車次(argv_select_trains)         
                all_trains_data = [] 

                # 上一個檔案的跨午夜車次，放到下一個檔案中繪製
                for item in all_after_midnight_data:
                    all_trains_data.append(item)

                all_after_midnight_data = []

                count = 0
                total = len(all_trains_json)

                # 逐一將每一個車次進行資料轉換
                for train in all_trains_json:

                    train_data = Spacetime.CalculateSpaceTime(train)
                    all_trains_data.append(train_data[0])
                    all_after_midnight_data.append(train_data[1])
                    count += 1
                    pb.progress(count, total, "目前已處理車次：{0}".format(train['Train']))

                # 繪製運行圖
                dp.draw(all_trains_data, argv_website_svg_location, file_date)

                if move_file == True:
                    if os.path.exists('JSON/' + file_name):
                        shutil.move('JSON/' + file_name, 'JSON_BACKUP/' + file_name)

            # except Exception as e:
            #     print("\n發生了一個錯誤：在第 {0} 車次出問題，可能問題是 {1}".format(train['Train'], str(e)))
            # finally:
                end = time.time()
                print("\n工作完成！轉換時間共 {0} 秒\n".format(str(round(end - start, 2))))

    else:
        print('無法執行！沒有 JSON 檔案，請在 JSON 資料夾中置入台鐵的時刻表 JSON。\n')

def _check_output_folder(path):

    output_folder = os.listdir(path)

    diff = list(set(Globals.Folders).difference(set(output_folder)))

    if len(diff) > 0:
        for item in diff:
            os.makedirs(path + '/' + item)

if __name__ == "__main__":
    Parameters = [] # 參數集：參數1: JSON 檔位置, 參數2: 運行圖檔案存檔位置, 參數3: 特定車次繪製

    print('************************************')
    print('台鐵JSON轉檔運行圖程式 - 版本：{0}'.format(Globals.Version))
    print('************************************\n')

    if len(sys.argv) == 4:
        Parameters.append(sys.argv[1])
        Parameters.append(sys.argv[2])
        Parameters.append(sys.argv[3])
        Parameters.append(True)
    else:
        Parameters.append('JSON')
        Parameters.append('OUTPUT')

        action = input('請選擇轉檔方式，直接轉檔請直接按Enter鍵，需要轉檔特定車次請輸入「Y」再進行選擇，離開請按「N」：')
        if action.lower() == 'y':
            select_trains = []
            while True:
                action = input('請問特定車次號碼？\n請輸入車次號後再按Enter鍵。如果有多個車次，請依序輸入各車次，中間以半形空白鍵隔開(例如: 408 426 111)，再按Enter鍵：')
                if action != '':
                    select_trains = action.split(' ')
                    break
                if action == '':
                    break
            Parameters.append(select_trains)
        elif action.lower() == 'n':
            sys.exit("程式中止")  
        else:
            Parameters.append('')

        Parameters.append(False)

    if Parameters[2] == 'ALL':
        Parameters[2] = ''

    main(Parameters[0], Parameters[1], Parameters[2], Parameters[3])
