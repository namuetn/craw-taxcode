
import re
import json
import requests
from bs4 import BeautifulSoup


def create_json_file(file_save, data):
    with open(file_save, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def crawl_city_of_vn(filename):
    print('[INFO] Start crawl city list...')
    url = "https://tracuumst.com/"
    response = requests.get(url)

    cities = []
    if response.status_code == 200:
        total_city = 0
        soup = BeautifulSoup(response.text, 'lxml')
        cities_element = soup.find_all('a', attrs={
            'href': re.compile('https://tracuumst.com/tinh-thanh/')
        })

        for city in cities_element:
            total_city += 1
            cities.append(city['href'])

        create_json_file(filename, cities)
        print(f'[INFO] Total city: {total_city}')
        print(f'[INFO] Crawl city list successfully. Save at {filename}')


if __name__ == '__main__':
    city_filename = './dist/cities.json'
    result = crawl_city_of_vn(city_filename)