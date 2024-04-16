import requests
from bs4 import BeautifulSoup
import json
import os
import boto3
from dotenv import load_dotenv
import datetime
import time
import re
import pymysql
from database import get_db_connection, truncate_table_all_stock_list, insert_new_records_all_stock_list


# Load environment variables from .env file
load_dotenv()

#####
s3 = boto3.client('s3',
                  aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                  aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                  region_name=os.getenv("S3_BUCKET_REGION"))
BUCKET_NAME = os.getenv("BUCKET_NAME")
#####
stock_list = []
today = datetime.datetime.now().strftime("%Y/%m/%d")
today_file = datetime.datetime.now().strftime("%Y-%m-%d")


def save_data_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data has been written to {filename}")


def upload_file_to_s3(filepath, bucket_name, s3_directory):
    """Uploads a file to an S3 bucket."""
    s3_client = boto3.client('s3')
    s3_key = os.path.join(s3_directory, os.path.basename(filepath))
    print(f"Trying to upload {filepath} to {bucket_name} at {s3_key}")
    try:
        s3_client.upload_file(filepath, bucket_name, s3_key)
        print(f"Successfully uploaded")
    except Exception as e:
        print(f"Failed to upload {filepath}. Error: {str(e)}")


def ensure_local_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


##### Fetch stock list from TWSE website #####
url = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2"
response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'h4'})
    rows = table.find_all('tr')[1:]  # skip the header row
    # Get the data updated time
    center_tags = soup.find_all('center')
    date_str = None
    for tag in center_tags:
        if re.search(r'\d{4}/\d{2}/\d{2}', tag.text):
            date_str = re.search(r'\d{4}/\d{2}/\d{2}', tag.text).group()
            break

    if date_str:
        data_update_date = date_str
    else:
        data_update_date = "NULL"

    for row in rows:
        cells = row.find_all('td')
        if len(cells) > 4:
            code_and_name = cells[0].text.strip().split()
            # code and name are separated by a space
            if len(code_and_name) >= 2:
                stock_code = code_and_name[0]
                stock_name = " ".join(code_and_name[1:])
                listed_or_OTC = cells[3].text.strip()
                industry_category = cells[4].text.strip()

                stock_list.append({
                    "stock_code": stock_code,
                    "stock_name": stock_name,
                    "listed_or_OTC": listed_or_OTC,
                    "industry_category": industry_category,
                    "data_update_date": data_update_date,
                    "crawler_date": today
                })
else:
    print("Failed to fetch data from TWSE website.")


# Save the data to a JSON file and upload to S3
local_directory = 'json_files'
s3_directory = 'stock_list'

ensure_local_directory_exists(local_directory)
filename = f'stock_list_{today_file}.json'
local_filepath = os.path.join(local_directory, filename)

save_data_to_json(stock_list, local_filepath)
upload_file_to_s3(local_filepath, BUCKET_NAME, s3_directory)

# Insert the data into the database
connection = get_db_connection()
if connection:
    truncate_table_all_stock_list(connection)
    insert_data = [(stock['stock_code'], stock['stock_name'], stock['listed_or_OTC'],
                    stock['industry_category'], stock['data_update_date'], stock['crawler_date']) for stock in stock_list]
    insert_new_records_all_stock_list(connection, insert_data)
    connection.close()
