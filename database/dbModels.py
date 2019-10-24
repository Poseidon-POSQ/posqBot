#!/usr/bin/python3

from sqlalchemy import *
from sqlalchemy.orm import relationship, join
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import time

base = declarative_base()

class Users(base):

    """
    Base for all users.
    maturing returns sum of coins waiting for maturity
    winnings returns sum of winnings from games
    Lflip and Lroll track the last time a game was successful
    uid = user id
    bid = bitcointalk id
    did = discord id
    addr = posq address
    set is_banned=1 to disable users access to bot
    """
    __tablename__ = "users"
    uid = Column(BIGINT, primary_key=True)
    did = Column(VARCHAR)
    bid = Column(INT, default=0)
    uname = Column(VARCHAR)
    addr = Column(VARCHAR)
    bal = Column(FLOAT)
    stake_earned = Column(FLOAT)
    Lflip = Column(BIGINT, default=0)
    Lroll = Column(BIGINT, default=0)
    is_banned = Column(BOOLEAN, default=0)
    #txs = relationship('Txs', backref='owner')
    gambles = relationship('Gambles', backref='owner')
    mature = relationship('Maturing', backref='owner')

    @property
    def maturing(self):
        sum = 0
        for m in [m.amount for m in self.mature]:
            sum += m
        return sum

    @property
    def winnings(self):
        sum = 0
        for s in [g.paid for g in self.gambles]:
            sum += s
        return sum

    def isAmount(self, amount):
        amount = float(amount)
        newBal = self.bal - amount
        if newBal >= 0 and amount > 0:
            return True
        return False



    def __repr__(self):
        return "<users(uid=%s, did=%s, bid=%s, uname=%s addr=%s, bal=%s, Lflip=%s, Lroll=%s, maturing=%s)>" \
               % (self.uid, self.did, self.bid, self.uname, self.addr, self.bal, self.Lflip, self.Lroll, self.maturing)

class Txs(base):
    """
    Txs table tracks all transactions such as deposits, tips, donations, stake rewards and games
    tid = transaction id
    uid = user id
    type = type of trasnaction
    amount = tx amount
    hash = tx hash
    success = 0 for incomplete and 1 for successful
    """
    __tablename__ = "txs"
    tid = Column(BIGINT, primary_key=True)
    uid = Column(BIGINT, ForeignKey('users.uid'))
    type = Column(VARCHAR)
    amount = Column(FLOAT, default=0)
    hash = Column(VARCHAR, default=None)
    success = Column(BOOLEAN, default=0)

    def __repr__(self):
        return "<txs(uid=%s, tid=%s, amount=%s, type=%s, hash=%s)>" % (self.uid, self.tid, self.amount, self.type, self.hash)

class Gambles(base):
    """
    Gambles table is to track all game and bet action
    gid = gamble id -- Primary Key
    uid = user id -- Foreign Key
    game = type of game Ex : flip or roll
    outcome = tracks win or loss Ex : W or L
    bet = users bet
    paid = amount paid from winnings [set to negative for loss]
    """
    __tablename__ = "gambles"
    gid = Column(BIGINT, primary_key=True)
    uid = Column(BIGINT, ForeignKey('users.uid'))
    game = Column(VARCHAR)
    outcome = Column(VARCHAR)
    bet = Column(FLOAT, default=0)
    paid = Column(FLOAT, default=0)

    def __repr__(self):
        return "<gambles(uid=%s, gid=%s, bet=%s, paid=%s game=%s, outcome=%s)>" % (self.uid, self.gid, self.bet, self.paid, self.game, self.outcome)

class Counter(base):

    """
    count tracks total number of games played
    timer is not currently used but can be used to track an event
    amount tracks daily stakes earned
    fee tracks daily fees from staking
    """
    __tablename__ = "counter"
    count = Column(BIGINT, default=0, primary_key=True)
    timer = Column(BIGINT, default=0)
    amount = Column(FLOAT, default=0)
    fee = Column(FLOAT, default=0)

    def __repr__(self):
        return "<counter(count=%s, timer=%s, amount=%s, fee=%s)>" % (self.count, self.timer, self.amount, self.fee)

class Maturing(base):

    """
    Maturing table keeps track of new deposits
    set crontab to run checkMaturity.py hourly

    mid = maturing id -- Primary Key
    tid = tx id -- Foreign Key to tx
    uid = user id -- Foreign Key to user

    success defaults to 0 and can be deprecated
    as the script removes based on time and not success


    """
    __tablename__ = "maturing"
    mid = Column(BIGINT, primary_key=True)
    tid = Column(BIGINT, ForeignKey('txs.tid'))
    uid = Column(BIGINT, ForeignKey('users.uid'))
    amount = Column(REAL, default=0)
    time = Column(BIGINT, default=0)
    success = Column(BOOLEAN, default=0)
    user = relationship('Users', backref='owner')

class Stakes(base):
    """
    Tracks all stake blocks found by the bot
    sid = stake id
    hash = tx hash
    amount = stake amount
    nUsers can be deprecated now since
    make daily cronjob of dailyStakeAnnounce.py
    which distributes rewards and sends nUsers as a message in discord
    """
    __tablename__ = "stakes"
    sid = Column(BIGINT, primary_key=True)
    hash = Column(VARCHAR, default=None)
    amount = Column(FLOAT, default=0)
    nUsers = Column(BIGINT, default=0)
    success = Column(BOOLEAN, default=0)
    found_utc = Column(BIGINT, default=0)

    def __repr__(self):
        return "<stakes(sid=%s, hash=%s, amount=%s, nUsers=%s)>" % (self.sid, self.hash, self.amount, self.nUsers)


class Leaders(base):
    """
    Leaderboard class describes  a database view which keeps the sum amount of users games
    uid = user id
    paid = winnings sum
    """
    __tablename__ = "leaderBoard"
    uid = Column(BIGINT, primary_key=True)
    paid = Column(FLOAT)

    def __repr__(self):
        return "<stakes(uid=%s, paid=%s)>" % (self.uid, self.paid)


if __name__ == "__main__":

    from connections.connect import Connect
    #help(Users)
    #db = Connect.db()
    #users = db.query(Users)
    #users.filter(Users.uid==1).first().bal
    #user = db.query(func.sum(Users.bal))[0][0]
    #count = db.query(Users).filter(Users.bal>1).count()
