import ipdb
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import json
import datetime
import re
import boto3
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

#####
s3 = boto3.client('s3',
                  aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                  aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                  region_name=os.getenv("S3_BUCKET_REGION"))
BUCKET_NAME = os.getenv("BUCKET_NAME")
#####


def save_data_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data has been written to {filename}")


def upload_file_to_s3(filename, BUCKET_NAME):
    """Uploads a file to an S3 bucket."""
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(filename, BUCKET_NAME, filename)
        print(f"Successfully uploaded {filename} to S3 bucket {BUCKET_NAME}")
    except Exception as e:
        print(f"Failed to upload {filename}. Error: {str(e)}")


performance_map = [
    "1_week",
    "1_month",
    "3_month",
    "6_month",
    "YTD",
    "1_year",
    "2_year",
    "3_year",
    "5_year",
    "10_year"]


driver = webdriver.Chrome(service=ChromeService(
    ChromeDriverManager().install()))
driver.get("https://tw.stock.yahoo.com/tw-etf/")

etf_data = []
etf_performance = []
etf_industry = []
etf_stock_composition = []
today = datetime.datetime.now().strftime("%Y/%m/%d")
today_file = datetime.datetime.now().strftime("%Y-%m-%d")

# Step 1: Store the original window handle
original_window = driver.current_window_handle


# wait for ETF list from all regions to be visible
WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
    (By.ID, "etf-overview-region")))


# get all the tabs of different ETF regions
region_tabs = driver.find_elements(
    By.CSS_SELECTOR, "#etf-overview-region .tab-wrapper > button")
region_tabs_len = len(region_tabs)

