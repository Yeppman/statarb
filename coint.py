
from statsmodels.tsa.stattools import coint
import requests
import time
import pandas as pd
curr_time = round(time.time())
start_date = curr_time*1000 -30*24*60*60*1000
print (start_date)

pairs = ['ETHUSD', 'BTCUSD','XMRUSD','DSHUSD','LTCUSD', 'XRPUSD']
final_df = pd.DataFrame()
for pair in pairs:
	final_list=[]
	print(pair)
	for _ in range(0,2):
		time.sleep(3)
		r = requests.get('https://api.bitfinex.com/v2/candles/trade:30m:t'+pair+'/hist?sort=1&start='+str(start_date)+'&limit=1000')
		if r.status_code == 200:
			res =eval(r.content)
			if not final_list and len(res) !=0:
				final_list= res
			else:
				final_list = final_list+res
			
			start_date = res[-1][0]+30*60*1000
			res=[]
		
	df = pd.DataFrame(final_list)
	df.set_index(0)
	


	final_df[pair]= df[2]
	
	start_date = curr_time*1000 - 30*24*60*60*1000
final_df.dropna(inplace=True)
print(final_df.head())



def get_tradable_pairs():
		# self.returns_df = self.get_returns()
		pairs_list=[]
		adf_list=[]
		
		for i in list(final_df):
			for j in list(final_df):
				if(i != j):
					
					pairs= i+"-"+j

					coint_res = coint(final_df[i],final_df[j]) 
					print(pairs, coint_res)
					if coint_res[1]<0.05:
						pairs_list.append(pairs)
						adf_list.append(coint_res[1])
		df= pd.DataFrame({'pairs' : pairs_list, 'adf': adf_list})
		df.set_index('pairs', inplace=True)
		
		drop_list=[]
		for row_number, row in df.iterrows():
			inv_row = row_number.split('-')[1]+'-'+row_number.split('-')[0]
			if inv_row in df.index:
					
				if df.loc[inv_row]['adf'] < df.loc[row_number]['adf']:
					drop_list.append(row_number)
				else:
					drop_list.append(inv_row)
		df.drop(drop_list, inplace=True)
		print(df.index.values)


get_tradable_pairs()