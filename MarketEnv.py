import pandas as pd
import numpy as np
from Classes import Instrument
from sklearn.preprocessing import MinMaxScaler, StandardScaler


class MarketEnv(Instrument):

    def __init__(self,st='close',instrument='EUR_USD',lags=(5,22)):
        self.step = 0

        self.setData(instrument)

        for i,d in enumerate(lags):
            if i == 0:
                self.addFeatures(st,d)
                self.data_ = self.df.copy()

            else:
                self.addFeatures(st,d)
                self.data_ = self.data_.join(self.df.iloc[:,4:]).dropna()

        self.data_['position'] = 0


    def aa(self):
        data = self.data_.copy()

        lag = 22

        def arrangeData(a,back):
            b = [ a[i:i+back] for i,d in enumerate(a) ]
            b = list(filter(lambda x:len(x) == lag,b) )
            return b

        def scale_(x):
            aa = arrangeData(data[x].tolist(),lag)
            bb = np.array(aa)
            if x != 'position':
                scaler = MinMaxScaler()
                scaler.fit(bb)
                bb = scaler.transform(bb)
            return bb

        def accomodateAsSequences(arr):
            cont = [ [] for d in range(arr[0].shape[0]) ]

            for i in arr:
                for j,d in enumerate(i):
                    cont[j].append(d.tolist())

            cc_ = np.array(list(map(lambda x:list(zip(*x)),cont)))
            return cc_

        cols = data.columns.tolist()
        gg = list(map(scale_,cols))
        gg = accomodateAsSequences(gg)
        return gg


    def reset(self):
        self.step = 0
        return self.step_(1)[0]

    def step_(self,action):
        row = self.data_.iloc[self.step + 0 + 21]
        currentPrice = row['close']
        nextPrice = self.data_.iloc[self.step + 1 + 21]
        ix_ = self.step + 1 + 21
        row_andAhead = self.data_.iloc[ix_:].index
        position = row['position']

        if(action == 0):
            if position == 1:
                reward = self.price - currentPrice
                self.price = currentPrice

            elif position == 0:
                self.price = row['close']
                reward = 0

            else: # position == -1
                reward = 0

            self.data_.loc[row_andAhead,'position'] = -1

        if(action == 2):
            reward = 0

        if(action == 1):
            if position == -1:
                reward = currentPrice - self.price
                self.price = currentPrice

            elif position == 0:
                self.price = currentPrice
                reward = 0

            else: # positino == 1
                reward = 0

            self.data_.loc[row_andAhead,'position'] = 1

        finish = None if self.step < len(self.data_)-1 else True
        self.step += 1
        state = self.aa()[self.step]
        return [state,reward,finish]
