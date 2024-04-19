from dotenv import load_dotenv
import os
import pymysql
from flask import Flask, jsonify, render_template, request
from database import get_db_connection
import logging

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


if __name__ == '__main__':
    app.run(debug=True, port=5008)
