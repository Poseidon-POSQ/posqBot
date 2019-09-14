#!/usr/bin/python3
import time
from database.dbModels import *
from connections.connect import Connect

def check_maturity():

    now = float(time.time().__round__())
    mature_time = now - (60 * 60 * 24) # 24 hours
    db = Connect.db()

    txs = db.query(Maturing).filter(Maturing.time <= mature_time).all()

    for t in txs:
        t.user.bal += t.amount
        db.delete(t)

    db.commit()
    #print("checked maturity")

if __name__ == "__main__":
    check_maturity()