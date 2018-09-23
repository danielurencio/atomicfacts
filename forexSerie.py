import json
import requests
from time import sleep
from datetime import datetime
from pymongo import MongoClient


pair_ids = \
[
    ["EUR_USD","1"],
    ["USD_JPY","3"],
    ["GBP_USD","2"],
    ["USD_CHF","4"],
    ["USD_CAD","7"],
    ["EUR_JPY","9"],
    ["AUD_USD","5"],
    ["NZD_USD","8"],
    ["EUR_GBP","6"],
    ["EUR_CHF","10"],
    ["AUD_JPY","49"],
    ["GBP_JPY","11"],
    ["CHF_JPY","13"],
    ["EUR_CAD","16"],
    ["AUD_CAD","47"],
    ["CAD_JPY","51"],
    ["NZD_JPY","58"],
    ["AUD_NZD","50"],
    ["GBP_AUD","53"],
    ["EUR_AUD","15"],
    ["GBP_CHF","12"],
    ["EUR_NZD","52"],
    ["AUD_CHF","48"],
    ["GBP_NZD","55"],
    ["USD_INR","160"],
    ["USD_CNY","2111"],
    ["USD_SGD","42"],
    ["USD_HKD","155"],
    ["USD_DKK","43"],
    ["GBP_CAD","54"],
    ["USD_SEK","41"],
    ["USD_RUB","2186"],
    ["USD_TRY","18"],
    ["USD_MXN","39"],
    ["USD_ZAR","17"],
    ["CAD_CHF","14"],
    ["NZD_CAD","56"],
    ["NZD_CHF","57"],
    ["BTC_USD","945629"],
    ["BTC_EUR","1010801"],
    ["ETH_USD","997650"]
]




def paramsParse(symbol,to):
    params = {
        'symbol':symbol,
        'resolution':'D',
        'from':'0',
        'to':to
    }

    params = map(lambda x:'='.join(x),params.items())
    params = '&'.join(params)
    return params




def get_forexPairData(symbol,to):
    params = paramsParse(symbol,to)
    url = 'https://tvc4.forexpros.com/7cb640281e0d1f3943e7a8cd04634abc/1537593163/1/1/8/history?' +\
            params

    headers = {
        'Accept':'*/*',
        'Referer':'https://tvc-invdn-com.akamaized.net/web/1.12.23/index58-prod.html?carrier=7cb640281e0d1f3943e7a8cd04634abc&time=1537593163&domain_ID=1&lang_ID=1&timezone_ID=8&version=1.12.23&locale=en&timezone=America/New_York&pair_ID=1&interval=15&session=24x7&prefix=www&suffix=&client=0&user=guest&family_prefix=tvc4&init_page=instrument&sock_srv=https://stream36.forexpros.com:443&m_pids=&watchlist=&geoc=MX',
        'Origin':'https://tvc-invdn-com.akamaized.net',
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        'Content-Type':'text/plain'
    }

    res = requests.get(url,headers=headers).text
    res = json.loads(res)
    res = [res['t'],res['o'],res['h'],res['l'],res['c']]
    res = [ {'time':res[0][i], 'open':res[1][i], 'high':res[2][i], 'close':res[3][i] } for i,d in enumerate(res[0]) ]

    return res




def getAllPairs():
    now = datetime.now().strftime('%s')
    db = MongoClient('mongodb://localhost:27017')['forex']

    for i in pair_ids:
        data = get_forexPairData(i[1],now)
        db[i[0]].insert(data)
        print(i[0])
        sleep(2)

