import os
import csv
import time
import requests
import datetime
import traceback
import pandas as pd
import dateutil.parser
from bs4 import BeautifulSoup
from datetime import timedelta
from ebaysdk.finding import Connection as finding

datetimeFormat = '%Y-%m-%dT%H:%M:%S.000Z'
StartFromDays = 120
df = pd.read_csv('Collected Results/price comparison tool/index.csv')
filename_outputcsv = 'Collected Results/get ebay sales history/index.csv'
filename_progresstracker = 'Continue/get ebay sales history/progress tracker.txt'

myappid = 'appid_goes_here'
api = finding(appid=myappid, config_file=None)

if not os.path.exists('Collected Results/get ebay sales history/'):
    os.makedirs('Collected Results/get ebay sales history/')
if not os.path.exists('Continue/get ebay sales history/'):
    os.makedirs('Continue/get ebay sales history/')
if not os.path.isfile(filename_progresstracker):
    file = open(filename_progresstracker,'w')
    file.close()
    
list_columnnames = [
    'upcx',
    'totalentries_active',
    'totalentries_sold',
    'totalentries_unsold',     
    'title_hd',
    'title_wm',
    'title_eb',
    'price_hd',
    'price_wm',
    'price_eb',
    'cheapest',
    'pct_cheapest',
    'dollars_cheapest',
    'conditiondisplayname',
    'listingtype',
    'categoryid',
    'categoryname',
    'currentprice',
    'sellingstate',
    'starttime',
    'endtime',
    'endedindays',
    'sellerusername',
    'feedbackscore',
    'positivefeedbackpercent',
    'viewitemurl',
]
if not os.path.isfile(filename_outputcsv):
    with open(filename_outputcsv, 'w', encoding='UTF-8',errors='surrogateescape', newline='') as File_Csv:
        ListCsvWriter = csv.writer(File_Csv, delimiter=',')
        ListCsvWriter.writerow(list_columnnames)


