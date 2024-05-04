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
from selenium.common.exceptions import NoSuchElementException
import time
import json
import datetime
import re
import boto3
import os
from dotenv import load_dotenv
import pymysql
from pymysql import Error
import logging

# Load environment variables from .env file
load_dotenv()

##### logging  #####
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('etf_info_crawler.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.info('Start etf_info_crawler.py')

#####
s3 = boto3.client('s3',
                  aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                  aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                  region_name=os.getenv("S3_BUCKET_REGION"))
BUCKET_NAME = os.getenv("BUCKET_NAME")

# Access environment variables
db_host = os.getenv("DB_HOST", "localhost")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME", "dev")

#####


def send_slack_message(message):
    url = 'https://hooks.slack.com/services/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'
    headers = {'Content-Type': 'application/json'}
    data = {'text': message}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Check for successful response
    if response.status_code == 200:
        print("Message sent to Slack successfully!")
    else:
        print(f"""Failed to send message. Status code: {
              response.status_code}, response text: {response.text}""")


def etf_info_crawler():
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

    ### Start the web driver ###
    # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
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
    try:
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
        WebDriverWait(driver, 180).until(EC.presence_of_all_elements_located(
            (By.ID, "etf-overview-region")))

        # get all the tabs of different ETF regions
        region_tabs = driver.find_elements(
            By.CSS_SELECTOR, "#etf-overview-region .tab-wrapper > button")
        region_tabs_len = len(region_tabs)

        # mimic clicking on each tab to get the ETF list
        for idx in range(region_tabs_len):
            driver.switch_to.window(original_window)

            region_tabs = driver.find_elements(
                By.CSS_SELECTOR, "#etf-overview-region .tab-wrapper > button")
            logger.info(f"Clicking on tab {idx}")

            # Scroll the element into view
            driver.execute_script(
                "arguments[0].scrollIntoView(true);", region_tabs[idx])
            # Adjust the scroll position slightly: move it up by half the window's height approximately
            driver.execute_script(
                "window.scrollBy(0, -window.innerHeight / 2);")
            time.sleep(1)

            region_tabs[idx].click()
            # driver.execute_script(
            #     f"document.querySelectorAll('#etf-overview-region .tab-wrapper > button')[{idx}].click();")
            time.sleep(1)
            # wait for the ETF list of specific region to be visible
            WebDriverWait(driver, 180).until(EC.visibility_of_element_located(
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
                WebDriverWait(driver, 180).until(EC.number_of_windows_to_be(2))

                # Find the new window handle and switch to it
                new_window = None
                for handle in driver.window_handles:
                    if handle != original_window:
                        new_window = handle
                        break
                driver.switch_to.window(new_window)

                WebDriverWait(driver, 180).until(EC.presence_of_element_located(
                    (By.ID, "main-0-QuoteHeader-Proxy")))

                etf_name = driver.find_element(
                    By.CSS_SELECTOR, "#main-0-QuoteHeader-Proxy h1").text
                # symbol is the first span
                symbol = driver.find_element(
                    By.CSS_SELECTOR, "#main-0-QuoteHeader-Proxy span").text
                price_today = driver.find_elements(
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
                    "etf_name": etf_name,
                    "symbol": symbol,
                    "price_today": price_today,
                    "up_down": up_down,
                    "up_down_change": up_down_change,
                    "up_down_percentage": up_down_percentage,
                    "data_updated_date": data_updated_date,
                    "crawler_date": today
                }
                etf_data.append(each_etf)
                logger.info(f"ETF data for {symbol} has been added")

                ### get the performance, industry and stock composition data ###
                full_symbol = driver.current_url.split('/')[-1]
                performance_url = f"""https://tw.stock.yahoo.com/quote/{
                    full_symbol}/performance"""
                holding_url = f"""https://tw.stock.yahoo.com/quote/{
                    full_symbol}/holding"""

                # get the performance data
                driver.get(performance_url)
                # WebDriverWait(driver, 10).until(lambda d: "績效表現" in d.title)

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
                    "symbol": symbol, "data_updated_date": updated_date_performance, "crawler_date": today}
                for each in performance_map:
                    each_performance_data[each] = "NULL"

                if performance_data_elements:
                    for idx, each in enumerate(performance_data_elements):
                        if "trend-up" in each.get_attribute("class"):
                            each_performance_data[performance_map[idx]
                                                  ] = each.text
                        elif "trend-down" in each.get_attribute("class"):
                            each_performance_data[performance_map[idx]
                                                  ] = "-" + each.text
                        else:
                            each_performance_data[performance_map[idx]] = "NULL"

                    etf_performance.append(each_performance_data)
                    # logger.info(f"Performance data for {symbol} has been added")
                else:
                    etf_performance.append({
                        "symbol": symbol,
                        "data_updated_date": updated_date_performance,
                        "crawler_date": today,
                        "1_week": "NULL",
                        "1_month": "NULL",
                        "3_month": "NULL",
                        "6_month": "NULL",
                        "YTD": "NULL",
                        "1_year": "NULL",
                        "2_year": "NULL",
                        "3_year": "NULL",
                        "5_year": "NULL",
                        "10_year": "NULL"
                    })
                    logger.info(f"""Performance data for {
                                symbol} has been added""")

                ### get industry and stock composition data ###
                driver.get(holding_url)
                # WebDriverWait(driver, 10).until(lambda d: "持股分析" in d.title)

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
                                "data_updated_date": updated_date_industry,
                                "crawler_date": today
                            })
                            # logger.info(f"Industry data for {symbol} has been added")
                else:
                    etf_industry.append({
                        "symbol": symbol,
                        "industry": "NULL",
                        "ratio": "NULL",
                        "data_updated_date": updated_date_industry,
                        "crawler_date": today
                    })
                    # logger.info(f"Industry data for {symbol} has been added")

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
                            stock_name = match.group(2).strip()
                            ratio = match.group(3).strip()

                            etf_stock_composition.append({
                                "symbol": symbol,
                                "ranking": ranking,
                                "stock_name": stock_name,
                                "ratio": ratio,
                                "data_updated_date": updated_date_stock_composition,
                                "crawler_date": today
                            })
                            logger.info(f"""Stock composition data for {
                                        symbol} has been added""")
                else:
                    etf_stock_composition.append({
                        "symbol": symbol,
                        "ranking": "NULL",
                        "stock_name": "NULL",
                        "ratio": "NULL",
                        "data_updated_date": updated_date_stock_composition,
                        "crawler_date": today
                    })
                    logger.info(f"""Stock composition data for {
                                symbol} has been added""")

                driver.close()
    except Exception as e:
        print(f"Error: {str(e)}")
        logger.error(f"Error: {str(e)}")
    finally:
        driver.quit()

    local_directory = 'json_files'
    ensure_local_directory_exists(local_directory)

    files_and_data = [
        (f'etf_overview_{today_file}.json', etf_data, 'etf_overview_data'),
        (f'etf_performance_{today_file}.json',
         etf_performance, 'etf_performance_data'),
        (f'etf_industry_{today_file}.json', etf_industry, 'etf_industry_data'),
        (f'etf_stock_composition_{today_file}.json',
         etf_stock_composition, 'etf_stock_composition_data')
    ]

    for filename, data, s3_folder in files_and_data:
        local_filepath = os.path.join(local_directory, filename)
        save_data_to_json(data, local_filepath)
        upload_file_to_s3(local_filepath, BUCKET_NAME, s3_folder)

    # Insert data into the database
    insert_etf_overview_data(etf_data)
    insert_etf_performance_data(etf_performance)
    insert_industry_data(etf_industry)
    insert_top10_stock_composition_data(etf_stock_composition)


