import logging
import re
import sys
import time
import urllib3
from pathlib import Path
from typing import List, Tuple, Optional
from urllib.parse import unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter


BASE_URL = "https://ods.railway.gov.tw"
LIST_URL = urljoin(BASE_URL, "/tra-ods-web/ods/download/dataResource/railway_schedule/JSON/list/")

DOWNLOAD_DIR = Path("downloads")
USER_AGENT = "TRA-json-downloader/1.0"

REQUEST_TIMEOUT = (10, 30)
DOWNLOAD_DELAY_SECONDS = 1

# 該站 SSL 驗證容易失敗，直接關閉
VERIFY_SSL = False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def create_session() -> requests.Session:
    """建立可重複使用的 HTTP Session。"""
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    # SSL 已關閉，因此不另外做 retry，避免出現無意義重試訊息
    adapter = HTTPAdapter(max_retries=0)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


def sanitize_filename(name: str) -> str:
    """清理檔名中的非法字元。"""
    sanitized = re.sub(r'[\\/*?:"<>|]', "_", name).strip()
    return sanitized or "download.json"


def resolve_filename(response: requests.Response, fallback_name: str) -> str:
    """
    解析最終檔名，優先順序如下：
    1. Content-Disposition filename*
    2. Content-Disposition filename
    3. fallback_name
    4. URL path 最後一段
    """
    content_disposition = response.headers.get("Content-Disposition", "")

    filename_star_match = re.search(
        r"filename\*\s*=\s*([^']*)''([^;]+)",
        content_disposition,
        flags=re.IGNORECASE,
    )
    if filename_star_match:
        return sanitize_filename(unquote(filename_star_match.group(2)))

    filename_match = re.search(
        r'filename\s*=\s*"?(?P<name>[^";]+)"?',
        content_disposition,
        flags=re.IGNORECASE,
    )
    if filename_match:
        return sanitize_filename(filename_match.group("name"))

    if fallback_name:
        return sanitize_filename(fallback_name)

    url_name = Path(urlparse(response.url).path).name
    return sanitize_filename(url_name or "download.json")


def is_json_link(url: str, label: str) -> bool:
    """判斷是否為 JSON 檔案連結。"""
    path_name = Path(urlparse(url).path).name.lower()
    label_name = label.lower()
    return path_name.endswith(".json") or label_name.endswith(".json")


def fetch_download_links(session: requests.Session, url: str) -> List[Tuple[str, str]]:
    """抓取頁面上的 JSON 下載連結清單。"""
    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT, verify=VERIFY_SSL)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.error("無法讀取清單頁面 %s：%s", url, exc)
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    seen_urls = set()
    links: List[Tuple[str, str]] = []

    for anchor in soup.find_all("a", href=True):
        href = urljoin(BASE_URL, anchor["href"])
        file_name = anchor.get_text(strip=True) or Path(urlparse(href).path).name

        if not is_json_link(href, file_name):
            continue
        if href in seen_urls:
            continue

        seen_urls.add(href)
        links.append((file_name, href))

    return links


def parse_selection(selection: str, max_index: int) -> Optional[List[int]]:
    """
    解析使用者輸入的編號選擇。
    支援：
    - Enter：全部
    - q / quit / exit：離開
    - 1,3,5
    - 1-5
    - 1-3,8,10
    """
    raw = selection.strip().lower()

    if raw in {"q", "quit", "exit"}:
        return None

    if not raw:
        return list(range(1, max_index + 1))

    result = set()

    try:
        for part in selection.split(","):
            part = part.strip()
            if not part:
                continue

            if "-" in part:
                start_text, end_text = part.split("-", 1)
                start = int(start_text.strip())
                end = int(end_text.strip())

                if start > end:
                    start, end = end, start

                for i in range(start, end + 1):
                    if 1 <= i <= max_index:
                        result.add(i)
            else:
                value = int(part)
                if 1 <= value <= max_index:
                    result.add(value)
    except ValueError:
        return []

    return sorted(result)


def choose_files(items: List[Tuple[str, str]]) -> Optional[List[Tuple[str, str]]]:
    """列出可下載檔案，並讓使用者選擇。"""
    print("\n可下載檔案：\n")

    for i, (name, _) in enumerate(items, 1):
        print(f"{i:3d}. {name}")

    print("\n輸入要下載的編號")
    print("例如：1-5 或 1,3,8")
    print("直接按 Enter = 全部下載")
    print("輸入 q = 離開程式")

    while True:
        selection = input("\n選擇: ")
        indexes = parse_selection(selection, len(items))

        if indexes is None:
            return None

        if not indexes:
            print("輸入格式不正確，請重新輸入。")
            continue

        return [items[i - 1] for i in indexes]


