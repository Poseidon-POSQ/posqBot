#!/usr/bin/python3
from sys import argv
import time
from database.dbModels import *
from connections.connect import Connect
#from util import logger
MIN_POSQ_FOR_REWARDS = 5

def check_tx(hash=None,stake=False,deposit=False,confirmed=False):

    stake_fee = 0.05

    if hash == None:
        exit(0)

    db = Connect.db()

    # check if tx exists in db
    check_for_tx = db.query(Txs).filter(Txs.hash==hash).first()
    check_for_stk = db.query(Stakes).filter(Txs.hash==hash).first()


    if check_for_tx != None and check_for_stk != None:
        if check_for_tx.success == 0:
            pass
        elif check_for_stk.success == 0:
            pass
        else:
            print("tx already exists in db")
            return False

    # get tx via rpc
    RPC = Connect.RPC()
    tx = RPC.gettransaction(hash)

    #check tx for deposit or stake
    confirmations = tx['confirmations']

    if confirmations <= 0:
        check_for_stk = db.query(Stakes).filter(Stakes.hash == hash).first()

        if check_for_stk:
            db.delete(check_for_stk)
            db.commit()

        db.close()
        return False

    deposit = check_deposit(tx, hash)
    stake = check_stake(tx)

    #confirmation params
    SLEEP_TIME = 60 * 5  # 5minutes
    stk_confs = 26
    dep_confs = 6


    if not deposit and not stake:
        print("invalid tx, closing script")
        return False

    if deposit and confirmations >= dep_confs:
        confirmed = True

    if deposit and not confirmed:
        confirming = True

        while confirming:

            print("Deposit : {0} | confirmations : {1} |  hash : {2}".format(deposit, confirmations, hash))
            time.sleep(SLEEP_TIME)
            RPC = Connect.RPC()
            tx = RPC.gettransaction(hash)
            confirmations = tx['confirmations']
            if confirmations < 0:
                confirmed = False
                confirming = False
            if confirmations >= dep_confs:
                confirmed = True
                confirming = False

    if deposit and confirmed:

        RPC = Connect.RPC()
        tx = RPC.gettransaction(hash)
        amount = float(tx['amount'])
        address = tx['details'][0]['address']
        db = Connect.db()
        did = RPC.getaccount(address)

        #add confirmed amount to maturing and check Txs.success
        user = db.query(Users).filter(Users.did==did).first()
        transaction = db.query(Txs).filter(Txs.hash==hash).first()


        if transaction == None:
            transaction = Txs(tid=None, uid=user.uid, hash=hash, type="dep", amount=amount, success=1)
            db.add(transaction)
            db.commit()

        elif transaction.success == 0:
            transaction.success = 1

        elif transaction.success == 1:
            print("Deposit was already successful")
            db.close()
            return False

        newTX = Maturing(mid=None, tid=transaction.tid, uid=user.uid, amount=amount, time=time.time().__round__(), success=1)

        db.add(newTX, user)
        db.commit()
        print("deposit success | uid : {0} | amount : {1} | hash : {2}".format(user.uid, amount, hash))
        db.close()
        return True

    if stake and confirmations >= stk_confs:
        confirmed = True

    if stake and not confirmed:
        db = Connect.db()
        RPC = Connect.RPC()

        tx = RPC.gettransaction(hash)
        amount = float(tx['amount']) + float(tx['fee'])

        check_for_stk = db.query(Stakes).filter(Stakes.hash == hash).first()

        if check_for_stk == None:
            user_count = db.query(Users).filter(Users.bal > MIN_POSQ_FOR_REWARDS).count()
            newTX = Stakes(sid=0, amount=float(amount), hash=hash, nUsers=user_count, success=0, found_utc=int(time.time()))
            db.add(newTX)
            db.commit()
            print("Stake Found : ",  hash)
        db.close()
        return False


    if stake and confirmed:

        db = Connect.db()
        RPC = Connect.RPC()

        tx = RPC.gettransaction(hash)
        amount = float(tx['amount']) + float(tx['fee'])

        check_for_stk = db.query(Stakes).filter(Stakes.hash==hash).first()

        if check_for_stk == None:
            user_count = db.query(Users).filter(Users.bal > MIN_POSQ_FOR_REWARDS).count()
            newTX = Stakes(sid=0, amount=float(amount), hash=hash, nUsers=user_count, success=1, found_utc=int(time.time()))
            db.add(newTX)

        elif check_for_stk.success == 0:
            check_for_stk.success = 1

        else:
            print("stk already successfull in db")
            db.close()
            return False

        stake_counter = db.query(Counter).first()


        devFee = float(amount) * stake_fee

        stake_counter.amount += amount
        stake_counter.fee += devFee

        db.commit()
        db.close()
        return True


def check_deposit(tx, hash):
    try:
        # check for deposit address
        address = tx['details'][0]['address']
        amount = float(tx['amount'])

        RPC = Connect.RPC()
        db = Connect.db()

        did = RPC.getaccount(address)
        user = db.query(Users).filter(Users.did==did).first()

        if user == None:
            return False

        check_for_tx = db.query(Txs).filter(Txs.hash==hash).first()

        if check_for_tx == None or check_for_tx.success == 0:
            return True

        elif check_for_tx.success == 1:
            print("deposit is already successful")
        db.close()
        return False

    except Exception as e:
        # no deposit address
        # print(e)
        return False

def check_stake(tx):
    try:
        # tx is a stake
        if tx['generated']:
            return True

    # tx was not a stake
    except Exception as e:
        #print(e)
        return False

if __name__ == "__main__":
    hash = argv[1]
    check_tx(hash)
