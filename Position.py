
class Position:
	def __init__(self):
		pass

	def get_position_size(self, account_risk, trade_risk, amount, price):
		if account_risk < abs(trade_risk):
			trade_risk_coeff = -1*account_risk/trade_risk
		else:
			trade_risk_coeff = -1*trade_risk/account_risk
		risk_position_size = (amount*trade_risk_coeff)/price

		return risk_position_size