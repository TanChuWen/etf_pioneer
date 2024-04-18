import os
import pymysql
from pymysql import Error
from dotenv import load_dotenv
import time
import datetime
import logging

load_dotenv()

##### Logging #####
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('database.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.info('Start database.py')

today = datetime.datetime.now().strftime("%Y/%m/%d")

# Access environment variables
db_host = os.getenv("DB_HOST", "localhost")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME", "dev")


# Function to get a database connection
def get_db_connection():
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

# Stock list table


def clear_table_all_stock_list(connection):
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM all_stock_list;")
            connection.commit()
            logger.info("Table all_stock_list cleared.")
    except Error as e:
        logger.error("Failed to clear table all_stock_list", e)


def insert_new_records_all_stock_list(connection, data):
    try:
        with connection.cursor() as cursor:
            insert_query = """
            INSERT INTO all_stock_list (stock_code, stock_name, listed_or_OTC, industry_category, data_update_date, crawler_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(insert_query, data)
            connection.commit()
            logger.info("Inserted new records into all_stock_list.")
    except Error as e:
        logger.error("Failed to insert new records into all_stock_list", e)


# News data table


def insert_news_data(connection, news_item):
    try:
        with connection.cursor() as cursor:
            # Prepare the INSERT statement without the existence check.
            insert_query = """
            INSERT INTO news_data (news_title, news_date, website, crawler_date)
            VALUES (%s, STR_TO_DATE(%s, '%%Y/%%m/%%d'), %s, STR_TO_DATE(%s, '%%Y/%%m/%%d'))
            """
            try:
                # Attempt to insert the new record.
                cursor.execute(
                    insert_query,
                    (
                        news_item['news_title'],
                        news_item['news_date'],
                        news_item['website'],
                        news_item['crawler_date']
                    )
                )
                connection.commit()
                logger.info(f"Inserted: {news_item['news_title']}")
            except pymysql.err.IntegrityError as e:
                # This block will be executed if a duplicate entry is attempted.
                logger.info(f"""Skipped duplicate: {
                    news_item['news_title']}, Error: {e}""")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        # Rollback the transaction in case of any other error
        connection.rollback()


# ETF profile table


def insert_etf_overview_data(data):
    connection = get_db_connection()
    if connection is None:
        logger.error("Failed to connect to database.")
        return

    try:
        with connection.cursor() as cursor:
            # 創建臨時表
            cursor.execute("""
                CREATE TEMPORARY TABLE temp_etf_overview_data LIKE etf_overview_data;
            """)

            # 插入數據到臨時表
            for item in data:
                sql = """
                INSERT INTO temp_etf_overview_data (etf_name, symbol, price_today, up_down, up_down_change, up_down_percentage, data_updated_date, crawler_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """
                logger.info(item)
                cursor.execute(sql, (item['etf_name'], item['symbol'], item['price_today'], item['up_down'],
                               item['up_down_change'], item['up_down_percentage'], item['data_updated_date'], item['crawler_date']))

            # 更新主表數據
            cursor.execute("DELETE FROM etf_overview_data;")
            cursor.execute(
                "INSERT INTO etf_overview_data SELECT * FROM temp_etf_overview_data;")

            # 提交更改
            connection.commit()
    except Exception as e:
        logger.error(f"Error inserting data into etf_overview_data table: {e}")
    finally:
        if connection:
            connection.close()


def insert_etf_performance_data(data):
    connection = get_db_connection()
    if connection is None:
        logger.error("Failed to connect to database.")
        return

    try:
        with connection.cursor() as cursor:
            # create a temporary table
            cursor.execute("""
                CREATE TEMPORARY TABLE temp_etf_performance LIKE etf_performance;
            """)

            # insert data into the temporary table
            for item in data:
                sql = """
                INSERT INTO temp_etf_performance (symbol, data_updated_date, crawler_date, 1_week, 1_month, 3_month, 6_month, YTD, 1_year, 2_year, 3_year, 5_year, 10_year)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                cursor.execute(sql, (item['symbol'], item['data_updated_date'], item['crawler_date'], item['1_week'],
                               item['1_month'], item['3_month'], item['6_month'], item['YTD'], item['1_year'], item['2_year'], item['3_year'], item['5_year'], item['10_year']))

            # update the main table data
            cursor.execute("DELETE FROM etf_performance;")
            cursor.execute(
                "INSERT INTO etf_performance SELECT * FROM temp_etf_performance;")

            connection.commit()
    except Exception as e:
        logger.error(f"Error inserting data into etf_performance table: {e}")
    finally:
        if connection:
            connection.close()


def insert_industry_data(data):
    connection = get_db_connection()
    if connection is None:
        logger.error("Failed to connect to database.")
        return

    try:
        with connection.cursor() as cursor:
            # create a temporary table
            cursor.execute("""
                CREATE TEMPORARY TABLE temp_top_industry LIKE top_industry;
            """)

            # insert data into the temporary table
            for item in data:
                sql = """
                INSERT INTO temp_top_industry (symbol, industry, ratio, data_updated_date, crawler_date)
                VALUES (%s, %s, %s, %s, %s);
                """
                cursor.execute(sql, (item['symbol'], item['industry'], item['ratio'],
                               item['data_updated_date'], item['crawler_date']))

            # update the main table data
            cursor.execute("DELETE FROM top_industry;")
            cursor.execute(
                "INSERT INTO top_industry SELECT * FROM temp_top_industry;")

            connection.commit()
    except Exception as e:
        logger.error(f"Error inserting data into top_industry table: {e}")
    finally:
        if connection:
            connection.close()


def insert_top10_stock_composition_data(data):
    connection = get_db_connection()
    if connection is None:
        logger.error("Failed to connect to database.")
        return

    try:
        with connection.cursor() as cursor:
            # create a temporary table
            cursor.execute("""
                CREATE TEMPORARY TABLE temp_top10_stock LIKE top10_stock;
            """)

            # insert data into the temporary table
            for item in data:
                sql = """
                INSERT INTO temp_top10_stock (symbol, ranking, stock_name, ratio,  data_updated_date, crawler_date)
                VALUES (%s, %s, %s, %s, %s, %s);
                """
                cursor.execute(sql, (item['symbol'], item['ranking'], item['stock_name'],
                               item['ratio'], item['data_updated_date'], item['crawler_date']))

            # update the main table data
            cursor.execute("DELETE FROM top10_stock;")
            cursor.execute(
                "INSERT INTO top10_stock SELECT * FROM temp_top10_stock;")

            connection.commit()
    except Exception as e:
        logger.error(f"Error inserting data into top10_stock table: {e}")
    finally:
        if connection:
            connection.close()


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
