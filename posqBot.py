import re
from util import *
import discord
from discord.utils import get
from discord.ext.commands import Bot
from discord.ext import commands
from database.dbModels import *
from connections.connect import *
import datetime
from random import randint
from checkTx import *
bot_prefix = "!"
client = commands.Bot(command_prefix=bot_prefix)
Bot.remove_command(client, "help")




@client.command(pass_context=True)
async def leaders():
    db = Connect.db()
    leaders = db.query(Leaders).order_by(Leaders.paid.desc()).limit(5).all()
    content = "**User | Winnings**\n"
    for l in leaders:
        did = db.query(Users.did).filter(Users.uid == l.uid).first()[0]
        did = "<@" + str(did) + ">"
        content = content + "{0} | **{1} POSQ**\n".format(did, fullNotation(l.paid))
    msg = MSG("Leader Boards", content)
    await client.say(embed=msg)


@client.command(pass_context=True)
async def game(ctx, option=None):
    uname = ctx.message.author
    did = ctx.message.author.id
    db = Connect.db()

    if option == None:
        title = "POSQ Games"
        content = "**!game total** shows total earned from playing\n" \
                  "**!game tx** shows recent attempts"
        msg = MSG(title, content)
        await client.say(embed=msg)

    elif option == "total":
        user = db.query(Users).filter_by(did=did).first()
        title = "POSQ Games"
        content = "\nRewards total : **{0} POSQ**".format(fullNotation(user.winnings))
        url = "https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png".format(uname)
        msg = MSG(title, content, url)
        await client.say(embed=msg)

    elif option == "tx":
        user = db.query(Users).filter_by(did=did).first()
        transactions = db.query(Gambles).order_by(Gambles.gid.desc())\
            .filter(Gambles.uid == user.uid).limit(5).all()
        txs = ""
        for i in transactions:
            txs = txs + str("\nGame ID : **{0}** | Type : **{1}** |  Outcome : **{2}**"
                            "\nBet : **{3} POSQ** | Paid : **{4} POSQ**\n").format(
                i.gid, i.game, i.outcome, fullNotation(i.bet), fullNotation(i.paid))
        title = "POSQ Games"
        content = "{0}".format(txs)
        url = "https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png".format(uname)
        msg = MSG(title, content, url)
        await client.say(embed=msg)


@client.command(pass_context=True)
async def stake(ctx, option=None):
    uname = ctx.message.author
    did = ctx.message.author.id
    db = Connect.db()
    title = "POSQ Stake Bot"

    if option == None:
        content = "**!stake total** shows your total earned from staking.\n" \
                  "**!stake tx** shows recent stake rewards.\n" \
                  "**!stake current** shows current total rewards earned by the bot today."
        msg = MSG(title, content)
        await client.say(embed=msg)

    elif option == "total":
        user = db.query(Users).filter_by(did=did).first()
        content = "\nRewards total : **{0} POSQ**".format(fullNotation(user.stake_earned))
        url = "https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png".format(uname)
        msg = MSG(title, content, url)
        await client.say(embed=msg)

    elif option == "current":
        #totals = db.query(Counter).first()
        now = int(time.time())
        one_day = now - 60*60*24
        stakes = db.query(Stakes).filter(Stakes.found_utc>=one_day).filter_by(success=0)
        count = stakes.count()
        Stake_Reward=stakes.first().amount

        total_sum = count*Stake_Reward
        fee = total_sum * 0.05
        rewards = total_sum - fee

        content = "\nFound : **{0} Blocks**\nRewards : **{1} POSQ**\nFees : **{2} POSQ**" \
                  "".format(count, fullNotation(rewards), fullNotation(fee))
        msg = MSG("Last 24 Hours", content)
        await client.say(embed=msg)

    elif option == "tx":
        user = db.query(Users).filter_by(did=did).first()
        transactions = db.query(Txs).order_by(Txs.tid.desc())\
            .filter(Txs.uid == user.uid).filter(Txs.type == "stk")\
            .limit(10).all()
        txs = ""
        for i in transactions:
            txs = txs + str("TXID : **{0}** \t|\t Reward : **{1} POSQ**\n").format(
                                                            i.tid, fullNotation(i.amount))
        content = "{0}".format(txs)
        url = "https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png".format(uname)
        msg = MSG(title, content, url)
        await client.say(embed=msg)

