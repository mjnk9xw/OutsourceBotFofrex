from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import MetaTrader5 as mt5
 
account=40513145
authorized=mt5.login(account, password="c1ylysde")  

# connect to MetaTrader 5
if not mt5.initialize():
    mt5.initialize()
 
# request connection status and parameters
print(mt5.terminal_info())
# get data on MetaTrader 5 version
print(mt5.version())
 
start_date=datetime(2021,6,5,12)
end_date=datetime(2021,6,5,23)

# request 1000 ticks from EURAUD
#datetime(year,month,day,hour)
XAUUSD_ticks = mt5.copy_ticks_from("XAUUSD", start_date, 1000, mt5.COPY_TICKS_ALL)
# request ticks from AUDUSD within 2019.04.01 13:00 - 2019.04.02 13:00
 
# shut down connection to MetaTrader 5
mt5.shutdown()
 
#DATA
# print('euraud_ticks(', len(XAUUSD_ticks), ')')
print(XAUUSD_ticks)
for val in XAUUSD_ticks[:10]: 
    print(val)

#PLOT
# create DataFrame out of the obtained data
ticks_frame = pd.DataFrame(euraud_ticks)
# convert time in seconds into the datetime format
ticks_frame['time']=pd.to_datetime(ticks_frame['time'], unit='s')
# display ticks on the chart
plt.plot(ticks_frame['time'], ticks_frame['ask'], 'r-', label='ask')
plt.plot(ticks_frame['time'], ticks_frame['bid'], 'b-', label='bid')
 
# display the legends
plt.legend(loc='upper left')
 
# add the header
plt.title('EURAUD ticks')
 
# display the chart
plt.show()