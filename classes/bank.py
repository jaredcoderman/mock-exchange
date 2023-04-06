import json

def get_db(guild_id):
  data = open(f"./data/{guild_id}.json", "r").read()
  db = json.loads(data)
  return db

def write_to_db(guild_id, db):
  with open(f"./data/{guild_id}.json", "w") as f:
    f.write(json.dumps(db))

class Bank:
  def get_cash(self, guild_id, id):
    id = str(id)
    db = get_db(guild_id)
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
  
  def change_cash(self, guild_id, id, amt):
    id = str(id)
    amt = round(amt, 2)
    db = get_db(guild_id)
    if id in db["user_money"]:
      db["user_money"][id] += amt
    else:
      db["user_money"][id] = amt
    write_to_db(guild_id, db)

  def get_shares(self, guild_id, id, stock):
    id = str(id)
    portfolio = get_db(guild_id)["user_certificates"][id]
    shares = 0
    value = 0
    for cert in portfolio:
      if cert["name"] == stock:
        shares += cert["amount"]
        value += cert["value"]
    return shares, value

  def add_certificate(self, guild_id, id, name, amount, value):
    cert = {"name": name, "amount": amount, "value": value}
    db = get_db(guild_id)
    db["user_certificates"][id].append(cert)
    write_to_db(guild_id, db)

  def remove_shares(self, guild_id, id, name):
    i = 0
    db = get_db(guild_id)
    while i < len(db["user_certificates"][id]):
      if db["user_certificates"][id][i]["name"] == name:
        db["user_certificates"][id].pop(i)
        if i > 0:
          i -= 1
      else:
        i += 1
    write_to_db(guild_id, db)