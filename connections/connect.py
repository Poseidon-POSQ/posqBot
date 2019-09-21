from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bitcoinrpc.authproxy import AuthServiceProxy
from credentials.credentials import *
from os import environ




class Connect:

    def RPC():
        return AuthServiceProxy("http://{0}:{1}@127.0.0.1:{2}".format(environ.get("RPCUSER"),
                                                                      environ.get("RPCPASS"),
                                                                      environ.get("RPCPORT")),
                                                                        timeout=300)

    def db():
        engine = create_engine('mysql+pymysql://{0}:{1}@127.0.0.1/{2}?host=127.0.0.1?port={3}/charset=utf8/'
                               ''.format(environ.get("DBUNAME"),
                                         environ.get("DBPASS"),
                                         environ.get("DB"),
                                         environ.get("DBPORT")))

        return sessionmaker(bind=engine.connect())()

