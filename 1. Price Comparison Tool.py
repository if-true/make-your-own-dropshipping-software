import os
import csv
import traceback
from selenium import webdriver


pathname_continue = 'Continue/1. index/'
pathname_collectedresults = 'Collected Results/1. index/'
filename_outputcsv = pathname_collectedresults + 'index.csv'
if not os.path.exists(pathname_continue): os.makedirs(pathname_continue)
if not os.path.exists(pathname_collectedresults): os.makedirs(pathname_collectedresults)

list_upc = [i.replace('x','').strip() for i in open('upcx.txt').readlines()]
list_websites = ['HomeDepot','Walmart','Ebay']
list_columnnames = [
    'upcx',
    'title_hd',
    'price_hd',

    'cheapest',
    'pct_cheapest',
    'dollars_cheapest',
]
if not os.path.isfile(filename_outputcsv):
    with open(filename_outputcsv, 'w', encoding='UTF-8',errors='surrogateescape', newline='') as File_Csv:
        ListCsvWriter = csv.writer(File_Csv, delimiter=',')
        ListCsvWriter.writerow(list_columnnames)


web = webdriver.Chrome('support files/chromedriver.exe')
for myupc in list_upc:
    upcx = 'x'+myupc
    if os.path.isfile(pathname_continue+upcx): continue
    print('upc: ' + myupc)
    
    # Collecting HomeDepot
    try:
        url_homedepot = 'https://www.homedepot.com/s/%2522'+myupc+'%2522?NCNI-5'
        web.get(url_homedepot)
        title_homedepot = web.find_element_by_class_name('')
        price_homedepot = web.find_element_by_class_name('')
        price_homedepot = price_homedepot.replace('$','').replace(',','')
        print('HomeDepot:')
        print(title_homedepot)
        print(price_homedepot)
        print()
    except:
        traceback.print_exc()
        title_homedepot = '0'
        price_homedepot = '0'

    
    # Save Output To Csv
    list_itemdetails = [
        upcx,
        title_homedepot,
        price_homedepot,

        cheapestsite,
        pct_cheapest,
        dollars_cheapest,
    ]
    with open(filename_outputcsv, 'a', encoding='UTF-8',errors='surrogateescape', newline='') as File_Csv:
        ListCsvWriter = csv.writer(File_Csv, delimiter=',')
        ListCsvWriter.writerow(list_itemdetails)


    #write to "path_continue"
    file = open(pathname_continue+upcx,'w')
    file.close()
    



