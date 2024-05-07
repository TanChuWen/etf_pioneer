from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from datetime import timedelta
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
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
import pymysql
from pymysql import Error
import requests
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
logger.info('Start etf_ranking_crawler.py')


#####
# Access environment variables
db_host = os.getenv("DB_HOST", "localhost")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME", "dev")

s3 = boto3.client('s3',
                  aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                  aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                  region_name=os.getenv("S3_BUCKET_REGION"))
BUCKET_NAME = os.getenv("BUCKET_NAME")
#####


def send_slack_message(message):
    load_dotenv()
    url = os.getenv("SLACK_WEBHOOK_URL")
    headers = {'Content-Type': 'application/json'}
    data = {'text': message}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Check for successful response
    if response.status_code == 200:
        logger.info("Message sent to Slack successfully!")
    else:
        logger.error(f"""Failed to send message. Status code: {
            response.status_code}, response text: {response.text}""")


def etf_ranking_crawler():
    today = datetime.datetime.now().strftime("%Y/%m/%d")
    today_file = datetime.datetime.now().strftime("%Y-%m-%d")

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--headless')
    options.add_argument('--disable-application-cache')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')

    remote_url = 'http://remote_chromedriver:4444/wd/hub'
    driver = webdriver.Remote(
        command_executor=remote_url, keep_alive=True, options=options)

    try:
        driver.get('https://www.twse.com.tw/zh/ETFortune/index')
        send_slack_message("Crawling ETF ranking data...")
        # first tab
        first_tab = driver.find_element(
            By.CSS_SELECTOR, 'section#ranking.tabs > ul.nav > li')
        first_tab.click()

        WebDriverWait(driver, 180).until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'div.pane.active table tr')))
        data1 = scrape_table_data(driver)
        clean_data1 = []

        for item in data1:
            item_clean = {key: value.replace(
                ',', '') if "成交" in key else value for key, value in item.items()}
            clean_data1.append(item_clean)

        # second tab
        second_tab = driver.find_element(
            By.CSS_SELECTOR, 'section#ranking.tabs > ul.nav > li:nth-child(2)')
        second_tab.click()
        data2 = scrape_table_data(driver)
        clean_data2 = []
        for item in data2:
            item_clean = {key: value.replace(
                ',', '') if "今" in key else value for key, value in item.items()}
            clean_data2.append(item_clean)

        # third tab
        third_tab = driver.find_element(
            By.CSS_SELECTOR, 'section#ranking.tabs > ul.nav > li:nth-child(3)')
        third_tab.click()
        data3 = scrape_table_data(driver)
        clean_data3 = []
        for item in data3:
            item_clean = {key: value.replace(
                ',', '') if "人" in key else value for key, value in item.items()}
            clean_data3.append(item_clean)

        # fourth tab
        fourth_tab = driver.find_element(
            By.CSS_SELECTOR, 'section#ranking.tabs > ul.nav > li:nth-child(4)')
        fourth_tab.click()
        data4 = scrape_table_data(driver)
        driver.quit()

        # # data mapping
        # data_table_mapping = [
        #     (clean_data1, 'etf_ranking_volume'),
        #     (clean_data2, 'etf_ranking_assets'),
        #     (clean_data3, 'etf_ranking_holders'),
        #     (data4, 'etf_ranking_performance')
        # ]

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
            # Save the data to JSON file
            save_data_to_json(data, local_filepath)

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
            # table_name = filename.split(
            # '_')[0]+'_'+filename.split('_')[1]+'_'+filename.split('_')[2]
            insert_data_etf_ranking(
                clean_data1,  'etf_ranking_volume')
            send_slack_message(f"Data for {filename} has been uploaded to S3.")

            insert_data_etf_ranking(
                clean_data2,  'etf_ranking_assets')
            send_slack_message(f"Data for {filename} has been uploaded to S3.")

            insert_data_etf_ranking(
                clean_data3,  'etf_ranking_holders')
            send_slack_message(f"Data for {filename} has been uploaded to S3.")

            insert_data_etf_ranking(data4, 'etf_ranking_performance')
            send_slack_message(f"Data for {filename} has been uploaded to S3.")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        send_slack_message(f"Error: {str(e)}")
    finally:
        driver.quit()


