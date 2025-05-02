from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import json
import time

CACHE_FILE = "movie_cache.json"


def load_cache():
    """載入快取資料"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ 快取格式錯誤，自動重建")
            return {}
    return {}


def save_cache(cache_data):
    """儲存快取資料"""
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)


# 讀取快取（僅供初步觀察）
cache = load_cache()
print("讀取到的快取資料：", cache)


def wait_for_desired_p(driver, timeout=10, min_length=20):
    """
    等待網頁上至少有一個 <p> 標籤，其文字內容長度達到指定閾值。
    成功則回傳 True，逾時則回傳 False。
    """
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: any(len(elem.text.strip()) >= min_length for elem in d.find_elements(
                By.CSS_SELECTOR, "p"))
        )
        return True
    except TimeoutException:
        return False


def fetch_movie_summary_with_selenium(url):
    """
    使用 Selenium 開啟指定網址並嘗試抓取電影簡介。
    如果點擊「顯示更多」後仍無法找到符合條件的 <p> 標籤，
    則回傳預設值：「（未找到簡介內容）」。
    """
    print(f"🌐 擷取簡介網址：{url}")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        # 嘗試點擊「顯示更多」按鈕（若存在）
        try:
            show_more_button = driver.find_element(
                By.CSS_SELECTOR, "span.css-1f3npvg")
            show_more_button.click()
            print("✅ 點擊了顯示更多按鈕，等待頁面加載...")
            time.sleep(1)  # 等待頁面更新
        except NoSuchElementException:
            print("⚠️ 找不到顯示更多按鈕，跳過點擊步驟。")

        # 等待 <p> 標籤載入且內容達到指定長度
        if wait_for_desired_p(driver, timeout=10, min_length=20):
            all_p = driver.find_elements(By.CSS_SELECTOR, "p")
            if all_p:
                # 以文字長度最大的 <p> 為影片簡介內容
                best_p = max(all_p, key=lambda x: len(x.text))
                summary = best_p.text.strip()
                print("✅ 成功抓取完整簡介：\n", summary)
            else:
                print("❌ 找不到任何 <p> 標籤。")
                summary = "（未找到簡介內容）"
        else:
            print("⚠️ 等待 <p> 標籤載入逾時，無法抓取簡介。")
            summary = "（未找到簡介內容）"

        return summary

    except Exception as e:
        return f"❌ 擷取簡介失敗（錯誤信息）：{repr(e)}"
    finally:
        driver.quit()


def crawl_movie_titles():
    """
    採用快取策略來避免重複爬取：
      1. 若快取存在，讀取快取資料。
      2. 對於快取中每筆電影資料，若簡介為「（未找到簡介內容）」，則重新爬取。
      3. 若無快取資料，則完整進行爬取。
    """
    # 先從快取中讀取資料
    cached_data = load_cache()
    if cached_data and len(cached_data) > 0:
        print("✅ 發現快取資料")
        updated = False
        for movie in cached_data:
            if movie.get("summary") == "（未找到簡介內容）":
                print(f"⚠️ 電影《{movie.get('title')}》的簡介無法取得，開始重新爬取...")
                attempts = 0
                max_attempts = 3
                new_summary = movie.get("summary")
                while new_summary == "（未找到簡介內容）" and attempts < max_attempts:
                    attempts += 1
                    print(f"🔄 重試第 {attempts} 次...")
                    new_summary = fetch_movie_summary_with_selenium(
                        movie.get("review_url"))
                if new_summary != "（未找到簡介內容）":
                    movie["summary"] = new_summary
                    updated = True
        if updated:
            save_cache(cached_data)
        return cached_data

    # 若快取無資料則從頭進行爬取
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)
    driver.get("https://today.line.me/tw/v2/movie/chart/trending")

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "li.detailList-item"))
        )
    except TimeoutException:
        print("⚠️ 等待電影項目逾時，可能網站改版或連線有問題。")
        driver.quit()
        return []

    results = []
    try:
        movie_items = driver.find_elements(
            By.CSS_SELECTOR, "li.detailList-item")
        print(f"🔍 找到 {len(movie_items)} 部電影，開始擷取...\n")
        for item in movie_items:
            try:
                title = item.find_element(
                    By.CSS_SELECTOR, "h2.detailListItem-title").text.strip()
                image = item.find_element(
                    By.CSS_SELECTOR, "figure.detailListItem-posterImage").get_attribute("data-src")
                trailer_link = item.find_element(
                    By.CSS_SELECTOR, "a.detailListItem-trailer").get_attribute("href")
                comment_link = item.find_element(
                    By.CSS_SELECTOR, "a[href*='/v2/comment/movie/']").get_attribute("href")
                movie_id = comment_link.rstrip("/").split("/")[-1]
                review_url = f"https://today.line.me/tw/v3/movie/{movie_id}"
                summary = fetch_movie_summary_with_selenium(review_url)
                attempts = 0
                max_attempts = 3
                while summary == "（未找到簡介內容）" and attempts < max_attempts:
                    attempts += 1
                    print(f"⚠️ 簡介未找到，重試第 {attempts} 次...")
                    summary = fetch_movie_summary_with_selenium(review_url)
                print(f"✅ 成功：《{title}》")
                print(f"🧠 影片簡介網址：{trailer_link}")
                print(f"📄 簡介（前150字）：{summary[:150]}...\n")
                results.append({
                    "title": title,
                    "image": image,
                    "link": trailer_link,
                    "review_url": review_url,
                    "summary": summary
                })
            except Exception as e:
                print(
                    f"⚠️ 單筆電影擷取失敗：《{title if 'title' in locals() else '未知電影'}》 -> {e}")
                continue
        save_cache(results)
        print(f"📝 資料已保存至 {CACHE_FILE} 檔案中")
    finally:
        driver.quit()
    return results


def crawl_incinemas_newrelease():
    """
    爬取「電影院新片」資料：
      從 https://today.line.me/tw/v2/movie/incinemas/newrelease
      取得每筆電影資料，包括電影名稱、圖片網址、預告連結、
      放映時間與上映日期，並返回結果清單。
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)
    url = "https://today.line.me/tw/v2/movie/incinemas/newrelease"
    driver.get(url)

    try:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, '.detailListItem.movieListing-movie')))
        movie_elements = driver.find_elements(
            By.CSS_SELECTOR, '.detailListItem.movieListing-movie')
        results = []
        for movie in movie_elements:
            try:
                title = movie.find_element(
                    By.CSS_SELECTOR, '.detailListItem-title').text.strip()
                img_elem = movie.find_element(
                    By.CSS_SELECTOR, '.detailListItem-poster figure')
                img_url = img_elem.get_attribute('data-src')
                img_url = img_url.strip() if img_url else "No image found"
                try:
                    trailer_element = movie.find_element(
                        By.CSS_SELECTOR, '.detailListItem-images a')
                    trailer_relative_link = trailer_element.get_attribute(
                        "href")
                    if trailer_relative_link.startswith("/"):
                        trailer_link = "https://today.line.me" + trailer_relative_link
                    else:
                        trailer_link = trailer_relative_link
                except Exception:
                    trailer_link = "No trailer link found"
                time_info = movie.find_element(
                    By.CSS_SELECTOR, '.detailListItem-status span.text--ellipsis1').text.strip()
                parts = [part.strip()
                         for part in time_info.split('•') if part.strip()]
                if len(parts) >= 2:
                    show_time = parts[0]
                    release_time = parts[1]
                else:
                    show_time = None
                    release_time = None

                results.append({
                    'title': title,
                    'img_url': img_url,
                    'trailer_link': trailer_link,
                    'show_time': show_time,
                    'release_time': release_time
                })
            except Exception as e:
                print(f"錯誤: {e}")
        return results
    finally:
        driver.quit()


