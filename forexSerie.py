import json
import requests
import numpy
from datetime import datetime


pair_ids = \
[
    ["EUR/USD","1"],
    ["USD/JPY","3"],
    ["GBP/USD","2"],
    ["USD/CHF","4"],
    ["USD/CAD","7"],
    ["EUR/JPY","9"],
    ["AUD/USD","5"],
    ["NZD/USD","8"],
    ["EUR/GBP","6"],
    ["EUR/CHF","10"],
    ["AUD/JPY","49"],
    ["GBP/JPY","11"],
    ["CHF/JPY","13"],
    ["EUR/CAD","16"],
    ["AUD/CAD","47"],
    ["CAD/JPY","51"],
    ["NZD/JPY","58"],
    ["AUD/NZD","50"],
    ["GBP/AUD","53"],
    ["EUR/AUD","15"],
    ["GBP/CHF","12"],
    ["EUR/NZD","52"],
    ["AUD/CHF","48"],
    ["GBP/NZD","55"],
    ["USD/INR","160"],
    ["USD/CNY","2111"],
    ["USD/SGD","42"],
    ["USD/HKD","155"],
    ["USD/DKK","43"],
    ["GBP/CAD","54"],
    ["USD/SEK","41"],
    ["USD/RUB","2186"],
    ["USD/TRY","18"],
    ["USD/MXN","39"],
    ["USD/ZAR","17"],
    ["CAD/CHF","14"],
    ["NZD/CAD","56"],
    ["NZD/CHF","57"],
    ["BTC/USD","945629"],
    ["BTC/EUR","1010801"],
    ["ETH/USD","997650"]
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


def forexPros(symbol,to):
    params = paramsParse(symbol,to)
    url = 'https://tvc4.forexpros.com/7cb640281e0d1f3943e7a8cd04634abc/1537593163/1/1/8/history?' +\
            params
    #symbol='+symbol+'&resolution=D&from=1506489180&to=1537593241'

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