def save_data_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logger.info(f"Data has been written to {filename}")
    send_slack_message(f"Data has been written to {filename}")


def upload_file_to_s3(filepath, bucket_name, s3_directory):
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
        send_slack_message(f"Successfully uploaded {filepath}")
    except Exception as e:
        print(f"Failed to upload {filepath}. Error: {str(e)}")
        logger.error(f"Failed to upload {filepath}. Error: {str(e)}")
        send_slack_message(f"Failed to upload {filepath}. Error: {str(e)}")


def ensure_local_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Directory {directory} has been created")


def get_db_connection():
    load_dotenv()
    db_host = os.getenv("DB_HOST", "localhost")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME", "dev")
    try:
        connection = pymysql.connect(
            host=db_host,
            user=db_user,
            passwd=db_password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        logger.info("Connected to database.")
        return connection
    except pymysql.MySQLError as e:
        logger.error(f"Error connecting to database: {e}")
        return None

# ETF overview table


def insert_etf_overview_data(data):
    connection = get_db_connection()
    if connection is None:
        logger.error("Failed to connect to database.")
        return

    try:
        with connection.cursor() as cursor:
            # create a temporary table to store today's crawled data
            cursor.execute("""
                CREATE TEMPORARY TABLE temp_etf_overview_data LIKE etf_overview_data;
            """)

            # insert crawled data into the temporary table
            sql_insert_temp = """
            INSERT INTO temp_etf_overview_data (etf_name, symbol, price_today, up_down, up_down_change, up_down_percentage, data_updated_date, crawler_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """
            # bulk insert data into the temporary table
            values_to_insert = []
            for item in data:
                values_to_insert.append((item['etf_name'], item['symbol'], item['price_today'], item['up_down'],
                                         item['up_down_change'], item['up_down_percentage'], item['data_updated_date'], item['crawler_date']))

            cursor.executemany(sql_insert_temp, values_to_insert)

            # check if the temporary table is empty
            cursor.execute(
                "SELECT COUNT(*) as cnt FROM temp_etf_overview_data;")
            result = cursor.fetchone()
            if result['cnt'] == 0:
                logger.error("No data in temp_etf_overview_data table.")
                return

            # upsert data from temporary table to main table
            sql_upsert = """
            INSERT INTO etf_overview_data (etf_name, symbol, price_today, up_down, up_down_change, up_down_percentage, data_updated_date, crawler_date)
            SELECT etf_name, symbol, price_today, up_down, up_down_change, up_down_percentage, data_updated_date, crawler_date
            FROM temp_etf_overview_data
            ON DUPLICATE KEY UPDATE
                etf_name = VALUES(etf_name),
                price_today = VALUES(price_today),
                up_down = VALUES(up_down),
                up_down_change = VALUES(up_down_change),
                up_down_percentage = VALUES(up_down_percentage),
                data_updated_date = VALUES(data_updated_date),
                crawler_date = VALUES(crawler_date);
            """

            cursor.execute(sql_upsert)

            #  delete records from main table that are not in the temporary table
            sql_delete = """
            DELETE FROM etf_overview_data
            WHERE symbol NOT IN (
                SELECT symbol FROM temp_etf_overview_data
            );
            """
            cursor.execute(sql_delete)

            connection.commit()
            logger.info("ETF overview data updated and cleaned.")
    except Exception as e:
        logger.error(f"Error updating etf_overview_data table: {e}")
        connection.rollback()
    finally:
        if connection:
            connection.close()

# ETF performance table


def insert_etf_performance_data(data):
    connection = get_db_connection()
    if connection is None:
        logger.error("Failed to connect to database.")
        return

    try:
        with connection.cursor() as cursor:
            # create a temporary table to store today's crawled data
            cursor.execute("""
                CREATE TEMPORARY TABLE temp_etf_performance LIKE etf_performance;
            """)

            # insert crawled data into the temporary table
            sql_insert_temp = """
            INSERT INTO temp_etf_performance (symbol, data_updated_date, crawler_date, 1_week, 1_month, 3_month, 6_month, YTD, 1_year, 2_year, 3_year, 5_year, 10_year)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            # bulk insert data into the temporary table
            values_to_insert = []
            for item in data:
                values_to_insert.append((item['symbol'], item['data_updated_date'], item['crawler_date'], item['1_week'], item['1_month'],
                                        item['3_month'], item['6_month'], item['YTD'], item['1_year'], item['2_year'], item['3_year'], item['5_year'], item['10_year']))

            cursor.executemany(sql_insert_temp, values_to_insert)

            # check if the temporary table is empty
            cursor.execute(
                "SELECT COUNT(*) as cnt FROM temp_etf_performance;")
            result = cursor.fetchone()
            if result['cnt'] == 0:
                # logger.error("No data in temp_etf_performance table.")
                return

            # upsert data from temporary table to main table
            sql_upsert = """
            INSERT INTO etf_performance (symbol, data_updated_date, crawler_date, 1_week, 1_month, 3_month, 6_month, YTD, 1_year, 2_year, 3_year, 5_year, 10_year)
            SELECT symbol, data_updated_date, crawler_date, 1_week, 1_month, 3_month, 6_month, YTD, 1_year, 2_year, 3_year, 5_year, 10_year
            FROM temp_etf_performance
            ON DUPLICATE KEY UPDATE
                data_updated_date = VALUES(data_updated_date),
                crawler_date = VALUES(crawler_date),
                1_week = VALUES(1_week),
                1_month = VALUES(1_month),
                3_month = VALUES(3_month),
                6_month = VALUES(6_month),
                YTD = VALUES(YTD),
                1_year = VALUES(1_year),
                2_year = VALUES(2_year),
                3_year = VALUES(3_year),
                5_year = VALUES(5_year),
                10_year = VALUES(10_year);
            """

            cursor.execute(sql_upsert)

            #  delete records from main table that are not in the temporary table
            sql_delete = """
            DELETE FROM etf_performance
            WHERE symbol NOT IN (
                SELECT symbol FROM temp_etf_performance
            );
            """
            cursor.execute(sql_delete)

            connection.commit()
            logger.info("ETF performance data updated and cleaned.")
            send_slack_message("ETF performance data updated and cleaned.")
    except Exception as e:
        logger.error(f"Error updating etf_performance table: {e}")
        send_slack_message(f"Error updating etf_performance table: {e}")
        connection.rollback()
    finally:
        if connection:
            connection.close()

# ETF top industry table


def insert_industry_data(data):
    connection = get_db_connection()
    if connection is None:
        logger.error("Failed to connect to database.")
        return

    try:
        with connection.cursor() as cursor:
            # create a temporary table to store today's crawled data
            cursor.execute("""
                CREATE TEMPORARY TABLE temp_top_industry LIKE top_industry;
            """)

            # insert crawled data into the temporary table
            sql_insert_temp = """
            INSERT INTO temp_top_industry (symbol, industry, ratio, data_updated_date, crawler_date)
            VALUES (%s, %s, %s, %s, %s);
            """
            # bulk insert data into the temporary table
            values_to_insert = []
            for item in data:
                values_to_insert.append(
                    (item['symbol'], item['industry'], item['ratio'], item['data_updated_date'], item['crawler_date']))

            cursor.executemany(sql_insert_temp, values_to_insert)

            # check if the temporary table is empty
            cursor.execute(
                "SELECT COUNT(*) as cnt FROM temp_top_industry;")
            result = cursor.fetchone()
            if result['cnt'] == 0:
                # logger.error("No data in temp_top_industry table.")
                return

            # upsert data from temporary table to main table
            sql_upsert = """
            INSERT INTO top_industry (symbol, industry, ratio, data_updated_date, crawler_date)
            SELECT symbol, industry, ratio, data_updated_date, crawler_date
            FROM temp_top_industry
            ON DUPLICATE KEY UPDATE
                industry = VALUES(industry),
                ratio = VALUES(ratio),
                data_updated_date = VALUES(data_updated_date),
                crawler_date = VALUES(crawler_date);
            """

            cursor.execute(sql_upsert)

            #  delete records from main table that are not in the temporary table
            sql_delete = """
            DELETE FROM top_industry
            WHERE symbol NOT IN (
                SELECT symbol FROM temp_top_industry
            );
            """
            cursor.execute(sql_delete)

            connection.commit()
            logger.info("ETF top industry data updated and cleaned.")
            send_slack_message("ETF top industry data updated and cleaned.")
    except Exception as e:
        logger.error(f"Error updating top_industry table: {e}")
        send_slack_message(f"Error updating top_industry table: {e}")
        connection.rollback()
    finally:
        if connection:
            connection.close()

# ETF top10 stock composition table


def insert_top10_stock_composition_data(data):
    connection = get_db_connection()
    if connection is None:
        logger.error("Failed to connect to database.")
        return

    try:
        with connection.cursor() as cursor:
            # create a temporary table to store today's crawled data
            cursor.execute("""
                CREATE TEMPORARY TABLE temp_top10_stock LIKE top10_stock;
            """)

            # insert crawled data into the temporary table
            sql_insert_temp = """
            INSERT INTO temp_top10_stock (symbol, ranking, stock_name, ratio,  data_updated_date, crawler_date)
            VALUES (%s, %s, %s, %s, %s, %s);
            """
            # bulk insert data into the temporary table
            values_to_insert = []
            for item in data:
                values_to_insert.append((item['symbol'], item['ranking'], item['stock_name'], item['ratio'],
                                         item['data_updated_date'], item['crawler_date']))

            cursor.executemany(sql_insert_temp, values_to_insert)

            # check if the temporary table is empty
            cursor.execute(
                "SELECT COUNT(*) as cnt FROM temp_top10_stock;")
            result = cursor.fetchone()
            if result['cnt'] == 0:
                logger.error("No data in temp_top10_stock table.")
                return

            # upsert data from temporary table to main table
            sql_upsert = """
            INSERT INTO top10_stock (symbol, ranking, stock_name, ratio, data_updated_date, crawler_date)
            SELECT symbol, ranking, stock_name, ratio, data_updated_date, crawler_date
            FROM temp_top10_stock
            ON DUPLICATE KEY UPDATE
                ranking = VALUES(ranking),
                stock_name = VALUES(stock_name),
                ratio = VALUES(ratio),
                data_updated_date = VALUES(data_updated_date),
                crawler_date = VALUES(crawler_date);
            """

            cursor.execute(sql_upsert)

            #  delete records from main table that are not in the temporary table
            sql_delete = """
            DELETE FROM top10_stock
            WHERE symbol NOT IN (
                SELECT symbol FROM temp_top10_stock
            );
            """
            cursor.execute(sql_delete)

            connection.commit()
            logger.info("ETF top 10 stock data updated and cleaned.")
            send_slack_message("ETF top 10 stock data updated and cleaned.")
    except Exception as e:
        logger.error(f"Error updating top10_stock table: {e}")
        send_slack_message(f"Error updating top10_stock table: {e}")
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
    dag_id='ETF_info_crawler_dag_v4',
    schedule="30 7 * * *",  # Run the DAG daily at 07:30 UTC
    start_date=datetime.datetime(2024, 5, 1),
    default_args=default_args,
    catchup=False,
    tags=['crawler', 'etf', 'info', 'daily']
) as dag:
    task_start = EmptyOperator(
        task_id='task_start',
        dag=dag
    )
    task_end = EmptyOperator(
        task_id='task_end',
        dag=dag
    )

    task_run_etf_info_crawler = PythonOperator(
        task_id='etf_info_crawler',
        python_callable=etf_info_crawler,
        dag=dag
    )
    (
        task_start
        >> task_run_etf_info_crawler
        >> task_end
    )