@client.command(pass_context=True)
async def admin(ctx, option=None, parm=None, parm2=None):
    uname = ctx.message.author
    did = ctx.message.author.id
    db = Connect.db()
    if str(did) == "400325881698058241" or str(did) == "342131766963994634" or str(did) == "335983814490718208":
        if option == None:
            title = "Admin Panel"
            content = "**!admin getbals** returns total users balances\n" \
                      "**!admin deluser DiscordID** delete user by did\n" \
                      "**!admin updatebal DiscordID amount** change user balance"
            msg = MSG(title, content)
            await client.say(embed=msg)
        elif option == "getbals":
            db = Connect.db()
            users = db.query(Users).all()
            total = 0
            for i in users:
                total += i.bal
            msg = MSG("Total Users Hodlings", "Balance : **{0} POSQ**".format(total))
            await client.say(embed=msg)

        elif option == "deluser":
            if parm == None:
                title = "Admin Panel"
                content = "Must provide a discord id"
                msg = MSG(title, content)
                await client.say(embed=msg)
            else:
                user = db.query(Users).filter_by(did=parm).first()
                if not user:
                    msg = MSG("Admin", "ID : **{}** Doesn't exist.".format(parm))
                    await client.say(embed=msg)
                    logger.info("delUser admin. did doesnt exist : {0}".format(parm))

                if user:
                    #uncomment to remote all user entries
                    #txs = db.query(Txs).filter(Txs.uid==user.uid).all()
                    #maturing = db.query(Maturing).filter(Maturing.uid==user.uid).all()
                    #staking = db.query(Staking).filter(Staking.uid==user.uid).all()
                    #db.delete(user, txs, maturingm staking)

                    db.delete(user)
                    db.commit()
                    msg = MSG("Admin", "Deleted User : {}".format(parm))
                    await client.say(embed=msg)
                    logger.info("Admin deleted user. did : {0}".format(parm))

        elif option == "updatebal":
            if parm == None:
                title = "Admin Panel"
                content = "Must provide a discord id"
                msg = MSG(title, content)
                await client.say(embed=msg)

            elif parm2 == None:

                title = "Admin Panel"
                content = "Must provide a new balance"
                msg = MSG(title, content)
                await client.say(embed=msg)

            else:
                user = db.query(Users).filter_by(did=parm).first()
                user.bal = parm2
                db.commit()
                title = "Admin Panel"
                content = "User balance has been updated"
                msg = MSG(title, content)
                await client.say(embed=msg)

@client.command(pass_context=True)
async def rain(ctx, amount=None, nUsers=None):
    uname = ctx.message.author
    did = ctx.message.author.id
    db = Connect.db()
    user = db.query(Users).filter_by(did=did).first()
    if (nUsers == None or amount == None):
        title = "Error"
        content = "Invalid rain, please specify an amount. \n" \
                  "To rain 5 posq split between 50 users do **!rain 5 50**"
        msg = MSG(title, content)
        await client.say(embed=msg)
        logger.info("invalid amount. Amount : {0}, nUsers : {1}".format(amount, nUsers))

    elif not user:
        msg = MSG("Error", "You must create an account before you can make it rain.\nTry **!create**")
        await client.say(embed=msg)

    else:
        msg = makeItRain(amount, nUsers, user, db)
        url = "https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png".format(uname)
        if msg[1] != []:
            send = MSG(msg[0][0], msg[0][1], url)
            await client.say(embed=send)
            # splits rain message into strings of 2,000 len
            for chunk in [msg[1][i:i + 2000] for i in range(0, len(msg[1]), 2000)]:
                c = re.sub("[[',]", "", str(chunk).strip(']'))
                await client.say(c)
            logger.info("Successful Rain. Amount : {0}".format(amount))
        else:
            msg = MSG(msg[0][0], msg[0][1])
            await client.say(embed=msg)

