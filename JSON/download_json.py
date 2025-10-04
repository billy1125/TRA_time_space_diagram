import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time
import re
import urllib3

# 忽略 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://ods.railway.gov.tw"
LIST_URL = BASE_URL + "/tra-ods-web/ods/download/dataResource/railway_schedule/JSON/list/"

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)


def read_url(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        # verify=False 關閉 SSL 驗證
        resp = requests.get(url, headers=headers, timeout=10, verify=False)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"無法連線 {url}: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        file_name = a.get_text(strip=True)
        href = a["href"]

        if not href.startswith("http"):
            href = BASE_URL + href

        links.append((file_name if file_name else Path(href).name, href))

    return links


def sanitize_filename(name: str) -> str:
    """移除檔名裡不合法的字元"""
    return re.sub(r'[\\/*?:"<>|]', "_", name)


def download_file(file_name, file_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        # verify=False 關閉 SSL 驗證
        with requests.get(file_url, headers=headers, stream=True, timeout=20, verify=False) as r:
            r.raise_for_status()

            cd = r.headers.get("Content-Disposition")
            if cd and "filename=" in cd:
                new_file_name = cd.split("filename=")[-1].strip('"')
            else:
                new_file_name = file_name or Path(file_url).name

            new_file_name = sanitize_filename(new_file_name)
            save_path = DOWNLOAD_DIR / new_file_name

            if save_path.exists():
                print(f"已存在，跳過: {new_file_name}")
                return

            with open(save_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"下載完成: {new_file_name}")

    except requests.RequestException as e:
        print(f"下載失敗 {file_url}: {e}")


if __name__ == "__main__":
    items = read_url(LIST_URL)
    print(f"找到 {len(items)} 個連結")

    for file_name, file_url in items:
        download_file(file_name, file_url)
        time.sleep(2)  # 延遲避免伺服器過載
