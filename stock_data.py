import numpy as np
import random 

def get_stock_data(start_price):
  mu = 0.00001
  sigma = 0.01
  np.random.seed(random.randint(0, 1000))
  returns = np.random.normal(loc=mu, scale=sigma, size=100)
  data = start_price*(1+returns).cumprod()
  return data
  