import csv

#處理所有基本資訊(Category.csv)
def category():
    category = []
    with open('CSV/Category.csv', newline='', encoding='utf8') as csvfile:

        reader = csv.reader(csvfile)

        for row in reader:
            category.append(row)

    return category

#處理所有車站基本資訊(Stations.csv)
def stations():
    stations = {}
    with open('CSV/Stations.csv', newline='', encoding='utf8') as csvfile:
        
        reader = csv.reader(csvfile)
        
        for row in reader:
        #print(row[0])
            stations[row[0]] = row
    
    return stations

#時間轉換(Locate.csv)
def time_loc():
    time_loc = {}
    with open('CSV/Locate.csv', newline='', encoding='big5') as csvfile:
        reader = csv.reader(csvfile)
        
        for row in reader:
        #print(row[0])
            time_loc[row[0]] = row[1]
    
    return time_loc