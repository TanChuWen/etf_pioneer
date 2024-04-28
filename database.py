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
                logger.error("No data in temp_etf_performance table.")
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
    except Exception as e:
        logger.error(f"Error updating etf_performance table: {e}")
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
                logger.error("No data in temp_top_industry table.")
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
    except Exception as e:
        logger.error(f"Error updating top_industry table: {e}")
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
    except Exception as e:
        logger.error(f"Error updating top10_stock table: {e}")
        connection.rollback()
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

# Insert data into ETF ranking tables


def insert_data_etf_ranking(data, table_name):
    connection = get_db_connection()
    if connection is None:
        logger.error("Failed to connect to the database.")
        return

    field_mapping = field_mappings.get(table_name, {})
    if not field_mapping:
        logger.error(f"Failed to find field mapping for table {table_name}")
        return

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

        connection.commit()
        logger.info(f"Data successfully upserted into {table_name}.")
    except Exception as e:
        logger.error(f"""Error occurred while inserting data into {
                     table_name}: {e}""")
        connection.rollback()
    finally:
        if connection:
            connection.close()

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
            INSERT INTO news_data (news_title, news_date, website, crawler_date, news_link)
            VALUES (%s, STR_TO_DATE(%s, '%%Y/%%m/%%d'), %s, STR_TO_DATE(%s, '%%Y/%%m/%%d'), %s)
            """
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
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        # Rollback the transaction in case of any other error
        connection.rollback()
