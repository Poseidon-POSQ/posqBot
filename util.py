import discord
from discord.utils import get
from discord.ext.commands import Bot
from discord.ext import commands
from connections.connect import *
from database.dbModels import *
import time
from discord import embeds
from datetime import datetime
from random import randint
import logging
from os import getcwd
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', filename=environ.get("LOG_PATH"))

MAX_BET = 100
GAME_INTERVAL = 10.0
NEW_USER_BAL = 2

def MSG(title, content, url="http://posq.io/posq_logo.png"):
    msg = discord.Embed(color=0x00b3b3)
    msg.set_thumbnail(url=url)
    msg.add_field(name=title, value=content, inline=False)
    return msg

def makeItRain(amount, nUsers, user, db):
    try:
        amount = float(amount)
        nUsers = int(nUsers)

        if nUsers > 50:
            nUsers = 50

    except Exception as e:
        #print(e)
        title = "Error"
        content = "Invalid rain, please specify a Correct amount amount \n" \
                  "To rain 5 posq split between 50 users do **!rain 5 50**"
        logger.info("invalid amount. Amount : {0}, nUsers : {1} | exception : {2}".format(amount, nUsers, e))
        return [title, content], []

    if not user.isAmount(amount):
        logger.info("invalid amount. Amount : {0}".format(amount))
        return ["Error", "Invalid amount, try again. \nExample, **!rain 5 50**"], []


    users = db.query(Users).all()
    rainAmount = float(fullNotation((amount / nUsers)))
    numberOfUsers = len(users)

    rainList = []
    for i in range(nUsers):

        rando = randint(1, int(numberOfUsers - 1))
        users[rando].bal += rainAmount
        rainList.append("<@" + str(users[rando].did) + ">")

    user.bal -= float(amount)
    db.commit()
    title = "Rain"
    content = "User : **<@{0}>** made it rain!!!\nTotal : **{1} POSQ**\nRained **{2}** POSQ on **{3}** users!".format(
        user.did, amount, rainAmount, nUsers)
    db.close()

    return [title, content],  rainList



def fullNotation(AMOUNT):
    return float("{0:0.08f}".format(AMOUNT))


def isAddress(ADDRESS):
    RPC = Connect.RPC()
    res = RPC.validateaddress(ADDRESS)
    if not res['isvalid']:
        return False
    return True

def checkLastBetTime(user, bet):
    now = int(time.time())
    if bet == "flip":
        if now-user.Lflip >= GAME_INTERVAL:
            return True
        else:
            return False
    elif bet == "roll":
        if now-user.Lroll >= GAME_INTERVAL:
            return True
        else:
            return False
    return False



def incrementCounter():
    db = Connect.db()
    count = db.query(Counter).first()
    count.count += 1
    db.commit()
    return "success"

class game:

    def getFlip():
        flip = randint(0, 1000)
        if flip >= 0 and flip <= 100:
            flip = 1
        elif flip >= 101 and flip <= 200:
            flip = 0
        elif flip >= 201 and flip <= 300:
            flip = 1
        elif flip >= 301 and flip <= 400:
            flip = 0
        elif flip >= 401 and flip <= 500:
            flip = 1
        elif flip >= 501 and flip <= 600:
            flip = 0
        elif flip >= 601 and flip <= 700:
            flip = 1
        elif flip >= 701 and flip <= 800:
            flip = 0
        elif flip >= 801 and flip <= 900:
            flip = 1
        elif flip >= 901 and flip <= 1000:
            flip = 0
        return flip

    def getRoll():
        roll = randint(0, 1200)
        if roll >= 0 and roll <= 100:
            roll = 1
        elif roll >= 101 and roll <= 200:
            roll = 2
        elif roll >= 201 and roll <= 300:
            roll = 3
        elif roll >= 301 and roll <= 400:
            roll = 4
        elif roll >= 401 and roll <= 500:
            roll = 5
        elif roll >= 501 and roll <= 600:
            roll = 6
        elif roll >= 601 and roll <= 700:
            roll = 1
        elif roll >= 701 and roll <= 800:
            roll = 2
        elif roll >= 801 and roll <= 900:
            roll = 3
        elif roll >= 901 and roll <= 1000:
            roll = 4
        elif roll >= 1001 and roll <= 1100:
            roll = 5
        elif roll >= 1101 and roll <= 1200:
            roll = 6
        return roll

def isBCT(id):
    try:
        int(id)
        id = str(id)
        if (len(id) > 0) & (len(id) < 8):
            return True
        else:
            return False
    except:
        return False

