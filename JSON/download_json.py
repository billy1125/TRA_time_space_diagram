from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import urllib.request
import zipfile
import os
import sys

def read_url(url):
    url_json = []

    url = url.replace(" ","%20")
    req = Request(url)
    a = urlopen(req).read()
    soup = BeautifulSoup(a, 'html.parser')
    x = (soup.find_all('a'))
    for i in x:
        file_name = i.extract().get_text()
        # print(file_name)
        url_new = url + file_name
        url_new = url_new.replace(" ","%20")
        if(file_name[-1]=='/' and file_name[0]!='.'):
            read_url(url_new)
        url_json.append([url_new, file_name])

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
        urllib.request.urlretrieve(url_json[0], url_json[1])

        if os.path.exists(url_json[1]):
            strLog += '下載成功' + '\n'
        else:
            strLog += '下載失敗' + '\n'


       # strLog += '解壓縮XML\n'
        zip_ref = zipfile.ZipFile(url_json[1], 'r')
        zip_ref.extractall()
        zip_ref.close()




        if os.path.exists(url_json[1]):
            strLog += '已刪除' + url_json[1] + '\n'
            os.remove(url_json[1])
        else:
            strLog += '沒有' + url_json[1] + '\n'

            
    except OSError as err:
        strLog += "OS error: {0}".format(err) + '\n'
    except ValueError:
        strLog += "Could not convert data to an integer." + '\n'
    except:
        strLog += "Unexpected error:", sys.exc_info()[0] + '\n'

items = read_url("http://163.29.3.98/json/")
last_file_number = len(items) - 2
download_tra_json(items[last_file_number])
download_tra_json(items[1])

##for item in read_url("http://163.29.3.98/json/"):
##    print(item[0])
##    download_tra_json(item)

