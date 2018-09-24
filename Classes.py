import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from datetime import datetime
from pprint import pprint
from pymongo import MongoClient

class Instrument(object):
    def __init__(self,instrument):
        self.db = db = MongoClient('mongodb://localhost:27017').forex
        self.name = instrument
        self.data = self.get_data(instrument)

    # Turns data into a Pandas DataFrame:
    def createDF(self):
        self.df = pd.DataFrame(self.data)
        self.df['time'] = self.df['time'].map(lambda x:datetime.fromtimestamp(x))        
    
    # Queries an instrument's daily prices from the database:
    def get_data(self,instrument):
        cursor = self.db[instrument].find({},{ '_id':0 })
        data = [ d for d in cursor ]
        return data
    
    # Gets a single value from the OHLC set:
    def ohlc(self,st):
        data = map(lambda x:x[st],self.data)
        data = list(data)
        return data
    
    # Arranges data as a n-lagged serie:
    def n_lags(self,arr,lag):
        lags = [ arr[i:i+lag] for i,d in enumerate(arr) ]
        ff = filter(lambda x:len(x) == lag, lags)
        ff = list(ff)
        return ff

    # Returns regression parameters of an n-lagged serie:
    def F_LinReg(self,arr):
        x = list(range(len(arr)))
        y = arr
        A = np.vstack([np.ones_like(x),x]).T
        params = list(np.linalg.lstsq(A,y,rcond=None)[0])
        return params

    # Returns de average of an n-lagged serie:
    def F_MAverage(self,arr):
        return np.mean(arr)

    # Returns de Bollinger Bands of an n-lagged serie:
    def F_BBands(self,arr):
        m = np.mean(arr)
        std = np.std(arr)
        upper = m + std
        lower = m - std
        return [upper,lower]
    
    # Makes sure that objects returned by methods have the same size as data:
    def fillNan(self,arr):
        n = len(self.data) - len(arr)
        arr_cols = arr.shape[1] if len(arr.shape) > 1 else 1
        nans = np.array( [ np.nan for j in range(arr_cols) ] * n )
        nans = nans.reshape((n,arr.shape[1])) if len(arr.shape) > 1 else nans
        filledObj = np.concatenate([nans,arr])
        return filledObj
    
    # Generate DataFrame with all computable features:
    def addFeatures(self,st,lag):
        self.createDF()
        data = self.ohlc(st)
        data = self.n_lags(data,lag)
        features = filter(lambda x:re.match('^F_',x),dir(self))
        for f in features:
            method = map(getattr(self,f),data)
            method = np.array(list(method))
            method = self.fillNan(method)
            name = '_'.join([f,str(lag),st])
            name = re.sub('F_','',name)
            
            if(len(method.shape) > 1):
                names = map(lambda x:'_'.join([name,str(x)]),range(method.shape[1]))
                names = list(names)
                
                for i,d in enumerate(names):
                    self.df[d] = method[:,i]
            else:
                self.df[name] = method
                
        self.df.dropna(inplace=True)
        self.df.set_index('time',inplace=True)