for rownumber in range(len(df)):
    file_progresstracker = [i.strip() for i in open(filename_progresstracker).readlines()]
    rowdata = df.iloc[rownumber]

    #columns from my dataframe
    upcx = rowdata.upcx
    upc = rowdata.upcx.replace('x','')
    if upcx in file_progresstracker: continue

    title_hd = rowdata.title_hd
    title_wm = rowdata.title_wm
    title_eb = rowdata.title_eb
    price_hd = float(rowdata.price_hd)
    price_wm = float(rowdata.price_wm)
    price_eb = float(rowdata.price_eb)
    cheapest = rowdata.cheapest
    pct_cheapest = rowdata.pct_cheapest
    dollars_cheapest = rowdata.dollars_cheapest

    print()
    print('row: ' + str(rownumber) + '/' + str(len(df)))
    print(upc)
    print(title_hd)
    
    # Input Values
    Keywords = upc
    value_solditemsonly = False
    value_listingtype = 'FixedPrice'
    value_outputselector = 'SellerInfo'
    value_condition = 'New'
    value_timestartfrom = ''.join(str(datetime.datetime.today() - timedelta(days=StartFromDays))\
                                  .replace(' ','T').split('.')[:-1]) + '.000Z'
    value_timeendto = ''.join(str(datetime.datetime.today())\
                              .replace(' ','T').split('.')[:-1]) + '.000Z' 
    value_locatedin = 'US'
    value_pricemin = price_hd+(price_hd*.3)
    if price_hd == 0:
        if price_wm == 0: continue
        value_pricemin = price_wm+(price_wm*.3)

    # Completed Request
    value_pagenumber = 1
    dct_completedrequest = { 
        'keywords': Keywords,
        'paginationInput': {'pageNumber': value_pagenumber},
##        'categoryId': value_categoryid,
        'outputSelector': value_outputselector,
        'itemFilter': [
            {'name': 'Condition', 'value': value_condition},
            {'name': 'SoldItemsOnly', 'value': value_solditemsonly},
            {'name': 'ListingType', 'value': value_listingtype},
            {'name': 'MinPrice', 'paramName': 'USD', 'value': value_pricemin},
            {'name': 'StartTimeFrom', 'value': value_timestartfrom},
            {'name': 'EndTimeTo', 'value': value_timeendto},
            {'name': 'LocatedIn', 'value': value_locatedin},     
    ]}                
    try: response_completeditems = api.execute('findCompletedItems', dct_completedrequest)
    except: traceback.print_exc()


    # Active Request
    value_pagenumber = 1
    dct_activerequest = { 
        'keywords': Keywords,
        'paginationInput': {'pageNumber': value_pagenumber},
##        'categoryId': value_categoryid,
        'outputSelector': value_outputselector,
        'itemFilter': [
            {'name': 'Condition', 'value': value_condition},
            {'name': 'ListingType', 'value': value_listingtype},
            {'name': 'MinPrice', 'paramName': 'USD', 'value': value_pricemin},
            {'name': 'LocatedIn', 'value': value_locatedin},
    ]}  
    try: response_active = api.execute('findItemsAdvanced', dct_activerequest)
    except: traceback.print_exc()
    

    # Parse It Out Now, Yall
    soup_completed = BeautifulSoup(response_completeditems.text,'lxml')
    if soup_completed.ack.text.lower() != 'success': print('bad request')
    totalentries_completed = int(soup_completed.totalentries.text)
    totalpages_completed = int(soup_completed.totalpages.text)
    totalentries_sold = len([i for i in soup_completed.find_all('item') if i.sellingstate.text == 'EndedWithSales'])
    totalentries_unsold = len([i for i in soup_completed.find_all('item') if i.sellingstate.text == 'EndedWithoutSales'])
    list_pageitems = soup_completed.find_all('item')
        
    if totalentries_sold > 0: 
        firstitem = soup_completed.find_all('item')[0]
        conditiondisplayname = firstitem.conditiondisplayname.text
        listingtype = firstitem.listingtype.text
        categoryid = firstitem.categoryid.text
        categoryname = firstitem.categoryname.text
        currentprice = firstitem.currentprice.text
        sellingstate = firstitem.sellingstate.text
        starttime = dateutil.parser.parse(str(firstitem.starttime.text))
        endtime =  dateutil.parser.parse(str(firstitem.endtime.text))
        endedindays = str((endtime-starttime).days)
        sellerusername = firstitem.sellerusername.text
        feedbackscore = firstitem.feedbackscore.text
        positivefeedbackpercent = firstitem.positivefeedbackpercent.text
        viewitemurl = firstitem.viewitemurl.text
    elif totalentries_sold == 0:
        conditiondisplayname = 'none'
        listingtype = 'none'
        categoryid = 'none'
        categoryname = 'none'
        currentprice = 'none'
        sellingstate = 'none'
        starttime = 'none'
        endtime = 'none'
        endedindays = 'none'
        sellerusername = 'none'
        feedbackscore = 'none'
        positivefeedbackpercent = 'none'
        viewitemurl = 'none'
        
    soup_active = BeautifulSoup(response_active.text,'lxml')
    if soup_active.ack.text.lower() != 'success': print('bad request')
    totalentries_active = int(soup_active.totalentries.text)
    totalpages_active = int(soup_active.totalpages.text)

    print('catcode: ' + categoryid)
    print('catname: ' + categoryname)
    print('totalentries_sold: ' + str(totalentries_sold))
    print('totalentries_unsold: ' + str(totalentries_unsold))
    print('totalentries_active: ' + str(totalentries_active))

    list_outputdetails = [
        upcx,
        totalentries_active,
        totalentries_sold,
        totalentries_unsold,      
        title_hd,
        title_wm,
        title_eb,
        price_hd,
        price_wm,
        price_eb,
        cheapest,
        pct_cheapest,
        dollars_cheapest,
        conditiondisplayname,
        listingtype,
        categoryid,
        categoryname,
        currentprice,
        sellingstate,
        starttime,
        endtime,
        endedindays,
        sellerusername,
        feedbackscore,
        positivefeedbackpercent,
        viewitemurl,
    ]
    with open(filename_outputcsv, 'a', encoding='UTF-8',errors='surrogateescape', newline='') as File_Csv:
        ListCsvWriter = csv.writer(File_Csv, delimiter=',')
        ListCsvWriter.writerow(list_outputdetails)

    file = open(filename_progresstracker,'a')
    file.write(upcx+'\n')
    file.close()