def crawl_third_column_data():
    """
    從正在上映頁面抓取電影資料，並只回傳第三欄位所需的資訊：
      - 電影名稱 (title)
      - 電影封面 (image)
      - 上映日期 (release_time)
      - 影片簡介 (summary)
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)

    third_data = []
    try:
        url = "https://today.line.me/tw/v2/movie/incinemas/playing"
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, '.detailListItem.movieListing-movie'))
        )
        movies = driver.find_elements(
            By.CSS_SELECTOR, '.detailListItem.movieListing-movie')
        for movie in movies:
            try:
                # 取得電影名稱
                title = movie.find_element(
                    By.CSS_SELECTOR, '.detailListItem-title').text.strip()
                # 取得電影封面
                img_elem = movie.find_element(
                    By.CSS_SELECTOR, '.detailListItem-poster figure')
                img_url = img_elem.get_attribute('data-src')
                img_url = img_url.strip() if img_url else "No image found"
                # 取得上映資訊（透過分隔字串擷取第二部份）
                time_info = movie.find_element(
                    By.CSS_SELECTOR, '.detailListItem-status span.text--ellipsis1'
                ).text.strip()
                parts = [p.strip() for p in time_info.split('•') if p.strip()]
                release_time = parts[1] if len(parts) >= 2 else "未知"
                # 取得評論連結，以生成 review_url
                try:
                    review_element = movie.find_element(
                        By.CSS_SELECTOR, "a[href^='/tw/v3/movie/']")
                    comment_link = review_element.get_attribute("href")
                    parts_href = comment_link.rstrip("/").split("/")
                    movie_id = parts_href[-2] if len(
                        parts_href) >= 2 else "unknown"
                    review_url = f"https://today.line.me/tw/v3/movie/{movie_id}"
                except Exception as e:
                    review_url = "No review link found"
                    print("評論連結錯誤:", e)
                # 透過 review_url 取得影片簡介
                summary = fetch_movie_summary_with_selenium(review_url)
                third_data.append({
                    "title": title,
                    "image": img_url,
                    "release_time": release_time,
                    "summary": summary,
                    "review_url": review_url,
                })
            except Exception as e:
                print(f"擷取單筆電影資料失敗 -> {e}")
                continue
    finally:
        driver.quit()

    # 將第三欄資料存入 JSON 檔案
    output_filename = "third_column_data.json"
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(third_data, f, ensure_ascii=False, indent=2)
        print(f"✅ 資料成功儲存到 {output_filename}")
    except Exception as e:
        print(f"❌ 儲存 JSON 檔案失敗：{e}")

    return third_data


if __name__ == '__main__':
    # 測試各個爬蟲方法
    print("===== 電影聲量榜 =====")
    trending_movies = crawl_movie_titles()
    print(trending_movies)

    print("\n===== 電影院新片 =====")
    incinema_movies = crawl_incinemas_newrelease()
    print(incinema_movies)

    new_movies = crawl_incinemas_newrelease()
    for movie in new_movies:
        print(f"電影名稱: {movie['title']}")
        print(f"圖片網址: {movie['img_url']}")
        print(f"預告連結: {movie['trailer_link']}")
        print(f"放映時間: {movie['show_time']}")
        print(f"上映時間: {movie['release_time']}")
        print("\n")