@client.command(pass_context=True)
async def donate(ctx, amount=None):
    uname = ctx.message.author
    did = ctx.message.author.id
    db = Connect.db()
    user = db.query(Users).filter_by(did=did).first()

    if user == None:
        msg = MSG("Error", "You have not registered yet. Use !create")
        logger.info("donate | user : {0} | amount : {1} | User doesnt exist".format(did, amount))
        return False

    elif amount == None:
        msg = MSG("Error", "Invalid amount, try again.")
        await client.say(embed=msg)
        logger.info("donate | user : {0} | amount : {1} | Invalid amount".format(did, amount))
        return False

    try:
        amount = float(amount)
        if not user.isAmount(amount):
            msg = MSG("Donate", "Invalid Amount")
            await client.say(embed=msg)
            return False
        if amount <= 0:
            msg = MSG("Donate", "Invalid Amount")
            await client.say(embed=msg)
            return False

    except:
        msg=MSG("Donate", "Invalid Amount")
        await client.say(embed=msg)
        return False

    user.bal -= amount

    newTx = Txs(tid=None, uid=user.uid, type="don", amount=amount, hash=None, success=1)
    db.add(newTx)

    db.commit()
    msg = MSG("Donated",
              "Thank you for your contribution of **{0} POSQ!**" \
              "\n**Your support is appreciated.**".format(fullNotation(amount)),
              "https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png".format(uname))
    logger.info("donation made amount : {0}".format(amount))
    await client.say(embed=msg)



@client.command(pass_context=True)
async def deposit(ctx, option=None):

    uname = ctx.message.author
    did = ctx.message.author.id

    db = Connect.db()
    RPC = Connect.RPC()

    user = db.query(Users).filter_by(did=did).first()

    if user == None:
        msg = MSG("Deposit", "You must first register with the bot by using !create")
        await client.send_message(uname, embed=msg)

    elif option == None:
        #check if they have a deposit address yet
        dep_address = RPC.getaccountaddress(str(did))
        msg = MSG("Deposit", '\nDeposits are automatic' \
                  '\n\nYou can check your recent deposits with **!deposit tx**' \
                  #'\n\nIf you do not see your deposit in your recent transactions after 30 minutes try **!deposit YOUR_TX_HASH**' \
                  #'\n**EXAMPLE : !deposit 7a9d46a548c929ce13eb7b1c6ea326538ced5125a696ffe829dc90afc8835014**' \           
                  '\n\nIf there are any issues, then please contact an admin and provide your transaction hash.' \
                  '\n\nYour deposit address is below :point_down:')

        await client.send_message(uname, embed=msg)
        await client.send_message(uname, dep_address)

    elif option == "tx":
        transactions = db.query(Txs).order_by(Txs.tid.desc()) \
            .filter(Txs.uid == user.uid).filter(Txs.type=="dep")\
            .limit(5).all()
        txs = ""
        for i in transactions:
            txs = txs + "\nTXID : **{0}** | Amount : **{1} POSQ ** | hash : **{2}**\n" \
                        "".format(i.tid, fullNotation(i.amount), i.hash)
        content = "{0}".format(txs)
        url = "https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png".format(uname)
        msg = MSG("Recent Deposits", content, url)
        await client.send_message(uname, embed=msg)

    else:

        try:
            if check_tx(option):
                msg = MSG("Deposit", '\nSuccessful Deposit.')
            else:
                msg = MSG("Deposit", "\nCheck your recent Deposits.")
            await client.send_message(uname, embed=msg)

        except Exception as e:
            #print(e)
            msg = MSG("Deposit", "\nInvalid TX \n If the problem persists, contact an admin.")
            await client.send_message(uname, embed=msg)







