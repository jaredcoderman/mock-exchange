import json

from classes.database import Database

db = Database()

def get_data():
  global db
  return db.get_data()["record"]

def write_to_db(data):
  global db
  db.update_data(json.dumps(data))

class Bank:
  def get_cash(self, id):
    id = str(id)
    data = get_data()
    if id in data["user_money"]:
      return data["user_money"][id]
    else:
      return 0
  
  def change_cash(self, id, amt):
    id = str(id)
    amt = round(amt, 2)
    data = get_data()
    print(data)
    if id in data["user_money"]:
      data["user_money"][id] += amt
    else:
      data["user_money"][id] = amt
    write_to_db(data)

  def get_shares(self, id, stock):
    id = str(id)
    portfolio = get_data()["user_certificates"][id]
    shares = 0
    value = 0
    for cert in portfolio:
      if cert["name"] == stock:
        shares += cert["amount"]
        value += cert["value"]
    return shares, value

  def add_certificate(self, id, name, amount, value):
    cert = {"name": name, "amount": amount, "value": value}
    data = get_data()
    data["user_certificates"][id].append(cert)
    write_to_db(data)

  def remove_shares(self, id, name):
    i = 0
    data = get_data()
    while i < len(data["user_certificates"][id]):
      if data["user_certificates"][id][i]["name"] == name:
        data["user_certificates"][id].pop(i)
        if i > 0:
          i -= 1
      else:
        i += 1
    write_to_db(data)