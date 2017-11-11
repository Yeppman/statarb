
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






@app.route('/')
def Welcome():
    return render_template('index.html')


def run():
	print('Trading ', pairs)
	risk = Risk()
	pos = Position()
	bfxTrade = BitfinexTrade()
	pairs = bfxTrade.pairs
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
		
		if not bfxTrade.opened_position:
			if zscore >3:
				print('short ',pair1,' ',pair1_p,' amount ',pos.get_position_size(risk.account_risk, risk.pl_risk, bfxTrade.init_amount, pair1_p),' long ',pair2,' ',pair2_p,' amount ',pos.get_position_size(risk.account_risk, risk.pl_risk, bfxTrade.init_amount, pair2_p))
				bfxTrade.backtest_trade(pair1,pair1_p, pos.get_position_size(risk.account_risk, risk.pl_risk, bfxTrade.init_amount, pair1_p), 'sell', 'short')
				bfxTrade.backtest_trade(pair2,pair2_p, pos.get_position_size(risk.account_risk, risk.pl_risk, bfxTrade.init_amount, pair2_p), 'buy', 'long')
					

				bfxTrade.opened_position = True
				bfxTrade.long =pair2
				bfxTrade.short =pair1

			elif zscore <-3:
				print('short ',pair2,' ',pair2_p,' amount ',pos.get_position_size(risk.account_risk, risk.pl_risk, bfxTrade.init_amount, pair2_p),' long ',pair1,' ',pair1_p,' amount ',pos.get_position_size(risk.account_risk, risk.pl_risk, bfxTrade.init_amount, pair1_p))
				bfxTrade.backtest_trade(pair2,pair2_p, pos.get_position_size(risk.account_risk, risk.pl_risk, bfxTrade.init_amount, pair2_p), 'sell', 'short')
				bfxTrade.backtest_trade(pair1,pair1_p, pos.get_position_size(risk.account_risk, risk.pl_risk, bfxTrade.init_amount, pair1_p), 'buy', 'long')
				
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
					print('Result amount', bfxTrade.init_amount)
					print('P/L ', pl*100,' %')
					bfxTrade.opened_position = False
				elif pl < risk.pl_risk:
					print('Stop loss buying back ',pair1,' ',pair1_p,' amount ',bfxTrade.short_amount, ' selling ',pair2,' ', pair2_p,' amount ',bfxTrade.long_amount)
					bfxTrade.backtest_trade(pair1,pair1_p, bfxTrade.short_amount, 'buy', 'short')
					bfxTrade.backtest_trade(pair2,pair2_p, bfxTrade.long_amount, 'sell', 'long')
					print('Result amount', bfxTrade.init_amount)
					print('P/L ', pl*100,' %')
					bfxTrade.opened_position = False
					
			elif bfxTrade.long == pair1 and bfxTrade.short == pair2:
				pl = risk.get_pl(bfxTrade.long_price, pair1_p, 'long')+risk.get_pl(bfxTrade.short_price, pair2_p, 'short')
				if pl >0.0 and zscore>-0.2:
					print('buying back ',pair2,' ',pair2_p,' amount ',bfxTrade.short_amount, ' selling ',pair1,' ', pair1_p,' amount ',bfxTrade.long_amount)
					bfxTrade.backtest_trade(pair2,pair2_p, bfxTrade.short_amount, 'buy', 'short')
					bfxTrade.backtest_trade(pair1,pair1_p, bfxTrade.long_amount, 'sell', 'long')
					print('Result amount', bfxTrade.init_amount)
					print('P/L ', pl*100,' %')
					bfxTrade.opened_position = False
				elif pl < risk.pl_risk:
					print('Stop loss buying back ',pair2,' ',pair2_p,' amount ',bfxTrade.short_amount, ' selling ',pair1,' ', pair1_p,' amount ',bfxTrade.long_amount)
					bfxTrade.backtest_trade(pair2,pair2_p, bfxTrade.short_amount, 'buy', 'short')
					bfxTrade.backtest_trade(pair1,pair1_p, bfxTrade.long_amount, 'sell', 'long')
					print('Result amount', bfxTrade.init_amount)
					print('P/L ', pl*100,' %')
					bfxTrade.opened_position = False
		time.sleep(1800)

threading.Thread(target=run, args=()).start()

port = os.getenv('PORT', '5000')
if __name__ == "__main__":
	app = socketio.Middleware(sio, app)
	eventlet.wsgi.server(eventlet.listen(('', int(port))), app)
	