@client.command(pass_context=True)
async def roll(ctx, choice=None, bet=None):
    uname = ctx.message.author
    did = ctx.message.author.id
    db = Connect.db()
    try:
        if int(choice) < 0 or int(choice) > 6:
            choice = None
    except:
        choice = None

    #check for roll and bet
    if choice == None or bet == None:
        title = "POSQ Dice"
        content = "Invalid command.\nMax Bet is **10 POSQ** \nExample : **!roll 6 10**"
        logger.info("Invalid roll. | choice : {0} | bet : {1} | user : {2}".format(choice, bet, did))
        msg = MSG(title, content)
        await client.say(embed=msg)
        #return False

    else:
        user = db.query(Users).filter_by(did=did).first()
        outcome = checkRolls(bet, user.uid, choice)
        url = "https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png".format(uname)
        msg = MSG(outcome[0], outcome[1], url)
        await client.say(embed=msg)
        logger.info("Successful roll. | choice : {0} | bet : {1} | user : {2}".format(choice, bet, did))



@client.command(pass_context=True)
async def create(ctx):

    uname = ctx.message.author
    did = ctx.message.author.id
    db = Connect.db()

    user = db.query(Users).filter_by(did=did).first()

    if user == None and user == None:

        user = Users(uname=str(uname), uid=0, did=did, bid=0,
                     stake_earned=0, addr=None, bal=NEW_USER_BAL, Lflip=0, Lroll=0)
        db.add(user)
        db.commit()
        user = db.query(Users).filter_by(did=did).first()
        title = "Account Creation"
        content = "<@{0}> is now registered. \nBalance : **{1}**".format(user.did, fullNotation(user.bal))
        url = "https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png".format(uname)
        msg = MSG(title, content, url)
        await client.say(embed=msg)
        logger.info("User created. {0}".format(user.did))

    else:
        title = "Error"
        content = "<@{}>\nis already Registered".format(user.did)
        url = "https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png".format(uname)
        msg = MSG(title, content, url)
        await client.say(embed=msg)
        logger.info("!create, user is already registered {0}".format(did))

@client.command(pass_context=True)
async def me(ctx):
    uname = ctx.message.author
    did = ctx.message.author.id
    db = Connect.db()

    user = db.query(Users).filter_by(did=did).first()
    if user == None:
        title = "Error"
        content = "You have not registered yet. Use !create"
        msg = MSG(title, content)
        await client.say(embed=msg)
        logger.info("me. profile doesnt exist | did :{0}".format(did))
    else:
        title = "User Profile"
        content = "User : **<@{0}>\n**UID: **{1}**\n BCT : **{2}**\nBal : **{3}** \n Maturing : **{4}**" \
                  "".format(user.did, user.uid, user.bid, fullNotation(user.bal), user.maturing)
        url = "https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png".format(uname)
        msg = MSG(title, content, url)
        await client.say(embed=msg)
        logger.info("checked profile | did :{0}".format(user.did))


@client.command(pass_context=True)
async def flip(ctx, choice=None, bet=None):
    uname = ctx.message.author
    did = ctx.message.author.id
    db = Connect.db()
    user = db.query(Users).filter_by(did=did).first()
    # invalid flip
    if choice == None or bet == None:
        msg = MSG("Error", "**Invalid Bet**\nMax Bet is {0} POSQ. Example : !flip heads 10".format(MAX_BET))
        await client.say(embed=msg)
    else:

        try:
            bet = float(bet)
            if bet > MAX_BET and bet < 0:
                bet = "invalid"

            if choice == "heads":
                choice = 1
            elif choice == "tails":
                choice = 0
            else:
                choice = "invalid"

        except Exception as e:
            print(e)
            bet = "invalid"

    if choice == "invalid" or bet == "invalid":
        msg = MSG("Error", "**Invalid Bet**\nMax Bet is {0} POSQ. Example : !flip heads 10".format(MAX_BET))
        await client.say(embed=msg)
    else:
        url = "https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png".format(uname)
        outcome = checkFlips(bet, user, choice, db)
        msg = MSG(outcome[0], outcome[1], url)
        await client.say(embed=msg)
        logger.info("successful flip. choice : {0} | bet : {1}".format(choice, bet))

