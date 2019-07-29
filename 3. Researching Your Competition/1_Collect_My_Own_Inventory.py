# VIDEO1: Collect my own inventory

import os
import requests
import datetime
from bs4 import BeautifulSoup
from datetime import timedelta
from ebaysdk.finding import Connection as finding


my_seller_name = 'dreidrivera2016'
timecode = ''.join([i for i in str(datetime.datetime.now()) if i.isnumeric()])
if not os.path.exists('results/'): os.makedirs('results/')
filename_output = 'results/1_inventory_for_'+my_seller_name+'_'+timecode+'.txt'
if not os.path.isfile(filename_output):
    file_output = open(filename_output,'w',encoding='UTF-8',errors='SURROGATEESCAPE')
    file_output.close()
    
my_app_id = open('support files/listappid.txt').readlines()[0].strip()
api = finding(appid=my_app_id, config_file=None)
max_pages = 101
list_itemdetails = []

print('collecting inventory of: ' + my_seller_name)
input('press ENTER to continue')
print()

for page_number in range(1, max_pages):
    dct_request = {
        'keywords': ' ',
        'paginationInput': {'pageNumber': str(page_number)},
        'itemFilter': [{'name': 'Seller', 'value': my_seller_name}]}
    response_api = api.execute('findItemsAdvanced', dct_request)
    soup_api = BeautifulSoup(response_api.text,'lxml')
    itemdetails = [
        [i.itemid.text, i.title.text, i.categoryid.text, i.categoryname.text, i.viewitemurl.text] for i in soup_api.find_all('item')]
    for item in itemdetails: list_itemdetails.append(item)
    if soup_api.totalpages.text >= str(page_number): break

for item in list_itemdetails:
    item_id = item[0]
    item_title = item[1]
    item_catcode = item[2]
    item_catname = item[3]
    item_url = item[4]
    print()
    print(item_title)

    response_site = requests.get(item_url)
    soup_site = BeautifulSoup(response_site.text,'lxml')
    list_attribute_labels = soup_site.find_all('td',{'class':'attrLabels'})
    
    try: upc_code = [i for i in list_attribute_labels if i.text.strip().lower()=='upc:'][0]\
                    .find_next_sibling().text.strip().lower().replace('does not apply', 'no_upc')
    except: upc_code = 'no upc'
    try: mpn_code = [i for i in list_attribute_labels if i.text.strip().lower()=='mpn:'][0]\
                    .find_next_sibling().text.strip().lower().replace('does not apply', 'no_mpn')
    except: mpn_code = 'no mpn'
    try: ean_code = [i for i in list_attribute_labels if i.text.strip().lower()=='ean:'][0]\
                    .find_next_sibling().text.strip().lower().replace('does not apply', 'no_ean')
    except: ean_code = 'no ean'
    try: isbn_code = [i for i in list_attribute_labels if i.text.strip().lower()=='isbn:'][0]\
                     .find_next_sibling().text.strip().lower().replace('does not apply', 'no_isbn')
    except: isbn_code = 'no isbn'

    file_output = open(filename_output,'a',encoding='UTF-8',errors='SURROGATEESCAPE')
    file_output.write('\t'.join([item_id, upc_code, mpn_code, ean_code, isbn_code, item_title, item_catcode, item_catname, item_url])+'\n')
    file_output.close()

