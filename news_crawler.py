from dotenv import load_dotenv
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
import time
import json
import datetime
import re
import boto3
import os
from database import get_db_connection, insert_news_data
import logging

# Load environment variables from .env file
load_dotenv()

##### logging  #####
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('news_crawler.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.info('Start news_crawler.py')


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


driver = webdriver.Chrome(service=ChromeService(
    ChromeDriverManager().install()))

today = datetime.datetime.now().strftime('%Y/%m/%d')
today_file = datetime.datetime.now().strftime("%Y-%m-%d")

# standardize date format


def standardize_date(date_str):
    for fmt in ('%Y/%m/%d', '%Y-%m-%d', '%Y-%m-%d %H:%M', '%Y.%m.%d', '%m-%d', '%H:%M'):
        try:
            if fmt == "%Y/%m/%d":
                datetime.datetime.strptime(date_str, fmt)
                return date_str
            elif fmt in ("%m-%d", "%m/%d"):
                date_obj = datetime.datetime.strptime(date_str, fmt)
                current_year = datetime.datetime.now().year
                formatted_date_str = f"{
                    current_year}/{date_obj.month:02d}/{date_obj.day:02d}"
                return formatted_date_str
            elif fmt == "%H:%M":
                return today
            else:
                date_obj = datetime.datetime.strptime(date_str, fmt)
                return date_obj.strftime("%Y/%m/%d")
        except ValueError:
            continue
    return date_str


# define a function to get news titles


def fetch_news_titles(driver, url, title_selector, date_selector, link_selector):
    news_items = []
    try:
        driver.get(url)
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, title_selector)))
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, date_selector)))
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, link_selector)))

        title_elements = driver.find_elements(By.CSS_SELECTOR, title_selector)
        date_elements = driver.find_elements(By.CSS_SELECTOR, date_selector)
        link_elements = driver.find_elements(By.CSS_SELECTOR, link_selector)

        for title, date, link in zip(title_elements, date_elements, link_elements):

            news_item = {
                'news_title': title.text,
                'news_date': standardize_date(date.text),
                'website': url,
                'crawler_date': today,
                'news_link': link.get_attribute('href')
            }
            news_items.append(news_item)

    except TimeoutException:
        logger.error(f"Timeout while waiting for page to load: {url}")
    except Exception as e:
        logger.error(f"Error fetching news from {url}: {str(e)}")

    return news_items


news_data = []
sites_to_crawl = [
    {
        "url": "https://m.cnyes.com/news/cat/etf",
        "title_selector": ".tlhuwq2",
        "date_selector": ".n1hj6r9n",
        "link_selector": ".list-title > a"
    },
    {
        "url": "https://www.ctee.com.tw/wealth/etf",
        "title_selector": ".news-title",
        "date_selector": ".news-time",
        "link_selector": ".news-title > a"
    },
    {
        "url": "https://money.udn.com/search/tagging/1001/ETF",
        "title_selector": ".story__headline",
        "date_selector": ".story__content > time",
        "link_selector": ".story__content > a"
    }
]

try:
    for site in sites_to_crawl:
        news_data.extend(fetch_news_titles(
            driver, site['url'], site['title_selector'], site['date_selector'], site['link_selector']))
except Exception as e:
    logger.error(f"An error occurred: {str(e)}")
finally:
    driver.quit()


# Save the data to a JSON file and upload to S3
local_directory = 'json_files'
s3_directory = 'news_data'

ensure_local_directory_exists(local_directory)
filename = f'news_data_{today_file}.json'
local_filepath = os.path.join(local_directory, filename)

save_data_to_json(news_data, local_filepath)
upload_file_to_s3(local_filepath, BUCKET_NAME, s3_directory)

# Insert the news data into the database
connection = get_db_connection()
if connection:
    try:
        for news_item in news_data:
            insert_news_data(connection, news_item)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        connection.close()
