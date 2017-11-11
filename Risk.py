
class Risk:
	def __init__(self):
		self.pl_risk = -0.2
		self.account_risk=0.05

	def get_pl(self, entry_price, current_price, type):
		if type =='long':
			return current_price/entry_price -1.004
		else: 
			return entry_price/current_price -1.004