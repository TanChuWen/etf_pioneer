import logging
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
from database import get_db_connection, insert_data_etf_ranking

# Load environment variables from .env file
load_dotenv()

##### logging  #####
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('etf_ranking_crawler.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.info('Start etf_ranking_crawler.py')


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
    logger.info(f"Data has been written to {filename}")


def upload_file_to_s3(filepath, bucket_name, s3_directory):
    """Uploads a file to an S3 bucket."""
    s3_client = boto3.client('s3')
    s3_key = os.path.join(s3_directory, os.path.basename(filepath))
    logger.info(f"Trying to upload {filepath} to {bucket_name} at {s3_key}")
    try:
        s3_client.upload_file(filepath, bucket_name, s3_key)
        logger.info(f"Successfully uploaded")
    except Exception as e:
        logger.error(f"Failed to upload {filepath}. Error: {str(e)}")


def ensure_local_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


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

# fourth tab
fourth_tab = driver.find_element(
    By.CSS_SELECTOR, 'section#ranking.tabs > ul.nav > li:nth-child(4)')
fourth_tab.click()
data4 = scrape_table_data()
driver.quit()

# data mapping
data_table_mapping = [
    (clean_data1, 'etf_ranking_volume'),
    (clean_data2, 'etf_ranking_assets'),
    (clean_data3, 'etf_ranking_holders'),
    (data4, 'etf_ranking_performance')
]


# Save data to a JSON file
files_and_data = [
    (f'etf_ranking_volume_{today_file}.json', clean_data1),
    (f'etf_ranking_assets_{today_file}.json', clean_data2),
    (f'etf_ranking_holders_{today_file}.json', clean_data3),
    (f'etf_ranking_performance_{today_file}.json', data4)
]


# Loop through each pair, save to JSON, and upload to S3
for filename, data in files_and_data:
    local_directory = 'json_files'
    ensure_local_directory_exists(local_directory)
    local_filepath = os.path.join(local_directory, filename)
    save_data_to_json(data, local_filepath)  # Save the data to JSON file

    # Determine the S3 directory based on the filename
    if 'volume' in filename:
        s3_directory = 'etf_ranking_volume'
    elif 'assets' in filename:
        s3_directory = 'etf_ranking_assets'
    elif 'holders' in filename:
        s3_directory = 'etf_ranking_holders'
    elif 'performance' in filename:
        s3_directory = 'etf_ranking_performance'
    else:
        s3_directory = 'other_data'

    # Upload the file to S3
    upload_file_to_s3(local_filepath, BUCKET_NAME,
                      s3_directory)  # Upload the file to S3

    # Insert the data into the database
    table_name = filename.split(
        '_')[0]+'_'+filename.split('_')[1]+'_'+filename.split('_')[2]
    insert_data_etf_ranking(
        clean_data1,  'etf_ranking_volume')
    insert_data_etf_ranking(
        clean_data2,  'etf_ranking_assets')
    insert_data_etf_ranking(
        clean_data3,  'etf_ranking_holders')
    insert_data_etf_ranking(data4, 'etf_ranking_performance')
