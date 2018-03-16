import sys
import os
from os import walk

#自訂class與module
import diagram as dg
import svg_save
import basic_data
from progessbar import progress

#台鐵運行圖 Python 版
version = '1.0b'
txt_output = ''

json_files = []

#程式執行段
print('台鐵JSON轉檔運行圖程式 - 版本：' + version + '\n')

for root, dirs, files in walk('JSON/'):
    for item in files:
        json_files.append(item)

for filename in json_files:
    
    if filename.split('.')[1] == 'json':
        txt_output += '台鐵JSON時刻表檔案日期：' + filename.split('.')[0] + '\n'
        count = 0
        
        try:
            data = dg.read_json(filename)
            trains = dg.find_trains(data, '') #特定車次的基本資料
            total = len(trains)
            
            # svg_output_WN = svg_save.Draw('/Library/WebServer/Documents/diagram/west_link_north/WESTNORTH_', filename.split('.')[0], 'LINE_WN', version, 3000)
            # svg_output_WS = svg_save.Draw('/Library/WebServer/Documents/diagram/west_link_south/WESTSOUTH_', filename.split('.')[0], 'LINE_WS', version, 3000)
            # svg_output_WM = svg_save.Draw('/Library/WebServer/Documents/diagram/west_link_moutain/WESTMOUNTAIN_', filename.split('.')[0], 'LINE_WM', version, 2000)
            # svg_output_WSEA = svg_save.Draw('/Library/WebServer/Documents/diagram/west_link_sea/WESTSEA_', filename.split('.')[0], 'LINE_WSEA', version, 2000)
            # svg_output_P = svg_save.Draw('/Library/WebServer/Documents/diagram/pingtung/PINGTUNG_', filename.split('.')[0], 'LINE_P', version, 2000)
            # svg_output_S = svg_save.Draw('/Library/WebServer/Documents/diagram/south_link/SOUTHLINK_', filename.split('.')[0], 'LINE_S', version, 2000)
            # svg_output_T = svg_save.Draw('/Library/WebServer/Documents/diagram/taitung/TAITUNG_', filename.split('.')[0], 'LINE_T', version, 2000)
            # svg_output_N = svg_save.Draw('/Library/WebServer/Documents/diagram/north_link/NORTHLINK_', filename.split('.')[0], 'LINE_N', version, 2000)
            # svg_output_I = svg_save.Draw('/Library/WebServer/Documents/diagram/yilan/YILAN_', filename.split('.')[0], 'LINE_I', version, 2000)
            # svg_output_PX = svg_save.Draw('/Library/WebServer/Documents/diagram/pingxi/PINGXI_', filename.split('.')[0], 'LINE_PX', version, 1250)
            # svg_output_NW = svg_save.Draw('/Library/WebServer/Documents/diagram/neiwan/NEIWAN_', filename.split('.')[0], 'LINE_NW', version, 1250)
            # svg_output_J = svg_save.Draw('/Library/WebServer/Documents/diagram/jiji/JIJI_', filename.split('.')[0], 'LINE_J', version, 1250)
            # svg_output_SL = svg_save.Draw('/Library/WebServer/Documents/diagram/shalun/SHALUN_', filename.split('.')[0], 'LINE_SL', version, 650)

            svg_output_WN = svg_save.Draw('', filename.split('.')[0], 'LINE_WN', version, 3000)
            svg_output_WS = svg_save.Draw('', filename.split('.')[0], 'LINE_WS', version, 3000)
            svg_output_WM = svg_save.Draw('', filename.split('.')[0], 'LINE_WM', version, 2000)
            svg_output_WSEA = svg_save.Draw('', filename.split('.')[0], 'LINE_WSEA', version, 2000)
            svg_output_T = svg_save.Draw('', filename.split('.')[0], 'LINE_T', version, 2000)
            svg_output_N = svg_save.Draw('', filename.split('.')[0], 'LINE_N', version, 2000)
            svg_output_I = svg_save.Draw('', filename.split('.')[0], 'LINE_I', version, 2000)
            svg_output_S = svg_save.Draw('', filename.split('.')[0], 'LINE_S', version, 2000)
            svg_output_P = svg_save.Draw('', filename.split('.')[0], 'LINE_P', version, 2000)
            svg_output_PX = svg_save.Draw('', filename.split('.')[0], 'LINE_PX', version, 1250)
            svg_output_NW = svg_save.Draw('', filename.split('.')[0], 'LINE_NW', version, 1250)
            svg_output_SL = svg_save.Draw('', filename.split('.')[0], 'LINE_SL', version, 650)
            svg_output_J = svg_save.Draw('', filename.split('.')[0], 'LINE_J', version, 650)
            
            for train_no in trains: #逐車次搜尋
                
                count += 1
                progress(count, total, '正在繪製日期：' + filename.split('.')[0] + '-車次：' + train_no['Train'])
                
                train_id = train_no['Train'] #車次號
                car_class = train_no['CarClass'] #車種
                line = train_no['Line'] #山線1、海線2、其他0
                over_night_stn = train_no['OverNightStn'] #跨午夜車站
                
                list_start_end_station = dg.find_train_stations(train_no) #查詢台鐵時刻表中，特定車次所有停靠車站

                list_passing_stations = dg.find_stations(list_start_end_station, train_no['Line'], train_no['LineDir']) #查詢特定車次所有停靠與通過車站

                nidmight_km = 0

                if over_night_stn != '0':
                    nidmight_km = dg.midnight_train(list_start_end_station, list_passing_stations, over_night_stn)
                
                train_time_space = dg.train_time_to_stations(list_start_end_station, list_passing_stations, nidmight_km) #估算特定車次通過車站通過時間


                svg_output_WN.draw_trains(train_time_space, train_id, car_class, line) 
                svg_output_WS.draw_trains(train_time_space, train_id, car_class, line) 
                svg_output_WM.draw_trains(train_time_space, train_id, car_class, line)
                svg_output_WSEA.draw_trains(train_time_space, train_id, car_class, line)
                svg_output_P.draw_trains(train_time_space, train_id, car_class, line)
                svg_output_S.draw_trains(train_time_space, train_id, car_class, line)
                svg_output_T.draw_trains(train_time_space, train_id, car_class, line) 
                svg_output_N.draw_trains(train_time_space, train_id, car_class, line)
                svg_output_I.draw_trains(train_time_space, train_id, car_class, line)
                svg_output_PX.draw_trains(train_time_space, train_id, car_class, line)
                svg_output_NW.draw_trains(train_time_space, train_id, car_class, line)
                svg_output_J.draw_trains(train_time_space, train_id, car_class, line)
                svg_output_SL.draw_trains(train_time_space, train_id, car_class, line)


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
        finally:
            txt_output += '完成 ok \n'

f = open('log.txt', 'w', encoding='utf-8')
f.write(txt_output)
f.close()
