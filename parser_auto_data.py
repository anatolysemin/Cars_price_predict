import requests
from bs4 import BeautifulSoup
import csv
import os
import pandas as pd
import time
start_time = time.time()

DF = pd.read_csv('cars_parsed_last.csv').Links
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0', 'accept': '*/*'}
HOST = 'https://auto.ru/'
FILE = 'cars_data.csv'

def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    r.encoding = 'utf8'
    return r

def clean_price(text):
    digits = [symbol for symbol in text if symbol.isdigit()]
    cleaned_text = ''.join(digits)
    if not cleaned_text:
        return None
    return int(cleaned_text)

def find_auto_main(html):
    soup = BeautifulSoup(html, 'html.parser')
    list_options = ['bodyType', 'brand', 'color', 'fuelType', 'modelDate', 'name',
       'numberOfDoors', 'productionDate', 'vehicleConfiguration',
       'vehicleTransmission', 'engineDisplacement', 'enginePower',
       'description', 'mileage', 'Комплектация', 'Привод', 'Руль', 'Состояние',
       'Владельцы', 'ПТС', 'Таможня', 'Владение', 'id', 'price']
    dict_auto = {'price' :0}
    is_notSold = True 
    j = 0
    if len(soup.select(".CardSold__title"))>0: # Машина уже продана 
        is_notSold = False  
    for li in soup.select(".LayoutSidebar__content"):           
         for i in li.find_all('meta'):
             if (i['itemprop'] in list_options):
                 if is_notSold  or i['itemprop'] != 'price':
                     if  i['itemprop'] == 'name':
                         dict_auto[i['itemprop'] + str(j)] = i['content']
                         j += 1
                     else:    
                         dict_auto[i['itemprop']] = i['content']
    ownership = soup.find('li', class_='CardInfo__row_owningTime')
    if ownership:
        ownership = ownership.get_text()
    else: None
    list_equips = {}
    list_values =[]
    for equipments in soup.select(".CardComplectation__groups"):
        for equip in equipments.find_all('div', class_='CardComplectation__group'):
            key = equip.find('span', class_='CardComplectation__itemName').get_text()
            values = equip.find_all('li', class_='CardComplectation__itemContentEl')
            # print(values)
            for value in values:
                list_values.append(value.get_text())
            list_equips[key] = list_values    
    # print(list_equips)
    cars = {
        'mileage': clean_price(soup.find('li', class_='CardInfo__row_kmAge').get_text()),
        'equipment': list_equips,
        'drive': soup.find('li', class_='CardInfo__row_drive').get_text()[6:],
        'steering wheel': soup.find('li', class_='CardInfo__row_wheel').get_text()[4:],
        'condition': soup.find('li', class_='CardInfo__row_state').get_text()[9:],
        'owners': soup.find('li', class_='CardInfo__row_ownersCount').get_text()[9:],
        'passport': soup.find('li', class_='CardInfo__row_pts').get_text()[3:],
        'customs': soup.find('li', class_='CardInfo__row_customs').get_text()[7:],
        'ownership': ownership[8:],
        'id': None,
        }
    dict_auto.update(cars)
    return dict_auto 

def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(list(items[0].keys()))
        # print(items)
        for item in items:
            try:
                writer.writerow([item[name] for name in list(item.keys())])
            except: continue

def parse():
    global DF
    cars = []
    count = 1
    for link in DF:
        try:
            URL = link #[:-11]
            print(URL)
            html = get_html(URL)
        # print(html.text)
            if html.status_code == 200:
                print(f'Парсинг страницы {count} из {len(DF)}...')
                cars.append(find_auto_main(html.text))
                count += 1
            else:
                print('Error')
        except: continue
    print(f'Получено {len(cars)} автомобилей')
    # print(cars)
    save_file(cars, FILE)
    os.startfile(FILE)

parse()
print("--- %s seconds ---" % (time.time() - start_time))