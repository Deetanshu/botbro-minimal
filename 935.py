"""

935 strat runfile
"""

import bot_utils as x
from logger import Logger
from datetime import datetime as dt
from datetime import timedelta as td
import datetime as dd
import threading
import pytz
from time import sleep

# Manually input these variables.
lots = 1
profiles = [
    {
        "profilename":"Deeptanshu",
        "username":"QZ1017",
        "password":"Horse dog123",
        "totp":"BIAY4GY6KOKTOH5HD3POCJ3NOBWOCUYY",
        "api_key":"xf76cgao54l6479p",
        "api_secret":"k67uq14zxbag151jdql3eokxt5qu3m43"
},
    {
     "profilename":"Puneeth",
     "username":"PA6857",
     "password":"Puneeth1!",
     "totp":"A4OMLDJJGPE233YWQFFDQ565DBYFBBLV",
     "api_key":"d2ipgsdidxoif87a",
     "api_secret":"vjskttygqc4x07xu77r4rayj0fxh9es6"
     },

{
     "profilename":"Ukash",
     "username":"GI9654",
     "password":"Studies7&",
     "totp":"T36PTEXJ5URPZMS5327AKZB6JNMWVQRM",
     "api_key":"gqis1i342ur7uamy",
     "api_secret":"oejua6cxkn6wg0jhmvjh9h56pxt1bji4"
 },
]
base_url = "https://kite.zerodha.com/connect/login?v=3&api_key="

l = Logger("strat_200x")

plist = x.create_profiles(profiles, l)
def watchlist_200x(profile,bot_price, l):
    try:
        call_put_list = x.get_all_calls_puts("https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY", l)
    except:
        try:
            call_put_list = x.get_optionstream(profile, l)
        except:
            print("Error in both so retrying...")
            l.fwrite("[LOG] Retrying by recursion. ")
            return watchlist_200x(profile, bot_price, l)
    wl = []
    for i in call_put_list:
        if i["askprice"]>=bot_price and i["askprice"]<=200:
            wl.append(i)
    return wl
def runthis(plist, base_url, l):
    profiles = []
    for p in plist:
        profiles.append(x.api_weblogin(base_url, p, l))
    
    current_datetime = dt.now(pytz.timezone('Asia/Kolkata'))
    ist = pytz.timezone('Asia/Kolkata')
    today = dt.date(current_datetime)
    exec_date = today.strftime("%d %B, %Y")
    end_dt = dt.strptime("09:55:00:10 "+exec_date+" +0530", "%H:%M:%S:%f %d %B, %Y %z")
    check_dt = dt.strptime("09:33:00:10 "+exec_date+" +0530", "%H:%M:%S:%f %d %B, %Y %z")
    watchlist = []
    watch_price = 180
    all_flags = False
    execute = None
    flags = [False,False,False]
    target_price = 200
    stoploss = 180
        
    while(not all_flags):
        current_datetime = dt.now(pytz.timezone('Asia/Kolkata'))
        if len(watchlist) == 0:
               watchlist = x.get_watchlist_200x(profiles[0], watch_price, l)
               if len(watchlist)==0:
                   watch_price = watch_price - 1
                   sleep(10)
                   if watch_price <150:
                       l.error_mail("NO ELIGIBLE CALLS OR PUTS")
                     #  break
               else:
                    flags[0]=True
                    l.fwrite("[LOG] WATCHLIST CREATED")
        if current_datetime >= check_dt and flags[0] and not flags[1]:
            highest = 0
            for i in watchlist:
                if i["last_price"] > highest:
                    highest = i["last_price"]
                    execute = i
            sleep(1)
            if highest > 200:
                target_price = highest+30
                stoploss = highest - 25
                flags[1] = True
            else:
                wl = []
                for i in watchlist:
                    wl.append(i["symbol"])
                quotes = x.get_quotes(profiles[0], wl, l, "NFO")
                for i in watchlist:
                    try:
                        i["last_price"] = quotes[i["symbol"]]
                    except:
                        l.error_mail("UPDATING WATCHLIST")
                        continue
                
            if flags[1] and execute is not None:
                x.buy_active_sell(profiles,
                                  variety = "regular",
                                  exchange = "NFO",
                                  tradingsymbol = execute["symbol"],
                                  quantity = lots*50,
                                  product = "MIS",
                                  order_type = "MARKET",
                                  price = execute['last_price'],
                                  logger = l,
                                  validity="DAY",
                                  target = target_price,
                                  stoploss = stoploss)
                all_flags = True
            
last_date = dt.date(dt.strptime("19 February, 2023 +0530", "%d %B, %Y %z"))
ist = pytz.timezone('Asia/Kolkata')
while(True):                    
    current_datetime = dt.now(ist)
    current_date = dt.date(current_datetime)
    exec_date = current_date.strftime("%d %B, %Y")
    execute_datetime = dt.strptime("09:25:00:10 "+exec_date+" +0530", "%H:%M:%S:%f %d %B, %Y %z")
    if current_date > last_date:
        last_date = current_date
        while(current_datetime <= execute_datetime):
            print("not yet")
            print("cr:",current_datetime)
            print("Ex:",execute_datetime)
            sleep(2)
            current_datetime = dt.now(ist)
        run_var = True
        runthis(plist, base_url, l)
        print("Done")
        break
    else:
        print("Sleeping...")
        sleep(60)
    
print("done")
