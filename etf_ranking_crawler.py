import ipdb
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import datetime
import re
import boto3
import os
from dotenv import load_dotenv
from database import get_db_connection

# Load environment variables from .env file
load_dotenv()

#####
s3 = boto3.client('s3',
                  aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                  aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                  region_name=os.getenv("S3_BUCKET_REGION"))
BUCKET_NAME = os.getenv("BUCKET_NAME")
#####
today = datetime.datetime.now().strftime("%Y/%m/%d")
today_file = datetime.datetime.now().strftime("%Y-%m-%d")


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


##### ETF Ranking Crawler #####
driver = webdriver.Chrome(service=ChromeService(
    ChromeDriverManager().install()))
driver.get('https://www.twse.com.tw/zh/ETFortune/index')

# first tab
first_tab = driver.find_element(
    By.CSS_SELECTOR, 'section#ranking.tabs > ul.nav > li')
first_tab.click()

WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
    (By.CSS_SELECTOR, 'div.pane.active table tr')))


def scrape_table_data():

    table = driver.find_element(By.CSS_SELECTOR, 'div.pane.active table')

    # Extract the headers
    headers = [header.text for header in table.find_elements(
        By.CSS_SELECTOR, 'thead th')]

    date_str = driver.find_element(
        By.CSS_SELECTOR, 'div.pane.active p').text
    date_match = re.search(r'\d{4}\.\d{2}\.\d{2}', date_str)
    if date_match:
        data_updated_date_before_formatting = date_match.group()
        data_updated_date = data_updated_date_before_formatting.replace(
            '.', '/')
    crawler_date = today

    ranking_data = []
    rows = table.find_elements(By.CSS_SELECTOR, 'tbody tr')

    for row in rows:
        cols = row.find_elements(By.CSS_SELECTOR, 'td')
        if cols:
            row_data = {headers[i]: cols[i].text for i in range(len(cols))}
            row_data['data_updated_date'] = data_updated_date
            row_data['crawler_date'] = crawler_date
            ranking_data.append(row_data)

    return ranking_data


data1 = scrape_table_data()
clean_data1 = []

for item in data1:
    item_clean = {key: value.replace(
        ',', '') if "成交" in key else value for key, value in item.items()}
    clean_data1.append(item_clean)

# print(clean_data1)

# second tab
second_tab = driver.find_element(
    By.CSS_SELECTOR, 'section#ranking.tabs > ul.nav > li:nth-child(2)')
second_tab.click()
data2 = scrape_table_data()
clean_data2 = []
for item in data2:
    item_clean = {key: value.replace(
        ',', '') if "今" in key else value for key, value in item.items()}
    clean_data2.append(item_clean)

# print(clean_data2)

# third tab
third_tab = driver.find_element(
    By.CSS_SELECTOR, 'section#ranking.tabs > ul.nav > li:nth-child(3)')
third_tab.click()
data3 = scrape_table_data()
clean_data3 = []
for item in data3:
    item_clean = {key: value.replace(
        ',', '') if "人" in key else value for key, value in item.items()}
    clean_data3.append(item_clean)

# print(clean_data3)

# forth tab
fourth_tab = driver.find_element(
    By.CSS_SELECTOR, 'section#ranking.tabs > ul.nav > li:nth-child(4)')
fourth_tab.click()
data4 = scrape_table_data()
print(data4)
driver.quit()

# data mapping
data_table_mapping = [
    (clean_data1, 'etf_ranking_volume'),
    (clean_data2, 'etf_ranking_assets'),
    (clean_data3, 'etf_ranking_holders'),
    (data4, 'etf_ranking_performance')
]

field_mappings = {
    'etf_ranking_volume': {
        '排名': 'ranking',
        '股票代號': 'symbol',
        "ETF名稱": "etf_name",
        "今日成交值(元)": "today_deal_value",
        "日均成交值(元)(年初至今)": "avg_deal_value",
        "日均成交量(股)(年初至今)": "avg_deal_volume",
        "data_updated_date": "data_updated_date",
        "crawler_date": "crawler_date"
    },
    'etf_ranking_assets': {
        "排名": "ranking",
        "股票代號": "symbol",
        "ETF名稱": "etf_name",
        "今日資產規模(元)": "today_total_assets",
        "年初至今淨增減（新台幣）": "YTD_adjustment",
        "變動率": "adjustment_rate",
        "data_updated_date": "data_updated_date",
        "crawler_date": "crawler_date"
    },
    'etf_ranking_holders': {
        "排名": "ranking",
        "股票代號": "symbol",
        "ETF名稱": "etf_name",
        "受益人數(人)": "holders",
        "年初至今淨增減(人)": "YTD_adjustment",
        "變動率": "adjustment_rate",
        "data_updated_date": "data_updated_date",
        "crawler_date": "crawler_date"
    },
    'etf_ranking_performance': {
        "排名": "ranking",
        "股票代號": "symbol",
        "ETF名稱": "etf_name",
        "年初至今績效(%)": "YTD_performance_rate",
        "data_updated_date": "data_updated_date",
        "crawler_date": "crawler_date"
    }
}


def insert_data_to_db(data, table_name):
    connection = get_db_connection()
    if connection is None:
        print("Error: Could not connect to the database.")
        return
    field_mapping = field_mappings[table_name]
    if not field_mapping:
        print(f"Error: No field mapping found for table {table_name}")
        return
    try:
        with connection.cursor() as cursor:
            for item in data:
                mapped_item = {
                    field_mapping[key]: value for key, value in item.items() if key in field_mapping}
                columns = ', '.join(f"`{key}`" for key in mapped_item.keys())
                placeholders = ', '.join(['%s'] * len(mapped_item))
                sql = f"""INSERT INTO `{table_name}` ({columns}) VALUES ({
                    placeholders})"""
                cursor.execute(sql, list(mapped_item.values()))
        connection.commit()
    except Exception as e:
        print(f"Error inserting data to database: {e}")
    finally:
        if connection:
            connection.close()


# Save data to a JSON file
files_and_data = [
    (f'etf_ranking_volume_{today_file}.json', clean_data1),
    (f'etf_ranking_assets_{today_file}.json', clean_data2),
    (f'etf_ranking_holders_{today_file}.json', clean_data3),
    (f'etf_ranking_performance_{today_file}.json', data4)
]

# Loop through each pair, save to JSON, and upload to S3
for filename, data in files_and_data:
    save_data_to_json(data, filename)  # Save the data to a JSON file
    upload_file_to_s3(filename, BUCKET_NAME)  # Upload the file to S3
    table_name = filename.split(
        '_')[0]+'_'+filename.split('_')[1]+'_'+filename.split('_')[2]
    insert_data_to_db(data, table_name)
