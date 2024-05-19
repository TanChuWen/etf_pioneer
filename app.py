import pymysql
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

from controllers import etf_controller, news_controller

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Register blueprints
app.register_blueprint(etf_controller.etf_bp)
app.register_blueprint(news_controller.news_bp)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html'), 404


@app.route('/test-error')
def test_error():
    return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=True, port=5008)
