# 台鐵運行圖 Python 版
import sys
import os
import io
import shutil

# 自訂class與module
import read_tra_json as tra_json
import diagram as dg
import svg_save
from progessbar import progress

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
version = '1.0b4'

# 程式執行段
def main(argv_json_location, argv_website_svg_location, argv_select_trains):

    txt_output = ''
    json_files = []

    check_output_folder(argv_website_svg_location)

    for root, dirs, files in os.walk(argv_json_location + '/'):
        for item in files:
            json_files.append(item)

    if len(json_files) != 0:
        for filename in json_files:            
            if filename.split('.')[1] == 'json':

                txt_output += '台鐵JSON時刻表檔案日期：' + filename.split('.')[0] + '\n'
                print('台鐵JSON時刻表檔案日期：' + filename.split('.')[0] + '\n')

                count = 0

                data = tra_json.read_json(filename)
                trains = tra_json.find_trains(data, argv_select_trains) # 特定車次的基本資料
                total = len(trains)

                website_svg_location = argv_website_svg_location

                svg_output_WN = svg_save.Draw(website_svg_location + '/west_link_north/WESTNORTH_', filename.split('.')[0], 'LINE_WN', version, 3000)
                svg_output_WS = svg_save.Draw(website_svg_location + '/west_link_south/WESTSOUTH_', filename.split('.')[0], 'LINE_WS', version, 4000)
                svg_output_WM = svg_save.Draw(website_svg_location + '/west_link_moutain/WESTMOUNTAIN_', filename.split('.')[0], 'LINE_WM', version, 2000)
                svg_output_WSEA = svg_save.Draw(website_svg_location + '/west_link_sea/WESTSEA_', filename.split('.')[0], 'LINE_WSEA', version, 2000)
                svg_output_P = svg_save.Draw(website_svg_location + '/pingtung/PINGTUNG_', filename.split('.')[0], 'LINE_P', version, 2000)
                svg_output_S = svg_save.Draw(website_svg_location + '/south_link/SOUTHLINK_', filename.split('.')[0], 'LINE_S', version, 2000)
                svg_output_T = svg_save.Draw(website_svg_location + '/taitung/TAITUNG_', filename.split('.')[0], 'LINE_T', version, 2000)
                svg_output_N = svg_save.Draw(website_svg_location + '/north_link/NORTHLINK_', filename.split('.')[0], 'LINE_N', version, 2000)
                svg_output_I = svg_save.Draw(website_svg_location + '/yilan/YILAN_', filename.split('.')[0], 'LINE_I', version, 2000)
                svg_output_PX = svg_save.Draw(website_svg_location + '/pingxi/PINGXI_', filename.split('.')[0], 'LINE_PX', version, 1250)
                svg_output_NW = svg_save.Draw(website_svg_location + '/neiwan/NEIWAN_', filename.split('.')[0], 'LINE_NW', version, 1250)
                svg_output_J = svg_save.Draw(website_svg_location + '/jiji/JIJI_', filename.split('.')[0], 'LINE_J', version, 1250)
                svg_output_SL = svg_save.Draw(website_svg_location + '/shalun/SHALUN_', filename.split('.')[0], 'LINE_SL', version, 650)

                # 逐車次搜尋
                for train_no in trains:

                    count += 1


                    train_id = train_no['Train'] # 車次號
                    car_class = train_no['CarClass'] # 車種
                    line = train_no['Line'] # 山線1、海線2、其他0
                    over_night_stn = train_no['OverNightStn'] # 跨午夜車站
                    line_dir = train_no['LineDir'] # 順逆行

                    progress(count, total, "目前正在轉換: 車次" + train_id)

                    list_start_end_station = dg.find_train_stations(train_no) # 查詢台鐵時刻表中，特定車次所有停靠車站

                    # print(list_start_end_station)

                    list_passing_stations = dg.find_stations(list_start_end_station, train_no['Line'], train_no['LineDir']) # 查詢特定車次所有停靠與通過車站

                    # print(list_passing_stations)

                    midnight_km = 0

                    if over_night_stn != '0':
                        midnight_km = dg.midnight_train(list_start_end_station, list_passing_stations, over_night_stn) # 跨夜車次處理

                    train_time_space = dg.train_time_to_stations(list_start_end_station, list_passing_stations, midnight_km) # 估算特定車次通過車站通過時間

                    temp = []

                    if 'End' in list_start_end_station: # 環島車次處理(例如51、52車次)，將停靠車站拆成三段分別處理(台北-八堵、八堵-竹南、竹南-台北)
                        temp = dg.roundabout_train(train_time_space, line_dir)
                    else:
                        temp.append(train_time_space)

                    # print(temp)
                    for item in temp:
                        svg_output_WN.draw_trains(item, train_id, car_class, line)
                        svg_output_WS.draw_trains(item, train_id, car_class, line)
                        svg_output_WM.draw_trains(item, train_id, car_class, line)
                        svg_output_WSEA.draw_trains(item, train_id, car_class, line)
                        svg_output_P.draw_trains(item, train_id, car_class, line)
                        svg_output_S.draw_trains(item, train_id, car_class, line)
                        svg_output_T.draw_trains(item, train_id, car_class, line)
                        svg_output_N.draw_trains(item, train_id, car_class, line)
                        svg_output_I.draw_trains(item, train_id, car_class, line)
                        svg_output_PX.draw_trains(item, train_id, car_class, line)
                        svg_output_NW.draw_trains(item, train_id, car_class, line)
                        svg_output_J.draw_trains(item, train_id, car_class, line)
                        svg_output_SL.draw_trains(item, train_id, car_class, line)


                txt_output += svg_output_WN.save()
                txt_output += svg_output_WS.save()
                txt_output += svg_output_WM.save()
                txt_output += svg_output_WSEA.save()
                txt_output += svg_output_P.save()
                txt_output += svg_output_S.save()
                txt_output += svg_output_T.save()
                txt_output += svg_output_N.save()
                txt_output += svg_output_I.save()
                txt_output += svg_output_PX.save()
                txt_output += svg_output_NW.save()
                txt_output += svg_output_J.save()
                txt_output += svg_output_SL.save()

                txt_output += '完成 ok \n'
                print("\n")
                print("檔案轉換完成！所有車次數量：" + str(total) + "，已轉換車次數量：" + str(count) + "，無法轉換車次數量：" + str(total - count)+ '\n')

                if os.path.exists('JSON/' + filename):
                    shutil.move('JSON/' + filename, 'JSON_BACKUP/' + filename)
    else:
        print('無法執行！原因為沒有讀取到 JSON 檔案。\n')

    f = open('log.txt', 'w', encoding='utf-8')
    f.write(txt_output)
    f.close()