def save_data_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def upload_file_to_s3(filepath, bucket_name, s3_directory):
    s3 = boto3.client('s3',
                      aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                      aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                      region_name=os.getenv("S3_BUCKET_REGION"))

    BUCKET_NAME = os.getenv("BUCKET_NAME")

    """Uploads a file to an S3 bucket."""
    s3_client = boto3.client('s3')
    s3_key = os.path.join(s3_directory, os.path.basename(filepath))
    try:
        s3_client.upload_file(filepath, bucket_name, s3_key)
        logger.info(f"""Successfully uploaded {
                    filepath} to {bucket_name}/{s3_key}""")
        send_slack_message(f"""Successfully uploaded {
                           filepath} to {bucket_name}/{s3_key}""")
    except Exception as e:
        logger.error(f"Failed to upload {filepath}. Error: {str(e)}")
        send_slack_message(f"Failed to upload {filepath}. Error: {str(e)}")


def ensure_local_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def scrape_table_data(driver):
    today = datetime.datetime.now().strftime("%Y/%m/%d")

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


def get_db_connection():
    load_dotenv()
    db_host = os.getenv("DB_HOST", "localhost")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME", "dev")
    send_slack_message(f"""Connecting to database. {
                       db_host}, {db_user}, {db_name}""")

    try:
        connection = pymysql.connect(
            host=db_host,
            user=db_user,
            passwd=db_password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )

        logger.info("Connected to the database.")
        send_slack_message("Connected to the database.")
        return connection
    except pymysql.MySQLError as e:

        logger.error(f"Error connecting to the database: {e}")
        send_slack_message(f"Error connecting to the database: {e}")


# Insert data into ETF ranking tables


def insert_data_etf_ranking(data, table_name):

    # ETF ranking tables
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
    connection = get_db_connection()
    if connection is None:
        return None

    field_mapping = field_mappings.get(table_name, {})
    if not field_mapping:
        return None

    try:
        with connection.cursor() as cursor:
            columns_list = []
            placeholders_list = []
            updates_list = []
            values_to_insert = []

            if data:
                first_item_keys = data[0].keys()
                for key in field_mapping:
                    if key in first_item_keys:
                        db_column = f"`{field_mapping[key]}`"
                        columns_list.append(db_column)
                        placeholders_list.append("%s")
                        updates_list.append(
                            f"{db_column} = VALUES({db_column})")

            columns = ', '.join(columns_list)
            placeholders = ', '.join(placeholders_list)
            updates = ', '.join(updates_list)

            for item in data:
                row_values = []
                for key in field_mapping:
                    if key in item:
                        row_values.append(item[key])
                values_to_insert.append(tuple(row_values))

            sql_upsert = f"""
            INSERT INTO `{table_name}` ({columns})
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {updates}
            """

            cursor.executemany(sql_upsert, values_to_insert)
            logger.info(f"Data for {table_name} has been inserted.")
            send_slack_message(f"Data for {table_name} has been inserted.")

        connection.commit()

    except Exception as e:
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
    dag_id='etf_ranking_crawler_v9',
    schedule="40 6 * * *",  # Run the DAG at 6:40 AM UTC every day
    start_date=datetime.datetime(2024, 5, 1),
    default_args=default_args,
    catchup=False,
    tags=['ranking', 'crawler', 'etf', 'daily']
) as dag:
    task_start = EmptyOperator(
        task_id='task_start',
        dag=dag
    )
    task_end = EmptyOperator(
        task_id='task_end',
        dag=dag
    )

    task_run_etf_ranking_crawler = PythonOperator(
        task_id='etf_ranking_crawler',
        python_callable=etf_ranking_crawler,
        dag=dag
    )
    (
        task_start
        >> task_run_etf_ranking_crawler
        >> task_end
    )
