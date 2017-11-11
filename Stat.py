import matplotlib.pyplot as plt
import numpy as np
import statsmodels.tsa.api as smt
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
import pandas as pd
from pyfinance.ols import PandasRollingOLS

class Stat:
	def __init__(self):
		pass

	
	def get_spread(self, close_df):
		spread = pd.DataFrame()
		
		pair1 = list(close_df)[0]
		pair2 = list(close_df)[1]
		pairs = pair1+'-'+pair2
		rolling_ols = PandasRollingOLS(y=close_df[pair1], x=close_df[pair2], window=20)
		spread[pairs] =close_df[pair1] - rolling_ols.beta['feature1'] * close_df[pair2]
		spread.dropna(inplace=True)
		return spread

	def get_zscore(self, spread):
		
		std_20 = spread.rolling(center=False,window=20).std()
		spread_mavg1 = spread.rolling(center=False,window=1).mean()
		spread_mavg20 = spread.rolling(center=False,window=20).mean()
		df = (spread_mavg1 - spread_mavg20)/std_20
		df.dropna(inplace = True)


		return df
