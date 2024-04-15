from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from wordcloud import WordCloud, STOPWORDS
from dotenv import load_dotenv
import time
import json
import datetime
import re
import boto3
import os


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
                return datetime.datetime.now().year + '/' + date_obj.strftime("%m/%d")
            elif fmt == "%H:%M":
                return today
            else:
                date_obj = datetime.datetime.strptime(date_str, fmt)
                return date_obj.strftime("%Y/%m/%d")
        except ValueError:
            continue
    return date_str


# define a function to get news titles


def fetch_news_titles(driver, url, title_selector, date_selector):
    news_items = []
    try:
        driver.get(url)
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, title_selector)))
        title_elements = driver.find_elements(By.CSS_SELECTOR, title_selector)
        date_elements = driver.find_elements(By.CSS_SELECTOR, date_selector)

        for title, date in zip(title_elements, date_elements):

            news_item = {
                'news_title': title.text,
                'news_date': standardize_date(date.text),
                'website': url,
                'crawler_date': today
            }
            news_items.append(news_item)

    except TimeoutException:
        print(f"Timeout while waiting for page to load: {url}")
    except Exception as e:
        print(f"Error fetching news from {url}: {str(e)}")

    return news_items


news_data = []
sites_to_crawl = [
    {
        "url": "https://m.cnyes.com/news/cat/etf",
        "title_selector": ".tlhuwq2",
        "date_selector": ".n1hj6r9n"
    },
    {
        "url": "https://www.ctee.com.tw/wealth/etf",
        "title_selector": ".news-title",
        "date_selector": ".news-time"
    },
    {
        "url": "https://money.udn.com/search/tagging/1001/ETF",
        "title_selector": ".story__headline",
        "date_selector": ".story__content > time"
    }

]

try:
    for site in sites_to_crawl:
        news_data.extend(fetch_news_titles(
            driver, site['url'], site['title_selector'], site['date_selector']))
finally:
    driver.quit()

filename = f'news_data_{today_file}.json'
save_data_to_json(news_data, filename)
upload_file_to_s3(filename, BUCKET_NAME)
