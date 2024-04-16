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


def save_data_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data has been written to {filename}")


def upload_file_to_s3(filepath, bucket_name, s3_directory):
    """Uploads a file to an S3 bucket."""
    s3_client = boto3.client('s3')
    s3_key = os.path.join(s3_directory, os.path.basename(filepath))
    print(f"Trying to upload {filepath} to {bucket_name} at {s3_key}")
    try:
        s3_client.upload_file(filepath, bucket_name, s3_key)
        print(f"Successfully uploaded")
    except Exception as e:
        print(f"Failed to upload {filepath}. Error: {str(e)}")


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
    # {
    #     "url": "https://www.moneydj.com/funddj/ya/YP051000.djhtm",
    #     "title_selector": "tr td.t3n1 a",
    #     "date_selector": "td[class*='t3n0c1']"
    # }
]

try:
    for site in sites_to_crawl:
        news_data.extend(fetch_news_titles(
            driver, site['url'], site['title_selector'], site['date_selector']))
finally:
    driver.quit()


def ensure_local_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


# Save the data to a JSON file and upload to S3
local_directory = 'json_files'
s3_directory = 'news_data'

ensure_local_directory_exists(local_directory)
filename = f'news_data_{today_file}.json'
local_filepath = os.path.join(local_directory, filename)

save_data_to_json(news_data, local_filepath)
upload_file_to_s3(local_filepath, BUCKET_NAME, s3_directory)


# # 使用jieba將新聞「標題」斷詞
# etf_title = [yahoo_title, ]


# # 使用wordcloud製作文字雲，STOPWORDS可以排除常見的無意義詞彙
# stopwords = set(STOPWORDS)
# stopwords.add("可以")
# stopwords.add("快訊")
# stopwords.add("新聞")
# stopwords.add("報導")
# stopwords.add("影音")
# stopwords.add("影片")
# stopwords.add("直播")
# stopwords.add("獨家")
# stopwords.add("專訪")
# stopwords.add("專家")

# cloud = WordCloud(width=1000, stopwords=stopwords, height=500,
#                   max_words=20, background_color='white').generate(cut_text)
# plt.imshow(cloud)
# plt.axis
# plt.show()
# cloud.to_file('wordcloud.png')
