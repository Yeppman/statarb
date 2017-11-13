from pymongo import MongoClient
import os
import numpy as np
from BitfinexTrade import BitfinexTrade
from Stat import Stat
from Risk import Risk
from Position import Position
import time
import threading
import socketio
import eventlet
import eventlet.wsgi
from flask import Flask, jsonify, render_template

sio = socketio.Server()
app = Flask(__name__)

#connection to remote db
client = MongoClient('mongodb://statarb:P%40ssw0rd@ds259305.mlab.com:59305/statarb')
db = client.statarb
db_data = db.data




@app.route('/')
def Welcome():
    return render_template('index.html')


def run():
	
	risk = Risk()
	pos = Position()
	bfxTrade = BitfinexTrade()
	pairs = bfxTrade.pairs
	print('Trading ', pairs)
	print('Preparing prices')
	bfxTrade.prepare_close_dataframe()
	stat = Stat()
	
	print('Starting event loop')
	while True:
		
		bfxTrade.get_tickers()
		spread_df = stat.get_spread(bfxTrade.close_df)
		zscore_df = stat.get_zscore(spread_df)
		
		zscore = zscore_df[pairs].iat[-1]
		
	
		pair1= pairs.split('-')[0]
		pair2= pairs.split('-')[1]
		pair1_p =bfxTrade.close_df[pair1].iat[-1]
		pair2_p =bfxTrade.close_df[pair2].iat[-1]
		print('zscore ',zscore, ' ',pair1,' price ',pair1_p, ' ',pair2,' price ',pair2_p)
		if not bfxTrade.opened_position:
			if zscore >3:
				amount1= pos.get_position_size(risk.account_risk, risk.pl_risk, bfxTrade.init_amount, pair1_p)
				amount2=pos.get_position_size(risk.account_risk, risk.pl_risk, bfxTrade.init_amount, pair2_p)
				print('short ',pair1,' ',pair1_p,' amount ',amount1,' long ',pair2,' ',pair2_p,' amount ', amount2)
				bfxTrade.backtest_trade(pair1,pair1_p, amount1, 'sell', 'short')
				bfxTrade.backtest_trade(pair2,pair2_p, amount2, 'buy', 'long')
				save_data(pair1,pair1_p, amount1,'short', pair2, pair2_p, amount2,'long', bfxTrade.init_amount)

				bfxTrade.opened_position = True
				bfxTrade.long =pair2
				bfxTrade.short =pair1

			elif zscore <-3:
				amount1= pos.get_position_size(risk.account_risk, risk.pl_risk, bfxTrade.init_amount, pair1_p)
				amount2=pos.get_position_size(risk.account_risk, risk.pl_risk, bfxTrade.init_amount, pair2_p)
				print('short ',pair2,' ',pair2_p,' amount ',amount2,' long ',pair1,' ',pair1_p,' amount ',amount1)
				bfxTrade.backtest_trade(pair2,pair2_p, amount2, 'sell', 'short')
				bfxTrade.backtest_trade(pair1,pair1_p, amount1, 'buy', 'long')
				save_data(pair2,pair2_p, amount2,'short', pair1, pair1_p, amount1,'long', bfxTrade.init_amount)

				bfxTrade.opened_position = True
				bfxTrade.long =pair1
				bfxTrade.short =pair2
		else:
			if bfxTrade.long == pair2 and bfxTrade.short == pair1:
				pl = risk.get_pl(bfxTrade.long_price, pair2_p, 'long')+risk.get_pl(bfxTrade.short_price, pair1_p, 'short')
				if pl >0.0 and zscore< 0.2:
					print('buying back ',pair1,' ',pair1_p,' amount ',bfxTrade.short_amount, ' selling ',pair2,' ', pair2_p,' amount ',bfxTrade.long_amount)
					bfxTrade.backtest_trade(pair1,pair1_p, bfxTrade.short_amount, 'buy', 'short')
					bfxTrade.backtest_trade(pair2,pair2_p, bfxTrade.long_amount, 'sell', 'long')
					save_data(pair1,pair1_p, bfxTrade.short_amount,'short', pair2, pair2_p, bfxTrade.long_amount,'long', bfxTrade.init_amount, pl)

					print('Result amount', bfxTrade.init_amount)
					print('P/L ', pl*100,' %')
					bfxTrade.opened_position = False
				elif pl < risk.pl_risk:
					print('Stop loss buying back ',pair1,' ',pair1_p,' amount ',bfxTrade.short_amount, ' selling ',pair2,' ', pair2_p,' amount ',bfxTrade.long_amount)
					bfxTrade.backtest_trade(pair1,pair1_p, bfxTrade.short_amount, 'buy', 'short')
					bfxTrade.backtest_trade(pair2,pair2_p, bfxTrade.long_amount, 'sell', 'long')
					save_data(pair1,pair1_p, bfxTrade.short_amount,'short', pair2, pair2_p, bfxTrade.long_amount,'long', bfxTrade.init_amount, pl)

					print('Result amount', bfxTrade.init_amount)
					print('P/L ', pl*100,' %')
					bfxTrade.opened_position = False
					
			elif bfxTrade.long == pair1 and bfxTrade.short == pair2:
				pl = risk.get_pl(bfxTrade.long_price, pair1_p, 'long')+risk.get_pl(bfxTrade.short_price, pair2_p, 'short')
				if pl >0.0 and zscore>-0.2:
					print('buying back ',pair2,' ',pair2_p,' amount ',bfxTrade.short_amount, ' selling ',pair1,' ', pair1_p,' amount ',bfxTrade.long_amount)
					bfxTrade.backtest_trade(pair2,pair2_p, bfxTrade.short_amount, 'buy', 'short')
					bfxTrade.backtest_trade(pair1,pair1_p, bfxTrade.long_amount, 'sell', 'long')
					save_data(pair2,pair2_p, bfxTrade.short_amount,'short', pair1, pair1_p, bfxTrade.long_amount,'long', bfxTrade.init_amount, pl)

					print('Result amount', bfxTrade.init_amount)
					print('P/L ', pl*100,' %')
					bfxTrade.opened_position = False
				elif pl < risk.pl_risk:
					print('Stop loss buying back ',pair2,' ',pair2_p,' amount ',bfxTrade.short_amount, ' selling ',pair1,' ', pair1_p,' amount ',bfxTrade.long_amount)
					bfxTrade.backtest_trade(pair2,pair2_p, bfxTrade.short_amount, 'buy', 'short')
					bfxTrade.backtest_trade(pair1,pair1_p, bfxTrade.long_amount, 'sell', 'long')
					save_data(pair2,pair2_p, bfxTrade.short_amount,'short', pair1, pair1_p, bfxTrade.long_amount,'long', bfxTrade.init_amount, pl)

					print('Result amount', bfxTrade.init_amount)
					print('P/L ', pl*100,' %')
					bfxTrade.opened_position = False
		time.sleep(1800)

def save_data(pair1, price1, amount1, type1, pair2, price2, amount2, type2, res, pl=0):
	doc = {'pair1': pair1,
			'type1': type1,
			'price1':price1,
			'amount1': amount1,
			'pair2': pair2,
			'type2': type2,
			'price2': price2,
			'amount2': amount2,
			'result_amount':res,
			'pl':pl}
	db_data.insert_one(doc).inserted_id
threading.Thread(target=run, args=()).start()

port = os.getenv('PORT', '5000')
if __name__ == "__main__":
	app = socketio.Middleware(sio, app)
	eventlet.wsgi.server(eventlet.listen(('', int(port))), app)
	