def check_output_folder(path):
    folders = ['west_link_north', 'west_link_south', 'west_link_moutain', 'west_link_sea',
               'pingtung', 'south_link', 'taitung', 'north_link', 'yilan',
               'pingxi', 'neiwan', 'jiji', 'shalun']

    output_folder = os.listdir(path)

    diff = list(set(folders).difference(set(output_folder)))

    if len(diff) > 0:
        for item in diff:
            os.makedirs(path + '/' + item)


# def traceback(err):
#     #now = time.strftime('%H:%M:%S', time.localtime(time.time()))
#     traceback = sys.exc_info()[2]
#     print(err, 'exception in line', traceback.tb_lineno)

if __name__ == "__main__":
    Parameters = [] # 參數集：參數1: JSON 檔位置, 參數2: 運行圖檔案存檔位置, 參數3: 特定車次繪製

    print('************************************')
    print('台鐵JSON轉檔運行圖程式 - 版本：' + version)
    print('************************************\n')

    if len(sys.argv) == 4:
        Parameters.append(sys.argv[1])
        Parameters.append(sys.argv[2])
        Parameters.append(sys.argv[3])
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
        else:
            Parameters.append('')

    if Parameters[2] == 'ALL':
        Parameters[2] = ''

    main(Parameters[0], Parameters[1], Parameters[2])
