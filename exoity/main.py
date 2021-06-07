from datetime import datetime as dt
import MetaTrader5 as mt5
from time import sleep
import pandas as pd

# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)

# establish connection to the MetaTrader 5 terminal
if not mt5.initialize(path=r'C:\Program Files\MetaTrader 5\terminal64.exe', login=46974312, server="MetaQuotes-Demo",password="8emroppt"):
    print("initialize() failed, error code =",mt5.last_error())
    quit()
else:
    print(mt5.initialize(path=r'C:\Program Files\MetaTrader 5\terminal64.exe', login=46974312, server="MetaQuotes-Demo",password="8emroppt"))

# display data on connection status, server name and trading account
print(mt5.terminal_info())
# display data on MetaTrader 5 version
print(mt5.version())
 
# shut down connection to the MetaTrader 5 terminal
# mt5.shutdown()


class Symbol:

    def __init__(self,
                 name="",
                 lot_size=0,
                 stop_loss=0,
                 take_profit=0,
                 dataframe_M15=pd.DataFrame(),
                 dataframe_M30=pd.DataFrame(),
                 dataframe_H1=pd.DataFrame(),
                 dataframe_H4=pd.DataFrame()):
        self.name = name
        self.lot_size = lot_size
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.dataframe_M15 = dataframe_M15
        self.dataframe_M30 = dataframe_M30
        self.dataframe_H1 = dataframe_H1
        self.dataframe_H4 = dataframe_H4

TIMEFRAMES = [
    mt5.TIMEFRAME_M15,
    mt5.TIMEFRAME_M30,
    mt5.TIMEFRAME_H1,
    mt5.TIMEFRAME_H4
]


current_tick = float()
last_tick = float()

symbol_to_trade = Symbol(name="XAUUSD",
                    lot_size=0.02,
                    stop_loss=500,
                    take_profit=300)
timeframe = 1
close_order_deviation = 20
current_ea_comments = "Exoity V1.3"
selected=mt5.symbol_select("XAUUSD",True)
if not selected:
    print("selected = ",selected)

def get_last_tick(symbol):
    last_tick = mt5.symbol_info_tick(symbol)
    print("get_last_tick = ",mt5.symbol_info_tick(symbol))
    return last_tick


def send_order_sell(symbol="Volatility 75 Index", comments="python script open", lot_size=0.001, take_profit=250000,
                    stop_loss=100000):
    # prepare the sell request structure
    symbol_info = mt5.symbol_info(symbol)

    if symbol_info is None:
        print(symbol, "not found, can not call order_check()")
        mt5.shutdown()
        quit()

    lot = lot_size
    STOP_LOSS = stop_loss
    TAKE_PROFIT = take_profit
    # lot = 1.5
    point = mt5.symbol_info(symbol).point
    price = mt5.symbol_info_tick(symbol).bid
    deviation = 20
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": price + STOP_LOSS * point,
        "tp": price - TAKE_PROFIT * point,
        "deviation": deviation,
        "magic": 234000,
        "comment": comments,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    # send a trading request
    result = mt5.order_send(request)

    return result, request


def send_order_buy(symbol="Volatility 75 Index", comments="python script open", lot_size=0.001, take_profit=250000,
                   stop_loss=100000):
    # prepare the buy request structure
    symbol_info = mt5.symbol_info(symbol)

    if symbol_info is None:
        print(symbol, "not found, can not call order_check()")
        mt5.shutdown()
        quit()

    lot = lot_size
    STOP_LOSS = stop_loss
    TAKE_PROFIT = take_profit
    # lot = 1.5
    point = mt5.symbol_info(symbol).point
    price = mt5.symbol_info_tick(symbol).ask
    deviation = 20
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": price - STOP_LOSS * point,
        "tp": price + TAKE_PROFIT * point,
        "deviation": deviation,
        "magic": 234000,
        "comment": comments,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    # send a trading request
    result = mt5.order_send(request)

    return result, request

def close_trade(action, buy_request, result, deviation):
    '''
        https://www.mql5.com/en/docs/integration/python_metatrader5/mt5ordersend_py
    '''
    # create a close request
    symbol = buy_request['symbol']
    if action == 'buy':
        trade_type = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).ask
    elif action =='sell':
        trade_type = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).bid
    position_id=result.order
    lot = buy_request['volume']

    close_request={
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": trade_type,
        "position": position_id,
        "price": price,
        "deviation": deviation,
        "magic": 12000,
        "comment": "python script close",
        "type_time": mt5.ORDER_TIME_GTC, # good till cancelled
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    # send a close request
    result = mt5.order_send(close_request)
    return result

# run

def determine_result(open_price,close_price):
    if open_price > close_price:
        return 'negative'
    elif open_price <= close_price:
        return 'positive'

def main():

    # date_from = dt.now()
    # date_to = dt(2021,6,10,23,59,59)
    #
    has_last_price = False
    buy_signal = False
    sell_signal = False

    print("begin run cal")
    while True:

        if has_last_price == False and dt.now().minute % timeframe == 0:
            last_price = get_last_tick(symbol_to_trade.name).ask
            has_last_price = True
            print("last price = ",last_price)
            print("sleep 60")
            sleep(60)

        if has_last_price == True and dt.now().minute % timeframe == 0:
            current_price = get_last_tick(symbol_to_trade.name).ask
            print("last price = ", current_price)
            delta = current_price - last_price
            print("delta = ", delta)
            if delta > 0:
                buy_signal = True
            else:
                sell_signal = True

            break

        print("sleep 1")
        sleep(1)

    print("chot lenh")
    if buy_signal == True:
        result, request = send_order_buy(symbol=symbol_to_trade.name,
                                         lot_size=symbol_to_trade.lot_size,
                                         stop_loss=symbol_to_trade.stop_loss,
                                         take_profit=symbol_to_trade.take_profit,
                                         comments=current_ea_comments)
        print("buy_signal = ", request)
        print("buy_signal = ", result)
    elif sell_signal == True:
        result, request = send_order_sell(symbol=symbol_to_trade.name,
                                          lot_size=symbol_to_trade.lot_size,
                                          stop_loss=symbol_to_trade.stop_loss,
                                          take_profit=symbol_to_trade.take_profit,
                                          comments=current_ea_comments)
        print("sell_signal = ", request)
        print("sell_signal = ", result)
    print("end")

    while True:
        buy_signal = False
        sell_signal = False
        if dt.now().minute % timeframe == 0:

            close_trade('sell',request,result,close_order_deviation)
            close_trade('buy',request,result,close_order_deviation)

            last_price = current_price
            current_price = get_last_tick(symbol_to_trade.name).ask
            delta = current_price - last_price

            if delta > 0:
                buy_signal = True
            elif delta < 0:
                sell_signal = True

            if buy_signal == True:
                result, request = send_order_buy(symbol=symbol_to_trade.name,
                                                 lot_size=symbol_to_trade.lot_size,
                                                 stop_loss=symbol_to_trade.stop_loss,
                                                 take_profit=symbol_to_trade.take_profit,
                                                 comments=current_ea_comments)
            elif sell_signal == True:
                result, request = send_order_sell(symbol=symbol_to_trade.name,
                                                  lot_size=symbol_to_trade.lot_size,
                                                  stop_loss=symbol_to_trade.stop_loss,
                                                  take_profit=symbol_to_trade.take_profit,
                                                  comments=current_ea_comments)

            sleep(60)

        sleep(1)

if __name__ == "__main__":
    main()