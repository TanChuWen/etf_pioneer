from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from datetime import timedelta
from dotenv import load_dotenv
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import json
import datetime
import re
import boto3
import os
import requests
import pymysql
from pymysql import Error
import logging

# Load environment variables from .env file
# load_dotenv()

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
# s3 = boto3.client('s3',
#                   aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
#                   aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
#                   region_name=os.getenv("S3_BUCKET_REGION"))
# BUCKET_NAME = os.getenv("BUCKET_NAME")

# Access environment variables
db_host = os.getenv("DB_HOST", "localhost")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME", "dev")

#####


def send_slack_message(message):
    load_dotenv()
    url = os.getenv("SLACK_WEBHOOK_URL")
    headers = {'Content-Type': 'application/json'}
    data = {'text': message}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Check for successful response
    if response.status_code == 200:
        logger.info(f"{message}")
    else:
        logger.error(f"""Failed to send message. Status code: {
            response.status_code}, response text: {response.text}""")


def news_crawler():
    load_dotenv()
    s3 = boto3.client('s3',
                      aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                      aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                      region_name=os.getenv("S3_BUCKET_REGION"))

    BUCKET_NAME = os.getenv("BUCKET_NAME")

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-application-cache')
    options.add_argument('--disable-gpu')

    remote_url = 'http://remote_chromedriver:4444/wd/hub'
    driver = webdriver.Remote(
        command_executor=remote_url, keep_alive=True, options=options)

    options.add_argument(
        "user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1")
    driver2 = webdriver.Remote(
        command_executor=remote_url, keep_alive=True, options=options)

    today = datetime.datetime.now().strftime('%Y/%m/%d')
    today_file = datetime.datetime.now().strftime("%Y-%m-%d")
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
        send_slack_message("News crawler started.")
        for site in sites_to_crawl:
            send_slack_message(f"Fetching news from {site['url']}")
            if site['url'] == "https://www.ctee.com.tw/wealth/etf":
                news_data.extend(fetch_news_titles(
                    driver2, site['url'], site['title_selector'], site['date_selector'], site['link_selector']))
            else:
                news_data.extend(fetch_news_titles(
                    driver, site['url'], site['title_selector'], site['date_selector'], site['link_selector']))
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        driver2.quit()
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
    for news_item in news_data:
        insert_news_data(news_item)
    send_slack_message("News crawler finished.")


def save_data_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logger.info(f"Data has been written to {filename}")


def upload_file_to_s3(filepath, bucket_name, s3_directory):
    load_dotenv()
    s3 = boto3.client('s3',
                      aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                      aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                      region_name=os.getenv("S3_BUCKET_REGION"))

    BUCKET_NAME = os.getenv("BUCKET_NAME")

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


# standardize date format


def standardize_date(date_str):
    today = datetime.datetime.now().strftime('%Y/%m/%d')
    for fmt in ('%Y/%m/%d', '%Y-%m-%d', '%Y-%m-%d %H:%M', '%Y.%m.%d', '%m-%d', '%H:%M'):
        try:
            if fmt == "%Y/%m/%d":
                datetime.datetime.strptime(date_str, fmt)
                return date_str
            elif fmt in ("%m-%d", "%m/%d"):
                date_obj = datetime.datetime.strptime(date_str, fmt)
                current_year = datetime.datetime.now().year
                formatted_date_str = (
                    f"{current_year}/"
                    f"{date_obj.month:02d}/"
                    f"{date_obj.day:02d}"
                )
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
    today = datetime.datetime.now().strftime('%Y/%m/%d')
    news_items = []
    try:
        driver.get(url)
        send_slack_message(f"""after get {url} {title_selector} {
                           date_selector} {link_selector}""")
        driver.switch_to.default_content()
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, title_selector)))
        send_slack_message(f"{title_selector} found")
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, date_selector)))
        send_slack_message(f"{date_selector} found")
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, link_selector)))
        send_slack_message(f"{link_selector} found")

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
            send_slack_message(f"""Found: {news_item['news_title']},{
                               news_item['news_link']}""")

    except TimeoutException:
        driver.get(url)
        logger.error(f"Timeout while waiting for page to load: {url}")
    except Exception as e:
        logger.error(f"Error fetching news from {url}: {str(e)}")

    send_slack_message(f"Finished fetching news from {url}")
    return news_items


def get_db_connection():
    load_dotenv()
    db_host = os.getenv("DB_HOST", "localhost")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME", "dev")
    # send_slack_message(f"""Connecting to database. {
    #                    db_host}, {db_user}, {db_name}""")
    try:
        connection = pymysql.connect(
            host=db_host,
            user=db_user,
            passwd=db_password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        # logger.info("Connected to database.")
        return connection
    except pymysql.MySQLError as e:
        logger.error(f"Error connecting to database: {e}")

# News data table


def insert_news_data(news_item):
    connection = get_db_connection()
    if connection is None:
        logger.error("Could not connect to the database.")
        return
    try:
        with connection.cursor() as cursor:
            if news_item['news_title'] is None or news_item['news_date'] is None or news_item['news_link'] is None:
                logger.error("Skipping invalid record.")
                return
            else:
                # Prepare the INSERT statement without the existence check.
                insert_query = """
                INSERT INTO news_data (news_title, news_date, website, crawler_date, news_link)
                VALUES (%s, STR_TO_DATE(%s, '%%Y/%%m/%%d'), %s, STR_TO_DATE(%s, '%%Y/%%m/%%d'), %s)
                """
                logger.info(f"Inserting: {news_item['news_title']}")
                send_slack_message(f"Inserting: {news_item['news_title']}")
                try:
                    # Attempt to insert the new record.
                    cursor.execute(
                        insert_query,
                        (
                            news_item['news_title'],
                            news_item['news_date'],
                            news_item['website'],
                            news_item['crawler_date'],
                            news_item['news_link']
                        )
                    )
                    connection.commit()
                    logger.info(f"Inserted: {news_item['news_title']}")
                except pymysql.err.IntegrityError as e:
                    # This block will be executed if a duplicate entry is attempted.
                    logger.info(f"""Skipped duplicate: {
                                news_item['news_title']}, Error: {e}""")
                    send_slack_message(f"""Skipped duplicate: {
                        news_item['news_title']}, Error: {e}""")
    except pymysql.MySQLError as e:
        logger.error(f"Unexpected error: {e}")
        # Rollback the transaction in case of any other error
        connection.rollback()
    finally:
        if connection:
            connection.close()


# DAG Configuration
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id='news_crawler_dag_v30',
    schedule="0 3 * * *",  # Run the DAG at 3:00 AM UTC every day
    start_date=datetime.datetime(2024, 5, 1),
    default_args=default_args,
    catchup=False,
    tags=['news', 'crawler', 'etf', 'daily']
) as dag:
    task_start = EmptyOperator(
        task_id='task_start',
        dag=dag
    )
    task_end = EmptyOperator(
        task_id='task_end',
        dag=dag
    )

    task_run_news_crawler = PythonOperator(
        task_id='news_crawler',
        python_callable=news_crawler,
        dag=dag
    )
    (
        task_start
        >> task_run_news_crawler
        >> task_end
    )
