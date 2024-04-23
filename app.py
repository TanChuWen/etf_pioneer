import logging
from database import get_db_connection
from flask import Flask, jsonify, render_template, request
import pymysql
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import boto3
from wordcloud import WordCloud, STOPWORDS
import jieba
from io import BytesIO
import base64


app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

##### logging #####
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('app.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.info('Start app.py')

#####
s3 = boto3.client('s3',
                  aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                  aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                  region_name=os.getenv("S3_BUCKET_REGION"))
BUCKET_NAME = os.getenv("BUCKET_NAME")
#####


def upload_file_to_s3(filepath, bucket_name, s3_directory):
    """Uploads a file to an S3 bucket."""
    s3_client = boto3.client('s3')
    s3_key = os.path.join(s3_directory, os.path.basename(filepath))
    logger.info(f"Trying to upload {filepath} to {bucket_name} at {s3_key}")
    try:
        s3_client.upload_file(filepath, bucket_name, s3_key,
                              ExtraArgs={'ACL': 'public-read'})
        logger.info(f"Successfully uploaded")
    except Exception as e:
        logger.error(f"Failed to upload {filepath}. Error: {str(e)}")


def ensure_local_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


# Database config
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

# Connect to MySQL Database


def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

# Route to see HTML dashboard


@app.route('/')
def dashboard():
    return render_template('index.html')


# Route to get data from ETF ranking tables
ALLOWED_TABLES = ['etf_ranking_volume', 'etf_ranking_assets',
                  'etf_ranking_holders', 'etf_ranking_performance']


@app.route('/etf-pioneer/api/ranking/<string:table_name>', methods=['GET'])
def get_data(table_name):
    if table_name not in ALLOWED_TABLES:
        logger.error(f"Table not allowed: {table_name}")
        return jsonify({"error": "Table not allowed"}), 403

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Escape table_name to prevent SQL injection
            cursor.execute('SHOW TABLES LIKE %s', (table_name,))
            result = cursor.fetchone()
            if not result:
                return jsonify({"error": "Table does not exist"}), 404

            # Use backticks for identifiers
            cursor.execute(f"SELECT * FROM `{table_name}`")
            data = cursor.fetchall()  # Fetch all results as a list of dictionaries
            logger.info(f"Data fetched from {table_name}")
            return jsonify(data)
    except Exception as e:
        logger.error(str(e))
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            connection.close()


# Route to get ranking data by type
@app.route('/etf-pioneer/api/ranking/volume', methods=['GET'])
def get_volume_data():
    return get_data('etf_ranking_volume')


@app.route('/etf-pioneer/api/ranking/assets', methods=['GET'])
def get_assets_data():
    return get_data('etf_ranking_assets')


@app.route('/etf-pioneer/api/ranking/holders', methods=['GET'])
def get_holders_data():
    return get_data('etf_ranking_holders')


@app.route('/etf-pioneer/api/ranking/performance', methods=['GET'])
def get_performance_data():
    return get_data('etf_ranking_performance')

# generate and upload wordcloud


def generate_and_upload_wordcloud(text):
    stopwords = set(STOPWORDS)
    stopwords.update(["可以", "快訊", "新聞", "報導", "影音",
                     "影片", "直播", "獨家", "專訪", "專家"])
    wordcloud = WordCloud(
        font_path="Noto_Sans_TC/NotoSansTC-VariableFont_wght.ttf",
        width=1000,
        height=500,
        stopwords=stopwords,
        max_words=50,
        background_color='black'
    ).generate(text)
    img = BytesIO()
    wordcloud.to_image().save(img, format='PNG')
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()
# Route to get news data and generate wordcloud


@app.route('/etf-pioneer/api/news-wordcloud', methods=['GET'])
def get_news_data():
    start_date = request.args.get(
        'start_date', (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d'))
    end_date = request.args.get(
        'end_date', datetime.today().strftime('%Y-%m-%d'))
    connection = get_db_connection()

    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                "SELECT news_title FROM news_data WHERE news_date >= %s AND news_date <= %s", (start_date, end_date))
            results = cursor.fetchall()

            if not results:
                logger.error("No data found")
                return jsonify({"error": "No data found"}), 404

            text = " "
            for news_item in results:
                words = jieba.cut(news_item['news_title'])
                text += " ".join(words) + " "  # Add a space between each word

            # Generate wordcloud
            img_data = generate_and_upload_wordcloud(text)
            return jsonify({'image_data': f"data:image/png;base64,{img_data}"})
    except Exception as e:
        logger.error(str(e))
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            connection.close()

# Route to search for an ETF


@app.route('/etf-pioneer/api/overview', methods=['POST'])
def search_etf_overview():
    data = request.get_json()
    symbol = data.get('symbol', '請輸入正確的ETF代號')
    if not symbol:
        return jsonify({"error": "Symbol is required"}), 400
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT etf_name, symbol, price_today, up_down_change, up_down_percentage, data_updated_date
                    FROM etf_overview_data 
                    WHERE symbol = %s
                """, (symbol,))
            result = cursor.fetchone()

            return jsonify(result)
    except Exception as e:
        logger.error(str(e))
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            connection.close()

# Route to get performance data for ETFs


@app.route('/etf-pioneer/api/performance', methods=['POST'])
def get_etf_performance():
    data = request.get_json()
    symbol = data.get('symbol', '請輸入正確的ETF代號')
    if not symbol:
        return jsonify({"error": "Symbol is required"}), 400
    connection = get_db_connection()

    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT symbol, 1_week, 1_month, 3_month, 6_month, YTD, 1_year, 2_year, 3_year, 5_year, 10_year, data_updated_date
                FROM etf_performance
                WHERE symbol = %s
                """, (symbol,))
            result = cursor.fetchone()
            if not result:
                return jsonify({"error": "No data found"}), 404
            return jsonify(result)
    except Exception as e:
        logger.error(str(e))
    finally:
        connection.close()


# Route to get top industry data for ETFs
@app.route('/etf-pioneer/api/top-industry', methods=['POST'])
def get_top_industry():
    data = request.get_json()
    symbol = data.get('symbol', '請輸入正確的ETF代號')
    if not symbol:
        return jsonify({"error": "Symbol is required"}), 400
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT symbol, industry, ratio, data_updated_date 
                FROM top_industry
                WHERE symbol = %s AND crawler_date = (
                            SELECT MAX(crawler_date) FROM top_industry WHERE symbol = %s
                            )
                """, (symbol, symbol))
            results = cursor.fetchall()
            if not results:
                return jsonify({"error": "No data found"}), 404
            return jsonify(results)
    except Exception as e:
        logger.error(str(e))
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            connection.close()


# Route to get top10 stock data for ETFs
@app.route('/etf-pioneer/api/top10-stock', methods=['POST'])
def get_top10_stock():
    data = request.get_json()
    symbol = data.get('symbol', '請輸入正確的ETF代號')
    if not symbol:
        return jsonify({"error": "Symbol is required"}), 400
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT symbol, ranking, stock_name, ratio, data_updated_date 
                FROM top10_stock 
                WHERE symbol = %s AND crawler_date = (
                           SELECT MAX(crawler_date) FROM top10_stock WHERE symbol = %s
                           )
                """, (symbol, symbol))
            results = cursor.fetchall()
            if not results:
                return jsonify({"error": "No data found"}), 404
            return jsonify(results)
    except Exception as e:
        logger.error(str(e))
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            connection.close()