def ask_overwrite(file_name: str, apply_all_mode: Optional[str]) -> Tuple[Optional[bool], Optional[str]]:
    """
    詢問是否覆蓋既有檔案。

    回傳：
    - (True, mode)  -> 覆蓋
    - (False, mode) -> 略過
    - (None, mode)  -> 離開程式

    mode 可為：
    - None：尚未套用整批模式
    - "overwrite_all"：全部覆蓋
    - "skip_all"：全部略過
    """
    if apply_all_mode == "overwrite_all":
        return True, apply_all_mode

    if apply_all_mode == "skip_all":
        return False, apply_all_mode

    while True:
        print(f"\n檔案已存在：{file_name}")
        answer = input("是否覆蓋？[y]是 [n]否 [a]全部覆蓋 [s]全部略過 [q]離開：").strip().lower()

        if answer == "y":
            return True, apply_all_mode
        if answer == "n":
            return False, apply_all_mode
        if answer == "a":
            return True, "overwrite_all"
        if answer == "s":
            return False, "skip_all"
        if answer == "q":
            return None, apply_all_mode

        print("輸入無效，請重新輸入。")


def get_remote_filename(session: requests.Session, file_name: str, file_url: str) -> str:
    """
    先嘗試取得實際檔名，用來比對本機 downloads 是否已有同名檔案。
    若無法提前判斷，就退回頁面上的檔名或 URL 檔名。
    """
    try:
        with session.get(file_url, stream=True, timeout=REQUEST_TIMEOUT, verify=VERIFY_SSL) as response:
            response.raise_for_status()
            return resolve_filename(
                response,
                file_name or Path(urlparse(file_url).path).name,
            )
    except requests.RequestException:
        return sanitize_filename(file_name or Path(urlparse(file_url).path).name)


def download_file(
    session: requests.Session,
    file_name: str,
    file_url: str,
    overwrite: bool = False,
) -> bool:
    """
    下載單一檔案。
    overwrite=False 時，若已有同名檔案會直接跳過。
    overwrite=True 時，會覆蓋既有檔案。
    """
    temp_path = None

    try:
        with session.get(file_url, stream=True, timeout=REQUEST_TIMEOUT, verify=VERIFY_SSL) as response:
            response.raise_for_status()

            target_name = resolve_filename(
                response,
                file_name or Path(urlparse(file_url).path).name,
            )

            save_path = DOWNLOAD_DIR / target_name
            temp_path = save_path.with_suffix(save_path.suffix + ".part")

            DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

            if save_path.exists() and not overwrite:
                logger.info("已存在，跳過：%s", target_name)
                return False

            with temp_path.open("wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            temp_path.replace(save_path)
            logger.info("下載完成：%s", target_name)
            return True

    except requests.RequestException as exc:
        logger.error("下載失敗 %s：%s", file_url, exc)

    except OSError as exc:
        logger.error("寫入失敗 %s：%s", file_url, exc)

    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink(missing_ok=True)

    return False


def main() -> int:
    logger.warning("目前使用 verify=False，僅建議用於該站 SSL 驗證異常時。")

    session = create_session()
    items = fetch_download_links(session, LIST_URL)

    if not items:
        logger.error("沒有找到可下載檔案。")
        return 1

    logger.info("找到 %d 個 JSON 檔案", len(items))

    selected = choose_files(items)
    if selected is None:
        print("\n已取消，程式結束。")
        return 0

    print(f"\n準備處理 {len(selected)} 個檔案。")

    overwrite_mode: Optional[str] = None
    downloaded_count = 0
    skipped_count = 0

    for file_name, file_url in selected:
        remote_name = get_remote_filename(session, file_name, file_url)
        local_path = DOWNLOAD_DIR / remote_name

        overwrite = False

        if local_path.exists():
            decision, overwrite_mode = ask_overwrite(remote_name, overwrite_mode)

            if decision is None:
                print("\n使用者取消，程式結束。")
                return 0

            if decision is False:
                logger.info("略過既有檔案：%s", remote_name)
                skipped_count += 1
                continue

            overwrite = True

        ok = download_file(session, file_name, file_url, overwrite=overwrite)
        if ok:
            downloaded_count += 1
        else:
            skipped_count += 1

        time.sleep(DOWNLOAD_DELAY_SECONDS)

    print("\n全部完成。")
    print(f"下載完成：{downloaded_count} 個")
    print(f"略過/失敗：{skipped_count} 個")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())