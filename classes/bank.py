import json

def get_data(db):
  return db.get_data()["record"]

class Bank:
  def __init__(self, bot):
    self.bot = bot
    self.db = self.bot.get_cog('DBCog').db

  def get_cash(self, id):
    id = str(id)
    data = get_data(self.db)
    if id in data["user_money"]:
      return data["user_money"][id]
    else:
      return 0
  
  async def change_cash(self, id, amt):
    id = str(id)
    amt = round(amt, 2)
    data = get_data(self.db)
    if id in data["user_money"]:
      data["user_money"][id] += amt
    else:
      data["user_money"][id] = amt
    await self.bot.get_cog("BankCog").update_roles(id)
    self.db.update_data(json.dumps(data))

  async def set_cash(self, id, amt):
    id = str(id)
    amt = round(amt, 2)
    data = get_data(self.db)
    data["user_money"][id] = amt
    await self.bot.get_cog("BankCog").update_roles(id)
    self.db.update_data(json.dumps(data))

  def get_shares(self, id, stock):
    id = str(id)
    portfolio = {}
    if id in get_data(self.db)["user_certificates"]:
      portfolio = get_data(self.db)["user_certificates"][id]
    else:
      return 0, 0
    shares = 0
    value = 0
    for cert in portfolio:
      if cert["name"] == stock:
        shares += cert["amount"]
        value += cert["value"]
    return shares, value

  def add_certificate(self, id, name, amount, value):
    cert = {"name": name, "amount": amount, "value": value}
    data = get_data(self.db)
    if not id in data["user_certificates"]:
      data["user_certificates"][id] = []
    data["user_certificates"][id].append(cert)
    self.db.update_data(json.dumps(data))

  def remove_shares(self, id, name):
    i = 0
    data = get_data(self.db)
    while i < len(data["user_certificates"][id]):
      if data["user_certificates"][id][i]["name"] == name:
        data["user_certificates"][id].pop(i)
        if i > 0:
          i -= 1
      else:
        i += 1
    self.db.update_data(json.dumps(data))