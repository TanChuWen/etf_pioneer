import ipdb
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s)
driver.get("https://tw.stock.yahoo.com/tw-etf/")

# Step 1: Store the original window handle
original_window = driver.current_window_handle


# wait for ETF list from all regions to be visible
WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
    (By.ID, "etf-overview-region")))
etf_data = []

# get all the tabs of different ETF regions
region_tabs = driver.find_elements(
    By.CSS_SELECTOR, "#etf-overview-region .tab-wrapper > button")

# mimic clicking on each tab to get the ETF list
for tab in region_tabs:
    driver.switch_to.window(original_window)
    # tabs = driver.find_elements(
    #     By.CSS_SELECTOR, "#etf-overview-region .tab-wrapper > button")
    tab.click()

    # wait for the ETF list of specific region to be visible
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, "div.table-body-wrapper")))

    # get all the ETFs in the list
    etf_elements = driver.find_elements(
        By.CSS_SELECTOR, "#etf-overview-region div.table-body-wrapper > ul > li a")

    for etf in etf_elements:
        driver.switch_to.window(original_window)
        etf.click()
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

        # Find the new window handle and switch to it
        new_window = None
        for handle in driver.window_handles:
            if handle != original_window:
                new_window = handle
                break
        driver.switch_to.window(new_window)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.ID, "main-0-QuoteHeader-Proxy")))

        name = driver.find_element(
            By.CSS_SELECTOR, "#main-0-QuoteHeader-Proxy h1").text
        symbol = driver.find_element(
            By.CSS_SELECTOR, "#main-0-QuoteHeader-Proxy span").text
        price = driver.find_elements(
            By.CSS_SELECTOR, "#main-0-QuoteHeader-Proxy span")[2].text
        up_down = ''
        up_down_class = driver.find_elements(
            By.CSS_SELECTOR, "#main-0-QuoteHeader-Proxy span")[2].get_attribute("class")
        if "trend-up" in up_down_class:
            up_down = "up"
        elif "trend-down" in up_down_class:
            up_down = "down"
        else:
            up_down = "no_change"
        up_down_change = driver.find_elements(
            By.CSS_SELECTOR, "#main-0-QuoteHeader-Proxy span")[3].text
        up_down_percentage = driver.find_elements(
            By.CSS_SELECTOR, "#main-0-QuoteHeader-Proxy span")[5].text

        etf_data.append({
            "name": name,
            "symbol": symbol,
            "price": price,
            "up_down": up_down,
            "up_down_percentage": up_down_percentage
        })

        driver.close()

print(etf_data)

driver.quit()

# 進到基本頁面，爬取最高管理費率、管理費率、保管費率
# 進到股利頁面，爬取股利發放資料
# 進到持股頁面，爬取前十大持股、行業類別、持股明細
# 進到績效表現頁面，爬取一週、一個月、三個月、六個月、今年至今、一年、兩年、三年、五年、十年的績效表現

####################
# ETF 名稱 V
# ETF 代號 V
# 今日股價 V
# 今日漲跌
# 最高管理費率、管理費率、保管費率

# 股利發放資料

# 前十大持股（這邊到時候要 join 股票代號）
# 行業類別
# 持股明細

# 績效表現（一週、一個月、三個月、六個月、今年至今、一年、兩年、三年、五年、十年）