# mimic clicking on each tab to get the ETF list
for idx in range(region_tabs_len):
    driver.switch_to.window(original_window)
    # wait for the tabs to be visible
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "#etf-overview-region .tab-wrapper > button")))
    region_tabs = driver.find_elements(
        By.CSS_SELECTOR, "#etf-overview-region .tab-wrapper > button")
    print(region_tabs[idx].text)
    region_tabs[idx].click()
    time.sleep(1)
    # wait for the ETF list of specific region to be visible
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, "div.table-body-wrapper")))

    # get all the ETFs in the list
    etf_elements = driver.find_elements(
        By.CSS_SELECTOR, "#etf-overview-region div.table-body-wrapper > ul > li a")
    etf_limit = 2
    for etf in etf_elements:
        if etf_limit == 0:
            break
        etf_limit -= 1
        each_etf = {}
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
        # symbol is the first span
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

        # get the up_down_percentage. If the up_down is no_change, then the up_down_percentage is "-".
        if up_down != "no_change":
            up_down_percentage = driver.find_elements(
                By.CSS_SELECTOR, "#main-0-QuoteHeader-Proxy span")[5].text
            match = re.search(r'\((\d+\.\d+%)', up_down_percentage)
            if match:
                up_down_percentage = match.group(1)
        else:
            up_down_percentage = "-"

        # if the up_down is down, then the up_down_change and up_down_percentage should be negative
        if up_down == "down":
            up_down_change = "-" + up_down_change
            up_down_percentage = "-" + up_down_percentage

        # get the data updated date
        data_updated_date_before_formatting = driver.find_element(
            By.CSS_SELECTOR, "#main-0-QuoteHeader-Proxy > div > div:nth-child(2) > div > span").text
        if data_updated_date_before_formatting:
            data_updated_date = data_updated_date_before_formatting.split('|')[
                1].strip(' 更新')
        else:
            data_updated_date = "NULL"

        each_etf = {
            "name": name,
            "symbol": symbol,
            "price": price,
            "up_down": up_down,
            "up_down_change": up_down_change,
            "up_down_percentage": up_down_percentage,
            "data_updated_date": data_updated_date,
            "crawler_date": today
        }
        etf_data.append(each_etf)
        print(each_etf)

        ### get the performance, industry and stock composition data ###
        full_symbol = driver.current_url.split('/')[-1]
        performance_url = f"https://tw.stock.yahoo.com/quote/{
            full_symbol}/performance"
        holding_url = f"https://tw.stock.yahoo.com/quote/{full_symbol}/holding"

        # get the performance data
        driver.get(performance_url)
        WebDriverWait(driver, 10).until(lambda d: "績效表現" in d.title)

        # get the data updated date
        try:
            elements_full_performance_update_date = driver.find_element(
                By.CSS_SELECTOR, "#main-2-QuotePerformance-Proxy > div > div > div:nth-child(2)")
            elements_performance_update_date = elements_full_performance_update_date.text.split()
            updated_date_performance = elements_performance_update_date[1]
        except NoSuchElementException:
            updated_date_performance = "NULL"

        try:
            performance_data_elements = driver.find_elements(
                By.CSS_SELECTOR, ".table-body-wrapper .table-row span[class*='trend']")
        except IndexError:
            etf_performance = []

        # etf performance data
        each_performance_data = {
            "symbol": symbol, "updated_date": updated_date_performance, "crawler_date": today}
        if performance_data_elements:
            for idx, each in enumerate(performance_data_elements):
                if "trend-up" in each.get_attribute("class"):
                    each_performance_data[performance_map[idx]] = each.text
                elif "trend-down" in each.get_attribute("class"):
                    each_performance_data[performance_map[idx]
                                          ] = "-" + each.text
                else:
                    each_performance_data[performance_map[idx]] = "NULL"

            etf_performance.append(each_performance_data)
            print(each_performance_data)
        else:
            etf_performance.append({
                "symbol": symbol,
                "1_week": "NULL",
                "1_month": "NULL",
                "3_month": "NULL",
                "6_month": "NULL",
                "YTD": "NULL",
                "1_year": "NULL",
                "2_year": "NULL",
                "3_year": "NULL",
                "5_year": "NULL",
                "10_year": "NULL",
                "updated_date": updated_date_performance,
                "crawler_date": today
            })
            print({
                "symbol": symbol,
                "1_week": "NULL",
                "1_month": "NULL",
                "3_month": "NULL",
                "6_month": "NULL",
                "YTD": "NULL",
                "1_year": "NULL",
                "2_year": "NULL",
                "3_year": "NULL",
                "5_year": "NULL",
                "10_year": "NULL",
                "updated_date": updated_date_performance,
                "crawler_date": today
            })

        ### get industry and stock composition data ###
        driver.get(holding_url)
        WebDriverWait(driver, 10).until(lambda d: "持股分析" in d.title)

        each_industry_data = {"symbol": symbol}

        # get the data updated date
        elements_full_industry_update_date = driver.find_elements(
            By.CSS_SELECTOR, "#main-2-QuoteHolding-Proxy span > time")
        if len(elements_full_industry_update_date) > 1:
            elements_industry_update_date = elements_full_industry_update_date[0].find_elements(
                By.CSS_SELECTOR, "span")
            updated_date_industry = elements_industry_update_date[2].text

        else:
            updated_date_industry = "NULL"

        try:
            # etf industry data. It is a list of industries and their ratios.
            etf_industry_data_elements = driver.find_elements(
                By.CSS_SELECTOR, "#main-2-QuoteHolding-Proxy > div > div:nth-child(2) > div:nth-child(2) ul li[class*='link-text']")
        except IndexError:
            # The industry list is not present
            etf_industry_data_elements = []

        # Regular expression pattern
        # (\D+)? - captures any non-digit characters, the industry name
        # (\d+\.\d+%) - captures the percentage which includes digits, a period, and ends with a %
        if etf_industry_data_elements:
            pattern = re.compile(r'(\D+)(\d+\.\d+%)')
            for element in etf_industry_data_elements:
                text = element.text
                # Use re.match to find matches
                match = pattern.match(text)

                if match:
                    # Removes any potential leading/trailing whitespace
                    industry = match.group(1).strip()
                    ratio = match.group(2)

                    etf_industry.append({
                        "symbol": symbol,
                        "industry": industry,
                        "ratio": ratio,
                        "crawler_date": today,
                        "updated_date": updated_date_industry
                    })
                    print({
                        "symbol": symbol,
                        "industry": industry,
                        "ratio": ratio,
                        "crawler_date": today,
                        "updated_date": updated_date_industry
                    })
        else:
            etf_industry.append({
                "symbol": symbol,
                "industry": "NULL",
                "ratio": "NULL",
                "crawler_date": today,
                "updated_date": updated_date_industry
            })
            print({
                "symbol": symbol,
                "industry": "NULL",
                "ratio": "NULL",
                "crawler_date": today,
                "updated_date": updated_date_industry
            })

        # etf top 10 stock composition data
        each_stock_composition_data = {"symbol": symbol}

        elements_full_stock_composition_date = driver.find_elements(
            By.CSS_SELECTOR, "#main-2-QuoteHolding-Proxy span > time")
        if len(elements_full_stock_composition_date) > 2:
            elements_stock_composition_date = elements_full_stock_composition_date[
                2].find_elements(By.CSS_SELECTOR, "span")
            updated_date_stock_composition = elements_stock_composition_date[2].text

        else:
            updated_date_stock_composition = "NULL"

        try:
            # etf stock composition data. It is a list of top10 stock and their ratios.
            etf_stock_composition_data_elements = driver.find_elements(
                By.CSS_SELECTOR, "#main-2-QuoteHolding-Proxy > div > div:nth-child(4) > div:nth-child(2) ul li[class*='link-text']")
        except IndexError:
            # The stock composition list is not present
            etf_stock_composition_data_elements = []

        # Check if etf_stock_composition_data_elements is not empty
        if etf_stock_composition_data_elements:
            # Regular expression pattern
            # ^ asserts the position at the start of a line (due to the re.MULTILINE flag)
            # (\d+) captures one or more digits (the ranking)
            # \. matches the literal period following the ranking
            # \s* matches any amount of whitespace (space, tabs, etc.)
            # (.+?) non-greedily captures one or more of any character except newline (the company name)
            # The ? makes it non-greedy, so it stops at the first instance of following whitespace
            # \s+ matches one or more whitespace characters between the company name and the ratio
            # (\d+\.\d+%) captures the ratio, which is a sequence of digits, a decimal point, more digits, and a percent sign
            # $ asserts the position at the end of a line
            pattern = re.compile(
                r'^(\d+)\.\s*(.+?)\s+(\d+\.\d+%)$', re.MULTILINE)
            # This will create a list of tuples, where each tuple is (ranking, company, ratio)
            for element in etf_stock_composition_data_elements:
                text = element.text
                match = pattern.match(text)
                if match:
                    ranking = match.group(1).strip()
                    company = match.group(2).strip()
                    ratio = match.group(3).strip()

                    etf_stock_composition.append({
                        "symbol": symbol,
                        "ranking": ranking,
                        "company": company,
                        "ratio": ratio,
                        "crawler_date": today,
                        "updated_date": updated_date_stock_composition
                    })
                print({
                    "symbol": symbol,
                    "ranking": ranking,
                    "company": company,
                    "ratio": ratio,
                    "crawler_date": today,
                    "updated_date": updated_date_stock_composition
                })
        else:
            etf_stock_composition.append({
                "symbol": symbol,
                "ranking": "NULL",
                "company": "NULL",
                "ratio": "NULL",
                "crawler_date": today,
                "updated_date": updated_date_stock_composition
            })
            print({
                "symbol": symbol,
                "ranking": "NULL",
                "company": "NULL",
                "ratio": "NULL",
                "crawler_date": today,
                "updated_date": updated_date_stock_composition
            })

        ### organize the data ###

        # print(each_etf)
        # print(each_performance_data)
        # print(each_industry_data)
        driver.close()

# print(etf_data)

driver.quit()


files_and_data = [
    (f'etf_overview_data_{today_file}.json', etf_data),
    (f'etf_performance_data_{today_file}.json', etf_performance),
    (f'etf_industry_data_{today_file}.json', etf_industry),
    (f'etf_stock_composition_data_{today_file}.json', etf_stock_composition)
]

# Loop through each pair, save to JSON, and upload to S3
for filename, data in files_and_data:
    save_data_to_json(data, filename)  # Save the data to a JSON file
    upload_file_to_s3(filename, BUCKET_NAME)  # Upload the file to S3
