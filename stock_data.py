import numpy as np
import random

def get_stock_data(start_price, initial_price):
  mult = None
  rand = random.randrange(0, 2) 
  if rand == 0 or start_price > initial_price * 2:
    mult = -1
  elif rand == 1 or start_price < initial_price // 2:
    mult = 1
  mu = .0005 * mult
  sigma = 0.001
  np.random.seed(random.randrange(0, 1000))
  returns = np.random.normal(loc=mu, scale=sigma, size=100)
  prices = start_price*(1+returns).cumprod()
  return prices