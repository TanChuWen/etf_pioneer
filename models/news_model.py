from utils import fetch_data


def get_news_data(connection, start_date, end_date):
    query = """
        SELECT news_title, news_date, website, news_link
        FROM news_data
        WHERE news_date >= %s AND news_date <= %s
        ORDER BY news_date DESC
    """
    return fetch_data(connection, query, (start_date, end_date))
