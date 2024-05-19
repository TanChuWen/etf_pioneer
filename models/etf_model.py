from utils import fetch_data, fetch_single_record
from flask import jsonify


def get_etf_overview(connection, symbol):
    query = """
        SELECT etf_name, symbol, price_today, up_down_change, up_down_percentage, data_updated_date
        FROM etf_overview_data
        WHERE symbol = %s
    """
    result = fetch_single_record(connection, query, (symbol,))
    if not result:
        return jsonify({"error": "No data found"}), 404
    return result


def get_etf_performance(connection, symbol):
    query = """
        SELECT symbol, 1_week, 1_month, 3_month, 6_month, YTD, 1_year, 2_year, 3_year, 5_year, 10_year, data_updated_date
        FROM etf_performance
        WHERE symbol = %s
    """
    result = fetch_single_record(connection, query, (symbol,))
    if not result:
        return jsonify({"error": "No data found"}), 404
    return result


def get_top_industry(connection, symbol):
    query = """
        SELECT symbol, industry, ratio, data_updated_date
        FROM top_industry
        WHERE symbol = %s AND crawler_date = (
            SELECT MAX(crawler_date) FROM top_industry WHERE symbol = %s
        )
    """
    results = fetch_data(connection, query, (symbol, symbol))
    if not results:
        return jsonify({"error": "No data found"}), 404

    total_ratio_query = """
        SELECT SUM(ratio) as total_ratio
        FROM top_industry
        WHERE symbol = %s AND crawler_date = (
            SELECT MAX(crawler_date) FROM top_industry WHERE symbol = %s
        )
    """
    total_ratio = fetch_single_record(
        connection, total_ratio_query, (symbol, symbol))
    if total_ratio:
        other_ratio = max(100 - total_ratio['total_ratio'], 0)
    else:
        other_ratio = 0

    formatted_other_ratio = f"{other_ratio:.2f}%"
    results.append({'symbol': symbol, 'industry': '其他', 'ratio': formatted_other_ratio,
                   'data_updated_date': results[0]['data_updated_date']})
    return results


def get_top10_stock(connection, symbol):
    query = """
        SELECT symbol, ranking, stock_name, ratio, data_updated_date
        FROM top10_stock
        WHERE symbol = %s AND crawler_date = (
            SELECT MAX(crawler_date) FROM top10_stock WHERE symbol = %s
        )
    """
    top10_results = fetch_data(connection, query, (symbol, symbol))
    if not top10_results:
        return jsonify({"error": "No data found"}), 404

    total_ratio_query = """
        SELECT SUM(ratio) as total_ratio
        FROM top10_stock
        WHERE symbol = %s AND crawler_date = (
            SELECT MAX(crawler_date) FROM top10_stock WHERE symbol = %s
        )
    """
    total_ratio = fetch_single_record(
        connection, total_ratio_query, (symbol, symbol))
    if total_ratio:
        other_ratio = max(100 - total_ratio['total_ratio'], 0)
    else:
        other_ratio = 0

    formatted_other_ratio = f"{other_ratio:.2f}%"
    top10_results.append({'symbol': symbol, 'ranking': '其他', 'stock_name': '其他',
                         'ratio': formatted_other_ratio, 'data_updated_date': top10_results[0]['data_updated_date']})
    return top10_results