@client.command(pass_context=True)
async def bal(ctx, usr=None):
    did = ctx.message.author.id
    uname = ctx.message.author
    db = Connect.db()
    user = db.query(Users).filter_by(did=did).first()

    res = getUserBal(db, user, usr, uname, did)

    if res[2] == None:
        msg = MSG(res[0], res[1])
    else:
        msg = MSG(res[0], res[1], res[2])

    await client.say(embed=msg)


@client.command(pass_context=True)
async def withd(ctx, addr=None, amount=None):
    """
    TODO: Add option to display recent withdraw txs
    """
    uname = ctx.message.author
    did = ctx.message.author.id
    if not addr or not amount:
        msg = MSG("Error", "Invalid Command, try !withd ADDRESS AMOUNT")
        await client.say(embed=msg)
        logger.info("Invalid withdraw. | addr : {0} | amount : {1}".format(addr, amount))

    db = Connect.db()
    RPC = Connect.RPC()
    user = db.query(Users).filter_by(did=did).first()

    if not user:
        msg = MSG("Error", "You must first create an account with  **!create**")
        await client.say(embed=msg)

    elif not user.isAmount(float(amount)):
        msg = MSG("Error", "Invalid Amount, try again.")
        await client.say(embed=msg)
        logger.info("Invalid amount for withdraw. | addr : {0} | amount : {1}".format(addr, amount))

    elif not isAddress(addr):
        msg = MSG("Error", "Invalid Address, try again.")
        await client.say(embed=msg)
        logger.info("Invalid address for withdraw. | addr : {0} | amount : {1}".format(addr, amount))

    elif isAddress(addr) and user.isAmount(float(amount)):
        unlockWallet = RPC.walletpassphrase(environ.get("WALLETPASS"), 9999999)
        hash = RPC.sendtoaddress(addr, float(amount))

        user.bal -= float(amount)
        newTX = Txs(uid=user.uid, tid=None, hash=hash, type="wit", amount=amount, success=1)
        db.add(newTX)
        db.commit()
        link = "[{0}](http://posq.space:8080/tx/{0})".format(hash)
        msg = MSG("User Withdraw", "User : <@{0}>\nBalance : **{1}**\nSent : **{2} POSQ**"
                                   "\n hash : **{3}**".format(did, fullNotation(user.bal), amount, link),
                  "https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png".format(uname))

        await client.say(embed=msg)
        logger.info("Successful withdraw. | addr : {0} | amount : {1} | hash : {2}".format(addr, amount, hash))


