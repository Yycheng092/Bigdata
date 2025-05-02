from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time


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
    利用 Selenium 開啟指定的評論網址，嘗試點擊「顯示更多」後，
    以頁面上文字長度最大的 <p> 標籤作為影片簡介內容。
    若無法取得則回傳預設值：「（未找到簡介內容）」
    """
    print(f"🌐 擷取影片簡介網址：{url}")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # 關閉圖片載入，節省資源
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)
    summary = "（未找到簡介內容）"
    try:
        driver.get(url)

        # 若存在「顯示更多」的按鈕，嘗試點擊
        try:
            show_more_button = driver.find_element(
                By.CSS_SELECTOR, "span.css-1f3npvg")
            show_more_button.click()
            print("✅ 點擊了顯示更多按鈕，等待頁面加載...")
            time.sleep(1)  # 可加入短暫等待，以確保頁面資料更新
        except NoSuchElementException:
            print("⚠️ 找不到顯示更多按鈕，跳過點擊步驟。")

        if wait_for_desired_p(driver, timeout=10, min_length=20):
            all_p = driver.find_elements(By.CSS_SELECTOR, "p")
            if all_p:
                # 以文字長度最大的 <p> 作為影片簡介內容
                best_p = max(all_p, key=lambda x: len(x.text))
                summary = best_p.text.strip()
                print("✅ 成功抓取影片簡介")
            else:
                print("❌ 頁面中未找到 <p> 標籤")
        else:
            print("⚠️ 等待 <p> 標籤載入逾時")
    except Exception as e:
        print(f"❌ 擷取簡介失敗（錯誤信息）：{repr(e)}")
    finally:
        driver.quit()
    return summary


# 主程式：抓取正在上映的電影資料並取得影片簡介
# -----------------------------------------------------------------------------
# 設定 ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# 設定目標網址：正在上映
url = "https://today.line.me/tw/v2/movie/incinemas/playing"
driver.get(url)

# 等待網頁上所有電影項目加載
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_all_elements_located(
    (By.CSS_SELECTOR, '.detailListItem.movieListing-movie')))

# 抓取所有電影項目
movies = driver.find_elements(
    By.CSS_SELECTOR, '.detailListItem.movieListing-movie')

movie_data = []
for movie in movies:
    try:
        # 1. 取得電影名稱
        title = movie.find_element(
            By.CSS_SELECTOR, '.detailListItem-title').text.strip()

        # 2. 取得電影圖片 URL，從 data-src 屬性取得圖片連結
        img_elem = movie.find_element(
            By.CSS_SELECTOR, '.detailListItem-poster figure')
        img_url = img_elem.get_attribute('data-src')
        img_url = img_url.strip() if img_url else "No image found"

        # 3. 取得影片預告連結
        try:
            trailer_element = movie.find_element(
                By.CSS_SELECTOR, '.detailListItem-images a')
            trailer_relative_link = trailer_element.get_attribute("href")
            if trailer_relative_link.startswith("/"):
                trailer_link = "https://today.line.me" + trailer_relative_link
            else:
                trailer_link = trailer_relative_link
        except Exception:
            trailer_link = "No trailer link found"

        # 4. 取得放映時間和上映日期
        time_info = movie.find_element(
            By.CSS_SELECTOR, '.detailListItem-status span.text--ellipsis1').text.strip()
        parts = [part.strip() for part in time_info.split('•') if part.strip()]
        if len(parts) >= 2:
            show_time = parts[0]       # 例如 "2小時17分"
            release_time = parts[1]    # 例如 "2025年04月17日上映"
        else:
            show_time = None
            release_time = None

        # 5. 取得評論連結並組成評論網址
        # 此處利用 CSS Selector 擷取 href 屬性以 "/tw/v3/movie/" 開頭的 <a> 標籤
        try:
            review_element = movie.find_element(
                By.CSS_SELECTOR, "a[href^='/tw/v3/movie/']")
            comment_link = review_element.get_attribute("href")
            # 根據格式 "/tw/v3/movie/qokQmrK/1"
            parts_href = comment_link.rstrip("/").split("/")
            # 假設電影 ID 為倒數第二個位置
            movie_id = parts_href[-2] if len(parts_href) >= 2 else "unknown"
            review_url = f"https://today.line.me/tw/v3/movie/{movie_id}"
        except Exception as e:
            review_url = "No review link found"
            print("評論連結錯誤:", e)

        # 6. 利用 review_url 取得影片簡介
        summary = fetch_movie_summary_with_selenium(review_url)

        # 7. 將所有資料加入清單
        movie_data.append({
            'title': title,
            'img_url': img_url,
            'trailer_link': trailer_link,
            'show_time': show_time,
            'release_time': release_time,
            'review_url': review_url,
            'summary': summary
        })

    except Exception as e:
        print(f"其他錯誤: {e}")

# 列印所有取得的電影資料
for data in movie_data:
    print(f"電影名稱: {data['title']}")
    print(f"圖片網址: {data['img_url']}")
    print(f"預告連結: {data['trailer_link']}")
    print(f"放映時間: {data['show_time']}")
    print(f"上映時間: {data['release_time']}")
    print(f"評論網址: {data['review_url']}")
    print(f"影片簡介: {data['summary'][:150]}...\n")  # 只印前150字，方便檢查

# 關閉瀏覽器
driver.quit()
