import logging
import pymysql
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
from wordcloud import WordCloud, STOPWORDS
import jieba
import base64
from datetime import datetime
from io import BytesIO

# Logging configuration


def setup_logging():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    handler = logging.FileHandler('app.log')
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info('Start app.py')
    return logger


logger = setup_logging()


def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

# Utility functions


def fetch_data(connection, query, params=None):
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()
    except Exception as e:
        logger.error(str(e))
        return None


def fetch_single_record(connection, query, params=None):
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()
    except Exception as e:
        logger.error(str(e))
        return None


def generate_wordcloud(text):
    stopwords = set(STOPWORDS)
    stopwords.update(["可以", "快訊", "新聞", "報導", "影音",
                     "影片", "直播", "獨家", "專訪", "專家"])
    wordcloud = WordCloud(
        font_path="Noto_Sans_TC/NotoSansTC-VariableFont_wght.ttf",
        width=600,
        height=400,
        stopwords=stopwords,
        max_words=20,
        background_color='white'
    ).generate(text)
    img = BytesIO()
    wordcloud.to_image().save(img, format='PNG')
    img.seek(0)
    img_data = base64.b64encode(img.getvalue()).decode()
    return f"data:image/png;base64,{img_data}"
