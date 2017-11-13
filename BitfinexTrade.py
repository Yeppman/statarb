import pandas as pd
import requests
import time


class BitfinexTrade:
	def __init__(self):
		self.pairs = 'ETHUSD-DSHUSD'
		self.close_df=None
		self.init_amount = 1000
		self.reserve={}
		self.opened_position = False
		self.long_amount=0
		self.short_amount=0
		self.long_price=0
		self.short_price=0
		self.long=None
		self.short=None

		
		
	def prepare_close_dataframe(self):
		p_arr = self.pairs.split('-')
		final_df = pd.DataFrame()
		for pair in p_arr:
			temp_df = self.get_hist_data(pair)
			
			if final_df.empty:
				final_df = temp_df
				
			else:
				final_df[pair]= temp_df.values
			final_df.dropna(inplace = True)
		self.close_df = final_df[~final_df.index.duplicated(keep='first')]
		

	def get_hist_data(self, pair):
		final_list=[]
		curr_time = round(time.time())
		start_date = curr_time*1000 -7*24*60*60*1000
		time.sleep(3)
		r = requests.get('https://api.bitfinex.com/v2/candles/trade:30m:t'+pair+'/hist?sort=1&start='+str(start_date)+'&limit=1000')
		if r.status_code == 200:
			res =eval(r.content)
			if not final_list and len(res) !=0:
				final_list= res
			else:
				final_list = final_list+res
			
		temp_df = pd.DataFrame(final_list)
		temp_df.set_index(0, inplace=True)
		temp_df.drop([1,3,4,5], axis=1, inplace=True)
		temp_df[pair] = temp_df
		temp_df.drop([2],axis=1,inplace=True)
		return temp_df

	def get_tickers(self):
		pair1= self.pairs.split('-')[0]
		pair2= self.pairs.split('-')[1]
		r = requests.get('https://api.bitfinex.com/v2/tickers?symbols=t'+pair1+',t'+pair2)
		if r.status_code == 200:
			res =eval(r.content)
			curr_time = round(time.time())*1000
			row=[res[0][7],res[1][7]]
			self.close_df.loc[curr_time] = row

	def backtest_trade(self, pair,price, amount, side, type):
		if side == 'buy':
			if type == 'long':
				self.long_amount =amount
				self.init_amount = self.init_amount-self.long_amount*price
				self.long_price = price

			else:
				self.init_amount=self.init_amount+0.996*(2*self.reserve[pair]-amount*price)
			return
		else:
			if type == 'long':
				self.init_amount = self.init_amount+0.996*amount*price
			else:
				self.short_amount = amount
				self.reserve[pair] = self.short_amount*price
				self.init_amount=self.init_amount-self.reserve[pair]
				self.short_price = price
			return

	
