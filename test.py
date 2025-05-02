from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time


def fetch_movie_summary_v3(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        time.sleep(3)  # 確保 JS 載入，這邊可加長為 5

        wait = WebDriverWait(driver, 10)
        try:
            wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "article.synopsis p")))
            paragraph = driver.find_element(
                By.CSS_SELECTOR, "article.synopsis p")
            print("✅ 成功擷取簡介：\n", paragraph.text.strip())
        except TimeoutException:
            print("⚠️ 找不到 article.synopsis p，嘗試抓其他 p...")
            all_p = driver.find_elements(By.CSS_SELECTOR, "p")
            if all_p:
                best_p = max(all_p, key=lambda x: len(x.text))
                print("✅ 備援抓取到簡介：\n", best_p.text.strip())
            else:
                print("❌ 找不到任何 <p> 標籤。")

    except Exception as e:
        print(f"❌ 擷取失敗（完整錯誤）：{repr(e)}")

    finally:
        driver.quit()


# 測試網址
test_url = "https://today.line.me/tw/v3/movie/qokQmrK"
fetch_movie_summary_v3(test_url)
