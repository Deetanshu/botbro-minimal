"""

935 strat runfile
"""

import bot_utils as x
from logger import Logger
from datetime import datetime as dt
from datetime import timedelta as td
import math
import concurrent.futures
import pytz
import time
from agent import Agent

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
report = Agent("935")
l = Logger("strat_200x")

plist = x.create_profiles(profiles, l)

def sleep(num_sec):
    iterations = math.floor(num_sec/5)
    remainder = num_sec%5
    for _ in range(iterations):
        time.sleep(5)
    time.sleep(remainder)

def runthis(plist, base_url, test, l):  
    profiles = plist
    current_datetime = dt.now(pytz.timezone('Asia/Kolkata'))
    #ist = pytz.timezone('Asia/Kolkata')
    today = dt.date(current_datetime)
    exec_date = today.strftime("%d %B, %Y")
    wl_dt = dt.strptime(
        f"09:25:00:10 {exec_date} +0530", "%H:%M:%S:%f %d %B, %Y %z"
    )
    check_dt = dt.strptime(
        f"09:33:00:10 {exec_date} +0530", "%H:%M:%S:%f %d %B, %Y %z"
    )
    watchlist = []
    watch_price = 180
    all_flags = False
    execute = None
    flags = [False,False,False]
    target_price = 200
    stoploss = 180
    current_datetime = dt.now(pytz.timezone('Asia/Kolkata'))
    sleep_time = (wl_dt - current_datetime).total_seconds()-5
    sleep_time = max(sleep_time, 0)
    report.action("Main Run Function", str("Sleep until "+dt.strftime(wl_dt, "%d %B, %Y %H:%M")+"."))
    report.next_up("Main Run Function", "Watchlist Generation", "Create watchlist after sleep")
    sleep(sleep_time)
    report.action("Main Run Function","Creating watchlist")
    report.next_up("Main Run Function","Checking for watchlist creation")
    next_action_flag = False

    while (not all_flags):
        
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
                print(f"Watchlist: {str(watchlist)}")
        if current_datetime >= check_dt and flags[0] and not flags[1]:
            if not next_action_flag:
                report.action("Main Run Function","Monitoring Watchlist")
                report.next_up("Main Run Function","Place Buy Order")
                next_action_flag = True
            #print("Updating watchlist: "+str(watchlist))
            highest = 0
            for i in watchlist:
                if i["last_price"] > highest:
                    highest = i["last_price"]
                    execute = i
            sleep(1)
            if highest >= 200:
                target_price = highest+30
                stoploss = highest - 25
                flags[1] = True
            else:
                wl = [i["symbol"] for i in watchlist]
                quotes = x.get_quotes(profiles[0], wl, l, "NFO")
                for i in watchlist:
                    try:
                        i["last_price"] = quotes[i["symbol"]]
                    except Exception:
                        l.error_mail("UPDATING WATCHLIST")
                        continue

            if flags[1] and execute is not None:
                report.action("Main Run Function","Placing Buy Order")
                report.next_up("Main Run Function","Monitor For Active Sell")
                profiles = x.buy_active_sell(profiles,
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
                                  stoploss = stoploss,
                                  test = test)
                all_flags = True
        else:
            sleep_time = (check_dt-current_datetime).total_seconds()-2
            if sleep_time < 3:
                sleep_time = 0
            print(f"Sleeping for {str(sleep_time)}")
            sleep(sleep_time)

    return profiles
            
last_date = dt.date(dt.strptime("11 March, 2023 +0530", "%d %B, %Y %z"))
ist = pytz.timezone('Asia/Kolkata')
test = False
exec_date_str = (last_date+td(days=1)).strftime("%d %B, %Y")
while True:                    
    current_datetime = dt.now(ist)
    current_date = dt.date(current_datetime)
    execute_datetime = dt.strptime(
        f"09:20:00:10 {exec_date_str} +0530", "%H:%M:%S:%f %d %B, %Y %z"
    )
    exec_dt_2 = dt.strptime(
        f"14:55:00:10 {exec_date_str} +0530", "%H:%M:%S:%f %d %B, %Y %z"
    )
    if current_date > last_date:
        report.action("Main Run Function", "Logging into profiles")
        report.next_up("Main Run Function", "Watchlist Generation", "Create watchlist after login")
        retries = 0
        while (retries <5):
            try:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = [executor.submit(x.api_weblogin, base_url, p,l) for p in plist]
                    profiles = [f.result() for f in futures]
                break
            except Exception as e:
                if retries <5:
                    print("Retrying login.")
                else:
                    print("Giving up")
                    exit()
                retries += 1
        last_date = current_date
        current_datetime = dt.now(ist)
        num_sec = math.floor((execute_datetime-current_datetime).total_seconds()) - 40
        report.action("Main Run Function", str("Sleeping until "+dt.strftime(execute_datetime, "%d %B, %Y %H:%M")+"."))
        report.next_up("Main Run Function", "Watchlist Generation", "Login to profiles")
        while(current_datetime <= execute_datetime):
            print("not yet")
            print("cr:",current_datetime)
            print("Ex:",execute_datetime)
            sleep(2)


        run_var = True
        try:
            plist = runthis(profiles, base_url, test, l)
        except Exception:
            print("Error in runthis, retrying before quitting.")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(x.api_weblogin, base_url, p,l) for p in plist]
                profiles = [f.result() for f in futures]
            plist = runthis(profiles, base_url, test, l)
        print("Done")
        exec_date = (last_date+td(days=1))
        while(exec_date.weekday()>=5):
            exec_date = (exec_date+td(days=1))

        exec_date_str = exec_date.strftime("%d %B, %Y")
        if current_date.weekday() >0 and current_date.weekday() <4:
            current_datetime = dt.now(ist)
            sleep_time = (exec_dt_2 - current_datetime).total_seconds() - 2
            sleep_time = max(sleep_time, 0)
            sleep(sleep_time)
    else:
        num_sec = math.floor((execute_datetime-current_datetime).total_seconds()) - 150
        print("Sleeping for ", num_sec)
        report.action("Main Run Function", str("Sleeping until "+dt.strftime(execute_datetime, "%d %B, %Y %H:%M")+"."))
        report.next_up("Main Run Function", "Login to Profiles", "Login to profiles")
        if num_sec <0:
            num_sec = 30
        sleep(num_sec)

