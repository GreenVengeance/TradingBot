import logging
import time
from config.keys import client

""" Goals for this project
Buy-Sell Crypto automatically
Managa Portfolio to Maximize Profit
Track Price Historis

The reason behind this is that it does not utilize any form of advanced features to determine support and resistance levels, it doesn’t use an adjustable lot size which in my opinion should pretty much always be based on the average true range, and it obviously Lacks programmatic stop loss and take profit functions.

# Training Limit = 5-4% des Vermögens
# Stop Limit setzen in der Regel 60%, soll aber aber zu viel sein
# Wenn der Kurs noch weiter fällt soll der bot nachkaufen…
# Er soll gleiche traidmenge nochmal für weniger Geld nachkaufen
# Max 3mal nachkaufen
#bitfinex nicht ideal, weil immer 0,2% fee --> insgesamt 0,4
# es ist schwerer die richtige Strategie auszuwählen
# HH und LL (Highes High and Lowest Low) und den RSI.
"""
list_of_symbols = ["BTCUSDT", "ETHUSDT"]
RUN = False
'''Please be aware: If True it does nothing and log what it does'''
DRY_run = True


def starting_the_TradingBot():
    global RUN
    RUN = True
    main()


def stopping_the_TradingBot():
    global RUN
    RUN = False
    main()


def tradingBot_sate():
    if RUN == True:
        return "running"
    elif RUN == False:
        return "not running"


def activeTrade():
    orders = client.get_all_orders(symbol='BTCUSDT')

    print("...2")


def main():
    global RUN
    time.sleep(1.5)
    while RUN:
        try:
            activeTrade()
        except Exception as e:
            print(e)
            logging.info(e)

    if RUN == False:
        print("Stopped Bot")


if __name__ == "__main__":
    main()
