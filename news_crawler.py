import ipdb
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from wordcloud import WordCloud, STOPWORDS

# 使用webdriver-manager自動下載chrome driver
s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s)

# define a function to get news titles


def fetch_news_titles(driver, url, element_type, element_identifier):
    try:
        driver.get(url)
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((element_type, element_identifier)))
        news_titles = driver.find_elements(element_type, element_identifier)

        for title in news_titles:
            print(title.text)
    except Exception as e:
        print(e)


try:
    # Yahoo Finance
    fetch_news_titles(driver, "https://tw.stock.yahoo.com/funds-news/",
                      By.TAG_NAME, "h3")
    # cnyes
    fetch_news_titles(driver, "https://m.cnyes.com/news/cat/etf",
                      By.CLASS_NAME, "tlhuwq2")
    # 工商時報
    fetch_news_titles(driver, "https://www.ctee.com.tw/wealth/etf",
                      By.CLASS_NAME, "news-title")
    # 經濟日報
    fetch_news_titles(driver, "https://money.udn.com/search/tagging/1001/ETF",
                      By.CLASS_NAME, "story__headline")
    # yahoo 財經特派
    fetch_news_titles(
        driver, "https://tw.stock.yahoo.com/reporter/", By.TAG_NAME, "h3")


finally:
    driver.quit()


# # 使用jieba將新聞「標題」斷詞
# etf_title = [yahoo_title, ]


# # 使用wordcloud製作文字雲，STOPWORDS可以排除常見的無意義詞彙
# stopwords = set(STOPWORDS)
# stopwords.add("可以")
# stopwords.add("快訊")
# stopwords.add("新聞")
# stopwords.add("報導")
# stopwords.add("影音")
# stopwords.add("影片")
# stopwords.add("直播")
# stopwords.add("獨家")
# stopwords.add("專訪")
# stopwords.add("專家")

# cloud = WordCloud(width=1000, stopwords=stopwords, height=500,
#                   max_words=20, background_color='white').generate(cut_text)
# plt.imshow(cloud)
# plt.axis
# plt.show()
# cloud.to_file('wordcloud.png')
