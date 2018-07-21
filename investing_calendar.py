import json
import requests
import calendar
import numpy as np
from datetime import datetime
from bs4 import BeautifulSoup as bs



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
        ('country[]','72'),
        ('country[]','5'),
        ('category[]','_employment'),
        ('category[]','_economicActivity'),
        ('category[]','_inflation'),
        ('category[]','_credit'),
        ('category[]','_centralBanks'),
        ('category[]','_confidenceIndex'),
        ('category[]','_balance'),
        ('category[]','_Bonds'),
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



if __name__ == '__main__':
    bimesters = Bimesters()
    bimesterCalendar = getBimesterCalendar(bimesters[0])
    ids = extractIDsFromCalendar(bimesterCalendar)
    print(ids)
