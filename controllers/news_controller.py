from flask import Blueprint, request, render_template
from utils import get_db_connection, logger, generate_wordcloud
from models.news_model import get_news_data
from datetime import datetime
import jieba

news_bp = Blueprint('news_bp', __name__)


@news_bp.route('/etf-pioneer/api/news-wordcloud', methods=['GET'])
def get_news_data_route():
    start_date = request.args.get(
        'start_date', datetime.today().strftime('%Y-%m-%d'))
    end_date = request.args.get(
        'end_date', datetime.today().strftime('%Y-%m-%d'))
    max_date = datetime.today().strftime('%Y-%m-%d')

    connection = get_db_connection()
    try:
        news_data = get_news_data(connection, start_date, end_date)

        if not news_data:
            logger.error("No data found")
            return render_template('error.html', error="No data found", start_date=start_date, end_date=end_date)

        text = ""
        for item in news_data:
            words = jieba.cut(item['news_title'])
            text += " ".join(words) + " "

        image_data = generate_wordcloud(text)
        logger.info(f"Wordcloud generated from {start_date} to {end_date}")
        return render_template('news_trend.html', image_data=image_data, start_date=start_date, end_date=end_date, newsList=news_data, max_date=max_date)
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        return render_template('error.html', error=e)
    finally:
        connection.close()
