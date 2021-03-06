import json
import requests
import calendar
import numpy as np
from datetime import datetime
from bs4 import BeautifulSoup as bs
from time import sleep
from pymongo import MongoClient



try:
    client = MongoClient('mongodb://localhost:27017')
    db = client.investing.usd_id
    cursor = db.find( {},{'_id':0} )
    arr = [ i for i in cursor ]
except:
    pass




def Bimesters(startYear=1970):
    years = list(range(startYear, datetime.now().year + 1))
    months = list(range(13))[1:]

    arr = []
    counter = 1

    for y in years:
        for m in months:

            days = calendar.monthrange(y,m)[1]
            year = str(y)
            month = str(m) if len(str(m)) == 2 else '0' + str(m)
            day = str(days)

            if(counter % 2):
                bimester = []
                obj = '-'.join([year,month,'01'])
                bimester.append(obj)
                
            else:
                obj = '-'.join([year,month,day])
                bimester.append(obj)
                arr.append(bimester)

            counter += 1

    return arr



## A function to scrape all available countries and their code should be added:
def getBimesterCalendar(bimester):

    url = 'https://www.investing.com/economic-calendar/Service/getCalendarFilteredData'

    headers = {
     'Origin':'https://www.investing.com',
     'Accept-Encoding':'gzip, deflate, br',
     'Accept-Language':'en-US,en;q=0.9',
     'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
     'Content-Type':'application/x-www-form-urlencoded',
     'Accept':'*/*',
     'Referer':'https://www.investing.com/economic-calendar/',
     'X-Requested-With':'XMLHttpRequest',
     'Connection':'keep-alive'
    }

    data = [
#        ('country[]','72'),
        ('country[]','5'),
        ('category[]','_employment'),
        ('category[]','_economicActivity'),
        ('category[]','_inflation'),
        ('category[]','_credit'),
        ('category[]','_centralBanks'),
        ('category[]','_confidenceIndex'),
        ('category[]','_balance'),
        ('category[]','_Bonds'),
        ('importance[]','1'),
        ('importance[]','2'),
        ('importance[]','3'),
        ('dateFrom',bimester[0]),
        ('dateTo',bimester[1]),
        ('timeZone','8'),
        ('timeFilter','timeRemain'),
        ('currentTab','custom'),
        ('limit_from','0')
    ]

    res = requests.post(url,headers=headers,data=data)
    res = json.loads(res.text)['data']
    res = '<html><body><table>' + res + '</html></body></table>'

    return res




def extractIDsFromCalendar(bimesterCalendar):
    rows = bs(bimesterCalendar,'html5lib').select('tr[event_attr_id]')
    hrefs = list( map(lambda x:x.select('a')[0]['href'],rows) )
    
    def lastSplit(sep):
        def splits(x):
            last = len(x.split(sep)) - 1
            return x.split(sep)[last]
        return splits


    def properNames(x):
        arr = x.split('-')
        pName = '-'.join(arr[:len(arr)-1])
        return pName

    names = list( map(lastSplit('/'),hrefs) )
    ids = list( map(lastSplit('-'),names) )
    properN = list( map(properNames,names) )

    datasets = [ { 'serie':properN[i], 'id':ids[i] } for i,d in enumerate(properN) ]

    return datasets




def idsThroughout(bimesters):
    arr = []
    for b in bimesters:
        print('Getting: ',b)
        bimesterCalendar = getBimesterCalendar(b)
        ids = extractIDsFromCalendar(bimesterCalendar)
        arr += ids
        print('Sleep 2 secs...\n')
        sleep(2)

    arr = list( { d['id']: d for d in arr }.values() )
    return arr



def getAllIds():
    bimesters = Bimesters()
    arr = idsThroughout(bimesters)
    with open('ids.json','w') as output:
        json.dump(arr,output)



def getSerie(id):
    url = 'https://sbcharts.investing.com/events_charts/us/'+ id +'.json'

    headers = {
     'Origin':'https://www.investing.com',
     'Accept-Encoding':'gzip, deflate, br',
     'Accept-Language':'en-US,en;q=0.9',
     'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
     'Content-Type':'application/x-www-form-urlencoded',
     'Accept':'*/*',
     'Referer':'https://www.investing.com/economic-calendar/',
     'X-Requested-With':'XMLHttpRequest',
     'Connection':'keep-alive'
    }

    res = requests.get(url,headers=headers)
    res = json.loads(res.text)#['data']
    return res




def downloadSeries(arr,country):
    print(country)

    for i in arr:
        data = getSerie(i['id'])

        print(i['serie'])

        db = client[country]

        if(len(data['attr']) != 0):
            db[i['serie'] + '_attr'].insert_many(data['attr'])
            print('data' + '\n')

        if(len(data['data']) != 0):
            data_ = map(lambda x:{ 'timestamp':x[0],'val':x[1],'is':x[2] }, data['data'])
            data_ = list(data_)
            db[i['serie'] + '_data'].insert_many(data_)
            print('attr' + '\n')


        sleep(2)
        


#if __name__ == '__main__':
    #getAllIds()