def checkRolls(bet, uid, choice):
    # prepare variables
    try:
        db = Connect.db()
        user = db.query(Users).filter(Users.uid == uid).first()
        bet = float(bet)
        bet = fullNotation(bet)
        bet = float(bet)
    except Exception as e:
        #print(e)
        # variables are invalid
        return "POSQ Dice", "**Invalid Bet**. \nEXAMPLE : **!roll 6 {}**".format(MAX_BET)

    if not user:
        return "Error", "You need to register. Use **!create**"

    if not checkLastBetTime(user, 'roll'):
        # not enough time
        return "POSQ Dice", "You must wait at least **{} seconds** until you can bet again.".format(GAME_INTERVAL)

    # is invalid amount
    if not user.isAmount(bet) and bet <= 10:
        # invalid bet
        title = "Invalid Bet."
        content = "Max Bet is **{0} POSQ**.\nCurrent Balance : **{1}**".format(MAX_BET, fullNotation(user.bal))
        return title, content

    # get random roll
    roll = game.getRoll()
    # check rolls
    if int(choice) == int(roll):
        winnings = bet * 4.95
        user.bal += winnings
        gambles = Gambles(gid=None, uid=user.uid, bet=bet, game="roll", outcome='W', paid=winnings)
        db.add(gambles)
        user.Lroll = time.time()
        db.commit()
        incrementCounter()
        return "POSQ Dice", "Rolled : **{0}** | Guessed : **{1}** \n**Congratulations! You Win!!!** " \
                  "\nWagered : **{2} POSQ** | Winnings : **{3} POSQ**".format(
            roll, choice, fullNotation(bet), fullNotation(winnings+bet))

    user.bal -= bet
    gambles = Gambles(gid=None, uid=user.uid, bet=bet, game="roll", outcome='L', paid=(bet * -1))
    db.add(gambles)
    user.Lroll = time.time()
    db.commit()
    incrementCounter()
    return "POSQ Dice", "Rolled : **{0}** | Guessed : **{1}** \n**Sorry, you lost!**\nWagered : **{2} POSQ**" \
              "".format(roll,choice,fullNotation(bet))




def checkFlips(bet, user, choice, db):
    flip = game.getFlip()
    if not user:
        return "Error", "You must first create an account with !create"

    if not checkLastBetTime(user, "flip"):
        return "CoinFlip", "You must wait at least **30 seconds** until you can bet again"

    if not user.isAmount(bet):
        return "Invalid Bet.", "You do not have enough posq \nCurrent Balance : **{}**".format(fullNotation(user.bal))

    if not bet <= MAX_BET:
        return "Invalid Bet.", "Max bet is {} POSQ".format(MAX_BET)

    if flip == 0:
        outcome = "Tails"
    elif flip == 1:
        outcome = "Heads"

    # check flip outcomes
    if flip == choice:
            winnings = bet * 0.95
            user.bal += winnings
            gambles = Gambles(gid=None, uid=user.uid, bet=bet, game="flip", outcome='W', paid=winnings)
            user.Lflip = time.time()
            db.add(gambles)
            db.commit()
            incrementCounter()
            return "CoinFlip", "{0}!\n**Congratulations, you win!**\nBet : **{1} POSQ** | Winnings : **{2} POSQ**" \
                      "".format(outcome,fullNotation(bet), fullNotation((winnings+bet)))

    elif flip != choice:
            user.bal = user.bal - bet
            gambles = Gambles(gid=None, uid=user.uid, bet=bet, game="flip", outcome='L',
                              paid=(bet * -1))
            user.Lflip = time.time()
            db.add(gambles)
            db.commit()
            incrementCounter()
            return "CoinFlip", "{0}\n**Sorry,you lost.**\nWagered : **{1} POSQ**".format(outcome,bet)

def getUserBal(db, user, usr, uname, did):
    if user == None:
        user = Users(uname=str(uname), uid=0, did=did, bid=0, stake_earned=0, addr=None, bal=NEW_USER_BAL, Lflip=0, Lroll=0)
        db.add(user)
        db.commit()
        user = db.query(Users).filter_by(did=did).first()
        logger.info("bal, user created.  | User : {0}".format(user.did))
        title = "Balance Query"
        content = "User : <@{0}>\nBalance : **{1} POSQ**".format(user.did, fullNotation(user.bal))
        url = "https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png".format(uname)
        return title, content, url

    elif usr != None:

        user_did = str(usr).strip("<@").strip(">")
        user = db.query(Users).filter_by(did=user_did).first()
        if user == None:

            user = Users(uname=None, uid=0, did=user_did, bid=0, stake_earned=0, addr=None, bal=NEW_USER_BAL, Lflip=0, Lroll=0)
            db.add(user)
            db.commit()
            user = db.query(Users).filter_by(did=user_did).first()
            logger.info("bal, user created.  | User : {0}".format(user))

            title = "Balance Query"
            content = "User : <@!{0}> \nBalance : **{1}**\n Maturing : **{2}**".format(user.did, fullNotation(user.bal),
                                                                                       user.maturing)
            url = None
            return title, content, url
        else:
            title = "Balance Query"
            content = "User : <@!{0}> \nBalance : **{1}**\n Maturing : **{2}**".format(user.did, fullNotation(user.bal),
                                                                                       user.maturing)
            url = None
            return title, content, url
    else:
        title = "Balance Query"
        content = "User : <@!{0}> \nBalance : **{1}**\n Maturing : **{2}**".format(user.did, fullNotation(user.bal),
                                                                                   user.maturing)
        url = "https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png".format(uname)
        return title, content, url



