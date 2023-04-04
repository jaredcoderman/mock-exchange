from stock_data import get_stock_data

class Stock:
  def __init__(self, name, start_price):
    self.name = name
    self.data = get_stock_data(start_price)
    self.previous_prices = []
    self.time_spot = 0
    self.last_price = 0
    self.max_prices = 250

  def reset_stock_data(self, price):
    self.data = get_stock_data(price)
    self.time_spot = 0
    price = self.data[self.time_spot]
    return price

  def add_to_previous_prices(self, price):
    if len(self.previous_prices) >= self.max_prices:
      self.previous_prices.pop(0)
      self.previous_prices.append(price)
    else:
      self.previous_prices.append(price)
    
  def get_next_price(self):
    self.time_spot += 1
    if self.time_spot >= len(self.data):
      price = self.reset_stock_data(self.last_price)
    else:
      price = self.data[self.time_spot]
      self.last_price = price
      self.add_to_previous_prices(self.last_price)
    return price

  def get_price(self):
    return self.last_price

  def get_previous_prices(self):
    return self.previous_prices