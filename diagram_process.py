# 台鐵資料轉換後繪製程序

# 自訂class與module
import environment_variable as ev
import diagram as dm

Globals = ev.Singleton_GlobalVariables_Instance

def Draw(all_trains, location, date):

    offset = Globals.DiagramHours[0] * 600  # 將整個圖形往左移動的距離

    diagrams = {}

    for key, value in Globals.LinesDiagramSetting.items():
        diagrams[key] = dm.Diagram(Globals.LinesStationsForBackground[key],
                                    location + value[0],
                                    date,
                                    value[1],
                                    1200 * (len(Globals.DiagramHours) - 1) + 100,
                                    value[2],
                                    Globals.DiagramHours)

    # 各車次線路徑的轉換
    for line_kind, train_id, car_class, line_dir, over_night_stn, option_id, train_time_space in all_trains:
        set_train_path(line_kind, train_id, car_class, offset, option_id, train_time_space, diagrams)

    for key, value in diagrams.items():
        value.save_file()

# 轉換車次線路徑
def set_train_path(line_kind, train_id, car_class, offset, option_id, train_time_space, diagrams):

    color = Globals.CarKind.get(car_class, 'special')

    path = "M"

    for index, row in train_time_space.iterrows():
        if row['StopStation'] == "Y" or Globals.LinesStations[line_kind][row['StationID']][2] == "Y":
            # if row['StopStation'] == "Y" and lines_stations['']:
            x = round(row['Time'] * 10 + 50 - offset, 4)
            y = round(row['Loc'] + 50, 4)
            path += str(x) + ',' + str(y) + ' '

    diagrams[line_kind].draw_line(train_id, path, color, option_id)
