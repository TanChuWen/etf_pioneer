from dotenv import load_dotenv
import os
import pymysql
from flask import Flask, jsonify, render_template, request
from database import get_db_connection

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

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


# Route to get data from a generic table
ALLOWED_TABLES = ['etf_ranking_volume', 'etf_ranking_assets',
                  'etf_ranking_holders', 'etf_ranking_performance']


@app.route('/etf-pioneer/data/<string:table_name>', methods=['GET'])
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


if __name__ == '__main__':
    app.run(debug=True, port=5008)
