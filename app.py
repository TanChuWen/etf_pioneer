import logging
from database import get_db_connection
from flask import Flask, jsonify, render_template, request
import pymysql
import os
from dotenv import load_dotenv


app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

##### logging #####
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

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
            return jsonify(data)
    except Exception as e:
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
        logging.error(str(e))
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
        logging.error(str(e))
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
                WHERE symbol = %s
                """, (symbol,))
            results = cursor.fetchall()
            if not results:
                return jsonify({"error": "No data found"}), 404
            return jsonify(results)
    except Exception as e:
        logging.error(str(e))
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
                WHERE symbol = %s
                """, (symbol,))
            results = cursor.fetchall()
            if not results:
                return jsonify({"error": "No data found"}), 404
            return jsonify(results)
    except Exception as e:
        logging.error(str(e))
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
            # join top10_stock and all_stock_list tables to get the stock_code
            cursor.execute("""
                SELECT T.symbol, T.stock_name, T.ratio, T.data_updated_date, A.stock_code, A.listed_or_OTC, A.industry_category
                FROM top10_stock AS T 
                LEFT JOIN all_stock_list AS A ON T.stock_name = A.stock_name
                WHERE A.stock_code = %s
                """, (stock_code,))
            results = cursor.fetchall()
            if not results:
                return jsonify({"error": "No data found"}), 404
            return jsonify(results)
    except Exception as e:
        logging.error(str(e))
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            connection.close()


if __name__ == '__main__':
    app.run(debug=True, port=5008)
