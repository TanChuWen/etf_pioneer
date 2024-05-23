
# ETF Pioneer

ETF Pioneer is a website featuring ETF rankings, data search, comparison, stock lookup, and news aggregation to enhance user investment decisions.
Website: [https://etf-pioneer.services/](https://etf-pioneer.services/)
Full Demo: [https://youtu.be/m-WIfyfHKTk?si=-9hdtTWSlbcSWTtb](https://youtu.be/m-WIfyfHKTk?si=-9hdtTWSlbcSWTtb)

## Table of Contents
* [Features](#features)
* [Architecture](#architecture)
* [Live Demo](#live-demo)
* [Tools Used](#technologies-and-tools-used)
* [Contact](#contact)


## Features

* **ETF 排名**  
  Visualize ETF rankings based on multiple performance indicators.  
  See the live demo: [ETF 排名](#users-can-visualize-etf-rankings-based-on-multiple-performance-indicators)

* **搜尋 ETF**  
  Search for ETFs by name or ticker.  
  See the live demo: [搜尋 ETF](#users-can-search-for-etfs-by-name-or-ticker)

* **比較 ETF**  
  Compare ETFs side-by-side.  
  See the live demo: [比較 ETF](#users-can-compare-etfs-side-by-side)

* **個股反查 ETF**  
  Identify ETFs containing specific stocks.  
  See the live demo: [個股反查 ETF](#users-can-identify-etfs-containing-specific-stocks)

* **ETF 新聞整合與關鍵字文字雲**  
  Stay updated with ETF-related news.  
  See the live demo: [ETF 新聞整合與關鍵字文字雲](#users-can-stay-updated-with-etf-related-news)
  
## Architecture

System Architecture Overview
![System Architecture Diagram](ReadmeMaterial/Architecture.png)




#### EC2 A: Data Crawling and Processing Server
EC2 A is configured as a data crawling pipeline using Apache Airflow for ETL (Extract, Transform, Load) techniques to process data scraped from various websites. Initially, all scraped data is stored in an Amazon S3 bucket during the transformation phase. After normalization, the data is finally saved into a MySQL database.

#### EC2 B: Frontend Server
EC2 B handles the frontend website layout, efficiently managing a high volume of client requests using the Flask framework. This server is interconnected with the same database used by Server A, enabling it to access database tables and retrieve the required data in response to client requests. NGINX is used as a reverse proxy to enhance server performance and security.

#### Monitoring
Amazon CloudWatch is used to monitor the data pipeline and server, logging errors and ensuring 100% completion of the data pipeline during scraping. It continuously checks the frontend website status. For daily crawling operations, it automatically sends Slack notifications if any issues arise.

#### Data Backup
Processed data, in addition to being stored in the MySQL database, is also backed up to Amazon S3 to ensure data security and persistence.

#### DevOps
GitHub Actions is utilized for Continuous Integration (CI) and Continuous Deployment (CD) to verify error-free code passing unit tests. Upon successful test completion, the next deployment job is triggered to deploy the code to an AWS EC2 server.

This architecture ensures a seamless and reliable flow from data crawling to frontend presentation, including data processing, backup, monitoring, and automated deployment, ensuring the entire system runs smoothly and efficiently.


## Live Demo

#### Users can visualize ETF rankings based on multiple performance indicators. ETF 排名：以成交金額、資產規模、受益人數、年初至今績效進行排名。
![Feature 1: ETF 排名](ReadmeMaterial/feature_1_ETF_ranking_updated.gif)

#### Users can search for ETFs by name or ticker. 搜尋 ETF：輸入 ETF 名稱或是代號搜尋最近交易日的交易價格、不同時間尺度下的績效數據、ETF 組成的產業佔比、 ETF 前十大成分股佔比。
![Feature 2: 搜尋 ETF](ReadmeMaterial/feature_2_search_an_ETF_updated.gif)

#### Users can compare ETFs side-by-side. 比較 ETF：同時比較兩檔 ETF 數據。
![Feature 3: 比較 ETF](ReadmeMaterial/feature_3_compare_ETFs.gif)


#### Users can identify ETFs containing specific stocks. 個股反查 ETF：輸入個股名稱或代號，反查哪些 ETF 中含有該檔個股。
![Feature 4: 從股票反查 ETF](ReadmeMaterial/feature_4_find_ETF_from_stock_updated.gif)
  
#### Users can stay updated with ETF-related news. ETF 新聞整合與關鍵字文字雲：選擇時間，查看特定區間下的 ETF 相關新聞並可點選查看新聞內文，並輔以新聞關鍵字文字雲，作為投資參考依據。
- [Feature 5: ETF 新聞整合與關鍵字文字雲](ReadmeMaterial/feature_5_ETF_news_aggregation_and_keyword_word_cloud.mov)
  


## Tools Used
* Programming Languages: Python, JavaScript
* Database: MySQL
* Container: Docker
* Frameworks: Flask
* Reverse Proxy: Nginx
* Data Visualization Tool: Plotly
* Cloud Engineering - AWS: EC2, S3, RDS
* Monitoring Tools - AWS: CloudWatch
* Notification: Slack
* CI/CD Tools: GitHub Actions
  
## Contact

Chuwen Tan 
* Email: chuwen.tan33@gmail.com 
* LinkedIn: https://www.linkedin.com/in/chuwentan/
