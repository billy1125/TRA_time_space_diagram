from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import urllib.request
import zipfile
import os
import sys
import ssl


def main():
    ssl._create_default_https_context = ssl._create_unverified_context
    r = urllib.request.urlopen('https://google.com')
    print(r.status)
    print(r)

def read_url(url):
    url_json = []

    url = url.replace(" ","%20")
    req = Request(url)
    a = urlopen(req).read()
    soup = BeautifulSoup(a, 'html.parser')
    x = (soup.find_all('a'))
    for i in x:
        file_name = i.extract().get_text()
        xx = 'https://ods.railway.gov.tw' + i.extract().get('href')
        # print(file_name)
        url_new = url + file_name
        url_new = url_new.replace(" ","%20")
        if(file_name[-1]=='/' and file_name[0]!='.'):
            read_url(url_new)
        url_json.append([url_new, file_name, xx])

    return url_json

def download_tra_json(url_json):

##    strUrl = 'http://163.29.3.98/json/'
##    strFileExtent = '.zip'
##    strdate = str_date
##
##    strFullUrl = strUrl + strdate + strFileExtent #完整網址
##    strZipFile = str_date + strFileExtent #檔案名稱
##
    strLog =''
    
    try:
        #strLog += '下載XML\n'
        urllib.request.urlretrieve(url_json[2], url_json[1])

        if os.path.exists(url_json[1]):
            strLog += '下載成功' + '\n'
        else:
            strLog += '下載失敗' + '\n'


       # strLog += '解壓縮XML\n'
       #  zip_ref = zipfile.ZipFile(url_json[1], 'r')
       #  zip_ref.extractall()
       #  zip_ref.close()




        # if os.path.exists(url_json[1]):
        #     strLog += '已刪除' + url_json[1] + '\n'
        #     os.remove(url_json[1])
        # else:
        #     strLog += '沒有' + url_json[1] + '\n'

            
    except OSError as err:
        strLog += "OS error: {0}".format(err) + '\n'
    except ValueError:
        strLog += "Could not convert data to an integer." + '\n'
    except:
        strLog += "Unexpected error:", sys.exc_info()[0] + '\n'
        
if __name__ == '__main__':
    main()

# items = read_url("https://ods.railway.gov.tw/tra-ods-web/ods/download/dataResource/railway_schedule/JSON/list")
items = read_url("https://ods.railway.gov.tw/tra-ods-web/ods/download/dataResource/railway_schedule/JSON/list/")
# last_file_number = len(items) - 3
# download_tra_json(items[last_file_number])
# download_tra_json(items[1])

for item in read_url("https://ods.railway.gov.tw/tra-ods-web/ods/download/dataResource/railway_schedule/JSON/list/"):
    print(item[2])
    download_tra_json(item)
