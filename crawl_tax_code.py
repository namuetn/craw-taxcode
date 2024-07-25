import os
import sys
import json
import time
import requests
import argparse
from bs4 import BeautifulSoup
import multiprocessing
from pymongo import MongoClient


def connect_mongo():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['taxcode_db']
    collection = db['taxcodes']
    return collection


def get_data_input():
    parser = argparse.ArgumentParser(description='Crawl tax code with URL')
    parser.add_argument('url', type=str, help='URL parameter')
    args = parser.parse_args()

    return args.url


def get_last_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            page_list = soup.find_all('li', class_='page-item')
            last_page = page_list[-2]
            return last_page.a.text
        except Exception as e:
            print(f'[ERROR] An error occurred. Detail: {e}')
            sys.exit()
    else:
        print(f'[ERROR] Request fail. Status code: {response.status_code}. Detail: {response.reason}')
        sys.exit()


def crawl_tax_code(url):
    response = requests.get(url)

    taxcodes = []
    if response.status_code == 200:
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            taxcodes_element = soup.find_all('i', class_='fa fa-hashtag')

            for taxcode_element in taxcodes_element:
                taxcode = taxcode_element.next_sibling.next_sibling.text
                taxcodes.append(taxcode)
        except Exception as e:
            print(f'[ERROR] An error occurred. Detail: {e}')
            sys.exit()
    else:
        print(f'[ERROR] Request fail. Status code: {response.status_code}. Detail: {response.reason}')
        sys.exit()

    return taxcodes


def process_page(page):
    url_page = url + f'?page={page}'
    taxcodes = crawl_tax_code(url_page)
    print(f'[INFO] Crawled Page {page}: {taxcodes} tax codes')
    return taxcodes


if __name__ == '__main__':
    start_time = time.time()

    url = get_data_input()
    print(f'[INFO] Start crawling tax code list: {time}')
    last_page = int(get_last_page(url))
    batch_size = 1000

    all_taxcodes = []
    collection = connect_mongo()

    with multiprocessing.Pool() as pool:
        # results = pool.map(process_page, range(1, 1001))
        # final_total = sum(results)
        for i in range(1, last_page + 1, batch_size):
            end_page = min(i + batch_size - 1, last_page)
            results = pool.map(process_page, range(i, end_page + 1))
            for result in results:
                all_taxcodes.extend(result)
            if all_taxcodes:
                collection.insert_many([{'taxcode': taxcode} for taxcode in all_taxcodes])
                print(f'[INFO] Inserted {len(all_taxcodes)} tax codes to MongoDB')
                all_taxcodes.clear()

    end_time = time.time()
    execution_time = end_time - start_time
    print(f'[INFO] Execute time: {execution_time}')
    print(f'[INFO] Crawl tax code list successfully and saved to MongoDB.')
