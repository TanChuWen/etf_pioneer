from flask import Blueprint, request, jsonify, render_template
from utils import get_db_connection, logger
from models.etf_model import get_etf_overview, get_etf_performance, get_top_industry, get_top10_stock
from datetime import datetime
from utils import fetch_data, fetch_single_record

etf_bp = Blueprint('etf_bp', __name__)


# Routes


@etf_bp.route('/')
def home():
    max_date = datetime.today().strftime('%Y-%m-%d')
    return render_template('index.html', max_date=max_date)


@etf_bp.route('/etf-pioneer/api/ranking/<string:type>', methods=['GET'])
def get_ranking_data_by_type(type):
    ALLOWED_TYPES = ['volume', 'assets', 'holders', 'performance']
    if type not in ALLOWED_TYPES:
        logger.error(f"Type not allowed: {type}")
        return jsonify({"error": "Type not allowed"}), 403

    table_name = f'etf_ranking_{type}'
    return get_data(table_name)


@etf_bp.route('/etf-pioneer/api/ranking/<string:table_name>', methods=['GET'])
def get_data(table_name):
    ALLOWED_TABLES = ['etf_ranking_volume', 'etf_ranking_assets',
                      'etf_ranking_holders', 'etf_ranking_performance']
    if table_name not in ALLOWED_TABLES:
        logger.error(f"Table not allowed: {table_name}")
        return jsonify({"error": "Table not allowed"}), 403

    connection = get_db_connection()
    try:
        query = f"SELECT * FROM `{table_name}`"
        data = fetch_data(connection, query)
        if data is None:
            return jsonify({"error": "Table does not exist or no data found"}), 404

        logger.info(f"Data fetched from {table_name}")
        return jsonify(data)
    finally:
        connection.close()


@etf_bp.route('/search-results', methods=['GET'])
def search_results():
    symbol = request.args.get('symbol')
    symbol_compare = request.args.get('compareSymbol')
    if not symbol:
        return render_template('error.html', error="Symbol is required")

    connection = get_db_connection()
    try:
        etf_overview_data = {}
        etf_performance_data = {}
        top_industry_data = {}
        top10_stock_data = {}

        etf_overview_data["etf1"] = get_etf_overview(connection, symbol)
        etf_performance_data["etf1"] = get_etf_performance(connection, symbol)
        top_industry_data["etf1"] = get_top_industry(connection, symbol)
        top10_stock_data["etf1"] = get_top10_stock(connection, symbol)

        if symbol_compare:
            etf_overview_data["etf2"] = get_etf_overview(
                connection, symbol_compare)
            etf_performance_data["etf2"] = get_etf_performance(
                connection, symbol_compare)
            top_industry_data["etf2"] = get_top_industry(
                connection, symbol_compare)
            top10_stock_data["etf2"] = get_top10_stock(
                connection, symbol_compare)
        else:
            etf_overview_data["etf2"] = {}
            etf_performance_data["etf2"] = {}
            top_industry_data["etf2"] = {}
            top10_stock_data["etf2"] = {}

        max_date = datetime.today().strftime('%Y-%m-%d')

        return render_template('search_results.html', symbol=symbol, etfData=etf_overview_data, etfPerformanceData=etf_performance_data, etfIndustryData=top_industry_data, etfStockData=top10_stock_data, max_date=max_date)
    except Exception as e:
        logger.error(str(e))
        return render_template('error.html', error=str(e))
    finally:
        connection.close()


@etf_bp.route('/etf-pioneer/api/stock-to-etf', methods=['GET'])
def search_etf_by_stock():
    stock_code = request.args.get('stock_code')
    if not stock_code:
        logger.error("Stock code is required")
        return render_template('error.html', error="Stock code is required")

    connection = get_db_connection()
    try:
        query = """
            SELECT T.symbol, T.stock_name AS component_stock_name, T.ratio, T.data_updated_date, 
                   A.stock_code, A.listed_or_OTC, A.industry_category, ETF.etf_name AS etf_name
            FROM top10_stock AS T
            INNER JOIN (
                SELECT stock_name, MAX(crawler_date) AS max_crawler_date
                FROM top10_stock
                GROUP BY stock_name
            ) AS TM ON T.stock_name = TM.stock_name AND T.crawler_date = TM.max_crawler_date
            LEFT JOIN all_stock_list AS A ON T.stock_name = A.stock_name
            LEFT JOIN etf_overview_data AS ETF ON T.symbol = ETF.symbol
            WHERE A.stock_code = %s
        """
        results = fetch_data(connection, query, (stock_code,))
        max_date = datetime.today().strftime('%Y-%m-%d')
        if not results:
            error_message = "本檔股票不屬於任何一檔 ETF 的前十大成分股，請重新查詢"
            return render_template('error-top10.html', error=error_message, max_date=max_date)

        return render_template('lookup_from_stock.html', stock_data=results, max_date=max_date)
    finally:
        connection.close()
