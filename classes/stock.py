from stock_data import get_stock_data

class Stock:
  def __init__(self, name, start_price, initial_price):
    self.name = name
    self.initial_price = initial_price
    self.data = get_stock_data(start_price, initial_price)
    self.previous_prices = []
    self.trending = None
    self.time_spot = 0
    self.last_price = 0
    self.max_prices = 100

  def reset_stock_data(self, price):
    self.data = get_stock_data(price, self.initial_price)
    self.time_spot = 0
    price = self.data[self.time_spot]
    return price

  def add_to_previous_prices(self, price):
    if len(self.previous_prices) >= self.max_prices:
      self.previous_prices.pop(0)
      self.previous_prices.append(price)
    else:
      self.previous_prices.append(price)

  def _update_trending(self):
    if len(self.previous_prices) < 76:
      return
    if self.get_previous_prices()[75] < self.get_previous_prices()[-1]:
      self.trending = "up"
    else:
      self.trending = "down"
    
  def get_next_price(self):
    self.time_spot += 1
    if self.time_spot >= len(self.data):
      price = self.reset_stock_data(self.last_price)
    else:
      price = self.data[self.time_spot]
      self.last_price = price
      self.add_to_previous_prices(self.last_price)
    # Update trending
    self._update_trending()
    return price

  def get_price(self, rounded):
    if rounded:
      return round(self.last_price, 2)
    else:
      return self.last_price

  def get_previous_prices(self):
    return self.previous_prices