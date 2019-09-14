#!/usr/bin/python3
from util import MSG

from discord import Client
import time
from connections.connect import Connect
from database.dbModels import *
now = float(time.time().__round__())
from os import environ

client = Client()


def distribute_rewards():
    MIN_POSQ_FOR_REWARDS = 5
    db = Connect.db()
    users = db.query(Users).filter(Users.bal >= MIN_POSQ_FOR_REWARDS).all()
    count = db.query(Users).filter(Users.bal >= MIN_POSQ_FOR_REWARDS).count()
    total_staking = db.query(func.sum(Users.bal))[0][0]
    total_earnings = db.query(Counter).first()
    #print(users, total_staking)

    for u in users:
        percent = u.bal / total_staking
        reward = float(total_earnings.amount) * percent
        u.stake_earned += reward
        u.bal += reward
        # print("user percent of reward : ", percent)
        newtx = Txs(tid=None, uid=u.uid, type="stk",
                    amount=float("{0:0.8f}".format(float(reward))), hash=None)
        db.add(newtx)

    amount = total_earnings.amount
    fee = total_earnings.fee
    total_earnings.timer = now
    total_earnings.amount = 0
    total_earnings.fee = 0


    db.commit()
    print("stake rewards distributed")

    @client.event
    async def on_ready():
        db = Connect.db()
        count = db.query(Users).filter(Users.bal > 1).count()
        msg = MSG("Today's Stakes", "\n Rewards :  **{0} POSQ** \n Fees : **{1} POSQ** \n Users : **{2}**".format(amount, fee, count))
        # uncomment for testnet
        await client.send_message(client.get_channel(environ.get("ANN_CHAN")), embed=msg)
        # uncoment for mainnet
        #await client.send_message(client.get_channel(environ.get('ANN_CHAN')), embed=msg)

        exit(0)

    client.run(environ.get("token"))



if __name__ == "__main__":
    distribute_rewards()

