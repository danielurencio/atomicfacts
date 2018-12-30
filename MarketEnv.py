import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

df = pd.read_csv('fx_daily_EUR_USD.csv',parse_dates=['timestamp'],index_col='timestamp')
df.sort_index(inplace=True)
df['position'] = 0


class MarketEnv(object):
    
    def __init__(self, df, lag, standardize=True, hold=True, test_set=None):
    # Configuration:
        if not len(df) or not lag:
            raise ValueError('No DataFrame or lag has been determined.')
            
        self.df = df.copy()
        self.cols = self.df.columns.tolist()[:-1]
        self.lag = lag
        self.standardize = standardize
        self.hold = hold
        self.laggedFeatures = self.generate_LaggedDataset()
        self.step_ix = 0
        self.price = None
        self.last_step_ix = (len(self.df) - self.lag)


    def data_AsMovingWindow(self):
    # Arrange each feature as a lagged moving window:
        df = self.df
        cols = self.cols
        arr = []

        for i in range(len(df)):
            fn = lambda x: df[x].values[i:i+self.lag].tolist()
            vals = list(map(fn,cols))
            arr.append(vals)

        # Remove observations that don't have a length equal to the value specified by the variable 'lag':
        arr = arr[:-(self.lag - 1)]
        
        return arr

    
    def generate_LaggedDataset(self):
        
        arr = self.data_AsMovingWindow()
        self.scaler = StandardScaler()
        
        def standardizeValues(col):
            '''fn: isolate each set of observations and arrange it as a moving window'''
            index = col[0]
            column_name = col[1]

            fn = lambda x:x[index]
            feature_vector = map(fn,arr)

            cond = column_name not in ['position','balance']

            if self.standardize and cond:
                data = list(feature_vector)
                self.scaler.fit(data)
                result = self.scaler.transform(data, copy=True)
                #result = self.scaler.fit_transform(list(feature_vector)).tolist()
                
            else:
                result = list(feature_vector)

            return result

        laggedFeatures = list(map(standardizeValues,enumerate(self.cols)))
        
        return laggedFeatures



    def add_TradePosition(self,nth):
        #
        # 'features' variable:
        # Stores a set with the nth position of all available features (as a list/array):
        #   e.g: { [lagged_feature_1], [lagged_feature_2], ..., [lagged_feature_n] }
        #
        features = map(lambda x:self.laggedFeatures[x][nth],range(len(self.laggedFeatures)))
        
        # The next line allows to add dinamically changed features on the fly:
        concatenation = list(features) + [ self.df.iloc[nth:nth+self.lag].position.tolist() ]
        
        # Combine all features in one single vector:
        zippedFeatures = list(zip(*concatenation))
        
        return np.array(zippedFeatures)
    
    
    def actionLogic(self,action):
        #
        # This index let's us know what are the values of the lastest step such as:
        #   * The closing price.
        #   * Whether we had a short or a long position in order to:
        #       - Close the position if we open an opposite transaction.
        #       - Hold the position if we pass or execute the same transaction.
        #
        self.index = (self.step_ix + self.lag) - 1         # This is where we calculate this index.
        self.latest_step = self.df.iloc[self.index].copy() # This is how we use it: getting the latest step,
                                                           #  and its attriutes (closing price, kind of transaction)
            
        def positionType_givenAction(condition,positionType):
            
            if self.hold:
                if self.latest_step.position:
                    # If we have a position and an opposite one is afterward placed:
                    if condition:#self.latest_step.position > 0:
                        # Get rid of position:
                        next_position = 0
                    # Else, if the position is the same as the one already held:
                    else:
                        # Keep this position.
                        next_position = positionType
                else:
                    next_position = positionType
                    
            else:
                next_position = positionType
                
            return next_position
        
        
            
        if action == 0:
            # Sell:
            # If we SELL and the PREVIOUS open position is POSITIVE, handle it:
            next_position = positionType_givenAction(self.latest_step.position > 0, -1)

        elif action == 1:
            # Buy:
            # If we BUY and the PREVIOUS open position is NEGATIVE, handle it:
            next_position = positionType_givenAction(self.latest_step.position < 0, 1)
                
        elif action == 2:
            # Pass:
            next_position = self.latest_step.position
        
        # All steps forward are set to the value specified by 'next_position'
        self.df.loc[self.df.iloc[self.index:].index,'position'] = next_position


                
    def calculateReward(self):

        lastTwo = self.df.iloc[self.index-1:self.index+1]
        lastPositions = lastTwo.position.tolist()
        change = [lastPositions[0]] * len(lastTwo) != lastPositions

        if change:
            # If we are either opening a position for the firt time or closing one without re-opening another:
            latestPrice = lastTwo.close[-1]
            
            if 0 in lastPositions:
                # If we previously did not have an open transaction and now we do:
                if lastPositions[-1] and not lastPositions[-2]:
                    self.price = lastTwo.close[-1]
                    reward = 0

                # If we get rid of a position:
                else:
                    reward = latestPrice - self.price if lastPositions[-1] == 1 else self.price - latestPrice
                    self.price = None
            
            # If we transition from one kind of position to another without the 'hold' config:
            else:
                reward = latestPrice - self.price if lastPositions[-1] == 1 else self.price - latestPrice
                self.price = latestPrice

        else:
            reward = 0
        
        return reward

    
    def reset(self):
        state = self.add_TradePosition(0)
        self.step_ix = 1
        return state
    
        
    def step(self,action):
        
        if self.step_ix == 0:
            raise ValueError('You need to run reset first.')
        
        self.actionLogic(action)
        
        reward = self.calculateReward()
        state = self.add_TradePosition(self.step_ix)
                
        if self.last_step_ix > self.step_ix:
            done = False
            self.step_ix += 1
            
        else:
            done = True
            self.step_ix = self.last_step_ix

        result = (state,reward,done)
        
        return result
