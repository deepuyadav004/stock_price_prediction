# -*- coding: utf-8 -*-
"""VAR.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1q4b1o3iFGk4vqJM4KLE7T2ClDhJo_QC8
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import warnings
warnings.filterwarnings("ignore")



# Fetching data from the server
url = "https://web-api.coinmarketcap.com/v1/cryptocurrency/ohlcv/historical"
param = {"convert":"USD","slug":"bitcoin","time_end":"1601510400","time_start":"1367107200"}
content = requests.get(url=url, params=param).json()
df = pd.json_normalize(content['data']['quotes'])

# Extracting and renaming the important variables
df['Date']=pd.to_datetime(df['quote.USD.timestamp']).dt.tz_localize(None)
df['Low'] = df['quote.USD.low']
df['High'] = df['quote.USD.high']
df['Open'] = df['quote.USD.open']
df['Close'] = df['quote.USD.close']
df['Volume'] = df['quote.USD.volume']

# Drop original and redundant columns
df=df.drop(columns=['time_open','time_close','time_high','time_low', 'quote.USD.low', 'quote.USD.high', 'quote.USD.open', 'quote.USD.close', 'quote.USD.volume', 'quote.USD.market_cap', 'quote.USD.timestamp'])

# Creating a new feature for better representing day-wise values
df['Mean'] = (df['Low'] + df['High'])/2

# Cleaning the data for any NaN or Null fields
df = df.dropna()



# Creating a copy for making small changes
dataset_for_prediction = df.copy()
dataset_for_prediction['Actual']=dataset_for_prediction['Mean'].shift()
dataset_for_prediction=dataset_for_prediction.dropna()

# date time typecast
dataset_for_prediction['Date'] =pd.to_datetime(dataset_for_prediction['Date'])
dataset_for_prediction.index= dataset_for_prediction['Date']

from statsmodels.tsa.vector_ar.var_model import VAR

#predictiion
data=df[['Mean','Close']]
data=np.array(data,dtype='float32')
data=data[:2500]

#Exogeous variables
exo=df[['Open']]
exo=np.array(exo,dtype='float32')
exo=exo[:2500,:]
model=VAR(data,exog=exo)
x=np.array(df['Date'])
model.index=x[:2500]
result=model.fit()
arr=np.array(df['Mean'])

#test data
N=200
ap=arr[-N:]
z=exo[-N:,:]
a2=result.forecast(model.endog,N,z);
act=a2[:,1:]

#VAR model call
print("VAR")
plt.plot(act,color='cyan',label='predicted')
plt.plot(ap,label='actual')
c=0
for i in range(N):
   c+=(act[i]-ap[i])**2
c/=N


#print RMSE
print(c**0.5)
plt.xlabel('Days')
plt.ylabel('Value')
plt.legend()
plt.show()