@client.command(pass_context=True)
async def tip(ctx, user=None, amount=None):
    db = Connect.db()
    uname = ctx.message.author
    did = ctx.message.author.id
    SENDER = db.query(Users).filter_by(did=did).first()


    # check for valid tip
    if not user or not amount:
        msg = MSG("Error", "Invalid Command, try !tip @username amount")
        await client.say(embed=msg)
        logger.info("Invalid tip. user : {0}  | ammount : {1}".format(user, amount))

    else:
        did = str(user).strip("<@").strip(">")
        RECEIVER = db.query(Users).filter_by(did=did).first()

        # check if amount being sent is valid
        if not SENDER.isAmount(amount):
            msg = MSG("Error", "Invalid Amount, try again.")
            await client.say(embed=msg)
            logger.info("tip, invalid amount | user : {0} |"
                        " amount : {1} | sender : {2}".format(RECEIVER.did, amount, SENDER.did))


        # check if user exists in DB, if not then create new user
        elif not RECEIVER and SENDER.isAmount(amount):

            newUser = Users(uname=None, uid=0, did=did, stake_earned=0,
                            bid=0, addr=None, bal=NEW_USER_BAL, Lflip=0, Lroll=0)
            db.add(newUser)
            db.commit()
            newUser = db.query(Users).filter(Users.did==did).first()
            if SENDER.did == str(did):
                msg = MSG("Error", "Please do not tip yourself")
                await client.say(embed=msg)
                logger.info(
                    "tip, user tried to tip themself | receiver : {0} | amount : {1} | sender : {2}".format(
                        newUser.did,
                        amount,
                        SENDER.did))
            else:
                amount = float(amount)
                SENDER.bal -= amount
                newUser.bal += amount
                tx1 = Txs(uid=SENDER.uid, tid=None, amount=amount, type="tip", hash=None, success=1)
                tx2 = Txs(uid=newUser.uid, tid=None, amount=amount, type="tip", hash=None, success=1)
                db.add(tx1, tx2)
                db.commit()
                title = "POSQ Tip"
                content = "New User Created!\n<@{0}> tipped <@{1}> ** {2} POSQ**".format(SENDER.did,
                                                                                         newUser.did,
                                                                                         float(amount))
                url = "https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png".format(uname)
                msg = MSG(title, content, url)
                logger.info("tip, new user created then tipped. | newuser : {0} |"
                            " amount : {1} | sender : {2}".format(newUser.did, amount, SENDER.did))
                await client.say(embed=msg)


        elif SENDER.did == str(did):
            msg = MSG("Error", "Please do not tip yourself")
            await client.say(embed=msg)
            logger.info(
                "tip, user tried to tip themself | receiver : {0} | amount : {1} | sender : {2}".format(
                    RECEIVER.did,
                    amount,
                    SENDER.did))

        elif RECEIVER and SENDER.isAmount(amount):
            amount = float(amount)
            SENDER.bal -= amount
            RECEIVER.bal += amount
            tx1 = Txs(uid=SENDER.uid, tid=None, amount=amount, type="tip", hash=None, success=1)
            tx2 = Txs(uid=RECEIVER.uid, tid=None, amount=amount, type="tip", hash=None, success=1)
            db.add(tx1, tx2)
            db.commit()
            title = "POSQ Tip"
            content = "<@{0}> tipped <@{1}> ** {2} POSQ**".format(SENDER.did, RECEIVER.did, float(amount))
            url = "https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png".format(uname)
            msg = MSG(title, content, url)
            await client.say(embed=msg)
            logger.info("tip success | user : {0} |"
                        " amount : {1} | sender : {2}".format(RECEIVER.did, amount, SENDER.did))



@client.command(pass_context=True)
async def bot(ctx):
    try:
        RPC = Connect.RPC()
        bal = RPC.getbalance()
        title = "Bot Balance"
        content = "**" + str(bal) + "**"
        msg = MSG(title, content)
        await client.say(embed=msg)
        logger.info("bot, checked balance | bal : {0} ".format(str(bal)))

    except Exception as e:
        title = "Error"
        content = "Wallet Daemon is down."
        msg = MSG(title, content)

        await client.say(embed=msg)
        logger.info("botBal, daemon is down | Exception : {0} ".format(str(e)))

@client.command(pass_context=True)
async def blockheight(ctx):
    try:
        RPC = Connect.RPC()
        height = RPC.getblockcount()
        title = "POSQ Block Height"
        content = height
        logger.info("blockheight, checked top block | height : {0} ".format(str(height)))
        msg = discord.Embed(color=0x00b3b3)
        msg.add_field(name=title, value=content, inline=False)
        await client.say(embed=msg)
    except Exception as e:
        title = "Error"
        content = "Wallet Daemon is down."
        msg = MSG(title, content)
        await client.say(embed=msg)
        logger.info("botBal, daemon is down | Exception : {0} ".format(str(e)))