# Route to use stock symbol to search ETF


@app.route('/etf-pioneer/api/stock', methods=['POST'])
def search_etf_by_stock():
    data = request.get_json()
    stock_code = data.get('stockSymbol', '請輸入正確的股票代號')
    if not stock_code:
        return jsonify({"error": "Stock name is required"}), 400
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # max_crawler_date is the latest date of the stock data
            # join top10_stock and all_stock_list tables to get the stock_code
            cursor.execute("""
                SELECT T.symbol, T.stock_name, T.ratio, T.data_updated_date, A.stock_code, A.listed_or_OTC, A.industry_category
                FROM top10_stock AS T
                INNER JOIN (
                    SELECT stock_name, MAX(crawler_date) AS max_crawler_date
                    FROM top10_stock
                    GROUP BY stock_name
                ) AS TM ON T.stock_name = TM.stock_name AND T.crawler_date = TM.max_crawler_date
                LEFT JOIN all_stock_list AS A ON T.stock_name = A.stock_name
                WHERE A.stock_code = %s
                """, (stock_code,))
            results = cursor.fetchall()
            if not results:
                return jsonify({"error": "No data found"}), 404
            return jsonify(results)
    except Exception as e:
        logger.error(str(e))
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            connection.close()


if __name__ == '__main__':
    app.run(debug=True, port=5008)
