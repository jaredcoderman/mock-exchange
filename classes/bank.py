from replit import db

if not "user_money" in db.keys():
  db["user_money"] = {}
if not "user_stocks" in db.keys():
  db["user_stocks"] = {}
if not "user_certiciates" in db.keys():
  db["user_certificates"] = {}

class Bank:
  def get_cash(self, id):
    id = str(id)
    if id in db["user_money"]:
      return db["user_money"][id]
    else:
      return 0
  
  def set_cash(self, id, amt):
    id = str(id)
    amt = round(amt)
    print("user money:", db["user_money"])
    if id in db["user_money"]:
      db["user_money"][id] = amt
    else:
      db["user_money"][id] = amt
  
  def change_cash(self, id, amt):
    id = str(id)
    amt = round(amt, 2)
    if id in db["user_money"]:
      db["user_money"][id] += amt
    else:
      db["user_money"][id] = amt

  def get_shares(self, id, stock):
    id = str(id)
    portfolio = db["user_certificates"][id]
    shares = 0
    value = 0
    for cert in portfolio:
      if cert["name"] == stock:
        shares += cert["amount"]
        value += cert["value"]
    return shares, value

  def add_certificate(self, id, name, amount, value):
    cert = {"name": name, "amount": amount, "value": value}
    db["user_certificates"][id].append(cert)

  def remove_shares(self, id, name):
    i = 0
    while i < len(db["user_certificates"][id]):
      if db["user_certificates"][id][i]["name"] == name:
        db["user_certificates"][id].pop(i)
        if i > 0:
          i -= 1
      else:
        i += 1