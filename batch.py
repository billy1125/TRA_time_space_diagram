# 主程式
import sys
import os
# import io
import shutil
import time
import queue
import configparser

# 自訂class與module
import read_tra_json as rtj
import train_space_time as tps
import diagram_process as dp
import progessbar as pb 
import environment_variable as ev

# 公用參數
Globals = ev.GlobalVariables()
Spacetime = tps.SpaceTime()

# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 程式執行段，參數：
# argv_select_trains: 特定車次繪製
# argv_website_svg_location: 運行圖檔案存檔位置
# argv_json_location: JSON 檔位置
# argv_json_backup_location: 轉換後 JSON 檔存檔位置
def main (argv_select_trains, argv_website_svg_location, argv_json_location, argv_json_backup_location):

    _check_output_folder(argv_website_svg_location)
    all_after_midnight_data = []
    
    # 擷取台鐵JSON檔
    json_files_queue = queue.Queue()

    for root, dirs, files in os.walk(f'{argv_json_location}/'):
        for file in files:
            if file.split('.')[1] == 'json':
                json_files_queue.put(file.split('.')[0])

    total = json_files_queue.qsize()
    print(f"共有 {str(total)} 個 JSON 檔案需要轉檔。\n")

    if total != 0:
        while not json_files_queue.empty():            
            try:
                start = time.time() 
                file_date = json_files_queue.get()
                print(f"目前進行日期「{file_date}」轉檔。\n")            
                
                file_name = file_date + ".json"
                all_trains_json = rtj.find_trains(rtj.read_json(file_name), argv_select_trains)  # 讀取 JSON 檔案，可選擇特定車次(argv_select_trains)         
                
                count = 0
                all_trains_data = []                 
                total = len(all_trains_json)

                # 上一個檔案的跨午夜車次，放到下一個檔案中繪製
                # for item in all_after_midnight_data:
                #     all_trains_data.append(item)

                # all_after_midnight_data = []

                # 逐一將每一個車次進行資料轉換
                for train in all_trains_json:
                    train_data = Spacetime.CalculateSpaceTime(train)
                    all_trains_data.append(train_data['Train_Data'])
                    # all_after_midnight_data.append(train_data['After_midnight_Data'])
                    count += 1
                    pb.progress(count, total, f"目前已處理車次：{train['Train']}。")

                # 繪製運行圖
                dp.draw(all_trains_data, argv_website_svg_location, file_date)

                # 轉換後 JSON 檔案備份
                if os.path.exists(f'{argv_json_backup_location}/') != True:
                    os.makedirs(f'{argv_json_backup_location}/')
                if os.path.exists(f'{argv_json_location}/{file_name}'):
                    shutil.move(f'{argv_json_location}/{file_name}', f'{argv_json_backup_location}/{file_name}')

            except Exception as e:
                print(f"發生了一個錯誤：在第 {train['Train']} 車次出問題，可能問題是 {str(e)}。\n")
            finally:
                end = time.time()
                print(f"工作完成！轉換時間共 {str(round(end - start, 2))} 秒。\n")

    else:
        print('無法執行！沒有 JSON 檔案，請在 JSON 資料夾中置入台鐵的時刻表 JSON。\n')

# 確認運行圖繪製完成的存放的資料夾
def _check_output_folder(path):
    output_folder = os.listdir(path)
    default_folders = []

    for value in Globals.OperationLines.values():
        default_folders.append(value['FOLDER'])
    diff = list(set(default_folders).difference(set(output_folder)))

    if len(diff) > 0:
        for item in diff:
            os.makedirs(path + '/' + item)

def _load_config(config_file='config.ini'):
    config = configparser.ConfigParser()
    
    # 檢查config.ini文件是否存在
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"config.ini文件 '{config_file}' 不存在！")
    
    config.read(config_file)
    return config

if __name__ == "__main__":

    print('************************************')
    print(f'台鐵JSON轉檔運行圖程式 - 版本：{Globals.Version}')
    print('************************************\n')

    try:
        config = _load_config()    # 讀取config.ini設定值
        
        svg_location = config['DEFAULT']['OutputFolder']
        json_location = config['DEFAULT']['JsonFolder']
        json_backup = config['DEFAULT']['BackupFolder']
        
        Parameters = []                       # 參數集
        Parameters.append("")                 # 參數1: 特定車次繪製
        Parameters.append(svg_location)       # 參數2: 運行圖檔案存檔位置，預設資料夾「OUTPUT」
        Parameters.append(json_location)      # 參數3: JSON 檔位置，預設資料夾「JSON」 
        Parameters.append(json_backup)        # 參數4: 轉換後 JSON 檔存檔位置，預設資料夾「JSON_BACKUP」

        if "-b" in sys.argv:
            print('以批次模式執行...\n')
        else:
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
                Parameters[0] = select_trains
            elif action.lower() == 'n':
                sys.exit("您已離開本程式，謝謝您的使用。\n")

        main(Parameters[0], Parameters[1], Parameters[2], Parameters[3])
            
    except Exception as e:
        print(f"發生錯誤，可能問題是 {str(e)}。\n")
    finally:
        sys.exit("程式結束，謝謝您的使用。\n")