@client.command(pass_context=True)
async def bct(ctx, bid=None):
    uname = ctx.message.author
    did = ctx.message.author.id
    db = Connect.db()
    user = db.query(Users).filter_by(did=did).first()
    if (bid == None):
        title = "Error"
        content = "Invalid BCT ID\nExample : !bct 1234567"

        msg = MSG(title, content)
        await client.say(embed=msg)
        logger.info("bct invalid bct id | bid : {0} ".format(str(bid)))
    elif user == None:
        title = "Error"
        content = "!create an account first."
        msg = MSG(title, content)
        await client.say(embed=msg)
        logger.info("bct user not registered yet | bid : {0} | user : {1}".format(str(bid), did))
    else:
        # USER ALREADY HAS A DATABASE ENTRY
        if isBCT(bid):
            # insert POSQ address into db
            user.bid = bid
            db.commit()
            title = "BCT ID"
            content = '{0} has been set as your BCT userID'.format(str(user.bid))
            url = "https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png".format(uname)
            msg = MSG(title, content, url)

            await client.say(embed=msg)
            logger.info("bct updated bct id | bid : {0} | user : {1}".format(str(bid), did))
        else:
            title = "Error"
            content = "Invalid BCT ID\nExample : !bct 1234567"
            logger.info("bct invalid bct id | bid : {0} ".format(str(bid)))
            msg = MSG(title, content)
            await client.say(embed=msg)

@client.command(pass_context=True)
async def help(ctx):
    title = "POSQ Bot Help Desk"
    content = "\n**!create** Register with Bot." \
           "\n**!bal** Check your Balance" \
           "\n**!bot**  Check Bot balance" \
           "\n**!me**  View your profile" \
           "\n**!game** View your game activity" \
           "\n**!stake** View your stake activity" \
           "\n**!leaders** Game High Scores" \
           "\n**!blockheight**  Current BlockHeight" \
           "\n**!donate** AMOUNT  | Donate to Devs" \
           "\n**!bct** USERID  | EXAMPLE !bct 1234567" \
           "\n**!roll** GUESS BET | EXAMPLE : !roll 6 5" \
           "\n**!deposit** Bot will DM you instructions" \
           "\n**!flip** GUESS BET | EXAMPLE : !flip heads 5" \
           "\n**!withd** EXAMPLE !withd ADDRESS AMOUNT" \
           "\n**!rain** AMOUNT #OFUSERS | EXAMPLE !rain 5 50" \
           "\n**!tip** @USER AMOUNT | EXAMPLE : !tip @arkitekt 5" \
           "\nGet POSQ Wallet  : https://posq.space/#downloads"
    msg = MSG(title, content)
    await client.say(embed=msg)

@client.event
async def on_ready():
    print("POSQ Bot Online!")
    print("Name: {}".format(client.user.name))
    print("ID: {}".format(client.user.id))


@client.command(pass_context=True)
async def ping(ctx):
    did = ctx.message.author.id
    msg = discord.Embed(color=0x00b3b3)
    title = "POSQ Bot "
    content = "**PONG!**"
    msg = MSG(title, content)
    await client.say(embed=msg)
    logger.info("ping/pong | user : {0} ".format(did))

@client.command(pass_context=True)
async def hug(ctx, user=None):
    did = ctx.message.author.id
    msg = discord.Embed(color=0x00b3b3)
    title = "POSQ Bot"
    if user == None:
        content = "hugs <@{0}>".format(did)
    else:
        content = "hugs {0}".format(user)
    msg = MSG(title, content)
    await client.say(embed=msg)


if __name__ == "__main__":
    client.run(environ.get('token'))


# this splits messages into chunks of 2000 chars
#for chunk in [newList[i:i+2000]for i in range(0, len(newList), 2000)]:
#   await client.say(chunk)
