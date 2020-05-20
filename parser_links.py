import requests
from bs4 import BeautifulSoup
import csv
import os
import time
start_time = time.time()

CAR_BRANDS = ['MERCEDES', 'INFINITI', 'NISSAN', 'BMW', 'VOLKSWAGEN',
       'MITSUBISHI', 'TOYOTA', 'VOLVO', 'SKODA', 'LEXUS', 'AUDI', 'HONDA',
       'SUZUKI']
URL = 'https://auto.ru/moskva/cars/'
USED = '/used/'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0', 'accept': '*/*'}
FILE = 'cars_parsed_last.csv'

def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r

def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find('a', class_='Button Button_color_whiteHoverBlue Button_size_s Button_type_link Button_width_default ListingPagination-module__page').get('href')
    if pagination:
        return pagination[-1]
    else:
        return pagination[:-2] + str(1)

def get_brands_url(html):
    soup = BeautifulSoup(html, 'html.parser')
    brends = soup.find_all('a', class_='IndexMarks__item')
    brends_list = []
    for brend in brends:
        brend_url = brend.find('a').get('href')
        print(brend_url)
    return brends_list

def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='ListingItem-module__container')
    links = []
    for item in items:
        links.append({
            'link': item.find('a').get('href'),
        })
    return links


def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Links'])
        for item in items:
            writer.writerow([item['link']])


def parse():
    global URL, CAR_BRANDS, USED
    cars = []
    for brand in CAR_BRANDS:
        URL_FULL = URL + str(brand) + USED
        print(URL_FULL)
        html = get_html(URL_FULL)
        if html.status_code == 200:
            pages_count = 99
            for page in range(1, pages_count + 1):
                try:
                    print(f'Парсинг страницы {page} из {pages_count}...')
                    html = get_html(URL_FULL, params={'page': page})
                    cars.extend(get_content(html.text))
                except: continue
        else:
            print('Error')
    print(f'Получено {len(cars)} автомобилей')
    save_file(cars, FILE)
    os.startfile(FILE)

parse()
print("--- %s seconds ---" % (time.time() - start_time))