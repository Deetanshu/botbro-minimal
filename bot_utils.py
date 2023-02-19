"""
Creating bot bro v0.1 utils

Created on 22/01/2023
Author: Deeptanshu Paul (deeptanshupaul@gmail.com)

Notes:
1. Improve security by converting the existing storage to a json file with the data encrypted.
2. Convert the utils into an object so webdriver path etc can be changed.
"""

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from pyotp import TOTP
import urllib.parse as u
import kiteconnect as k 
import json
import requests
import pytz
from datetime import datetime as dt
import math
import threading
from optionchain_stream import OptionChain


class Profile():
    """
    Creating an object to store each profile's information.
    In order to create it, you require a profile name, username, password and TOTP code.
    The TOTP code is a 32 digit string provided through the Zerodha 2FA setup.

    """
    def __init__(self, profilename, username, password, totp_code, api_key, api_secret, logger, kite=None, access_token=None):
        self.profilename = profilename
        self.name = profilename
        self.username = username
        self.password = password
        self.totp_code = totp_code
        self.api_key = api_key
        self.api_secret = api_secret
        self.logger = logger 
        self.access_token = access_token
        self.kite = kite
        self.logger.fwrite(str("[INFO] Profile created for username "+self.username+" with name "+self.profilename))
    
    def set_access_token(self, access_token):
        self.logger.fwrite(str("[LOG] "+self.username+": Setting access token "))
        self.access_token = access_token
        if self.access_token == None:
            self.logger.fwrite("[ERROR] Access token still not set.")
            return False
        else:
            self.logger.fwrite("[LOG] SUCCESS: Access token set.")
            return True
    
    def set_kite_object(self, kite):
        self.logger.fwrite(str("[LOG] "+self.username+": Setting kite object "))
        self.kite = kite
        if self.kite == None:
            self.logger.fwrite("[ERROR] Kite object not created.")
            return False
        else:
            self.logger.fwrite("[LOG] SUCCESS: Kite object set.")
            return True

""" TODO: Saved for v0.2:
def load_profiles(profile_json_path):
    prof_json = json.load(open(profile_json_path))
    profiles = []
    for i in prof_json.values():
"""        

# Method to get nearest strikes
def round_nearest(x,num=50): return int(math.ceil(float(x)/num)*num)
def nearest_strike_bnf(x): return round_nearest(x,100)
def nearest_strike_nf(x): return round_nearest(x,50)

# Urls for fetching Data
url_oc      = "https://www.nseindia.com/option-chain"
url_bnf     = 'https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY'
url_nf      = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
url_indices = "https://www.nseindia.com/api/allIndices"

# Headers
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'accept-language': 'en,gu;q=0.9,hi;q=0.8',
            'accept-encoding': 'gzip, deflate, br'}

sess = requests.Session()
cookies = dict()

# Local methods
def set_cookie(logger):
    request = sess.get(url_oc, headers=headers, timeout=5)
    cookies = dict(request.cookies)
    logger.fwrite("[LOG] Cookies set")

def get_data(url, logger):
    set_cookie(logger)
    #logger.error_mail(" COOKIES SETTING ")
    response = sess.get(url, headers=headers, timeout=5, cookies=cookies)
    if(response.status_code==401):
        set_cookie(logger)
        response = sess.get(url_nf, headers=headers, timeout=5, cookies=cookies)
    if(response.status_code==200):
        return response.text
    return ""

#Utility function to get all calls and puts
def get_all_calls_puts(url, logger):
    call_put_list=[]
    response_text= get_data(url, logger)
    data = json.loads(response_text)
    for item in data['records']['data']:
        try:
            temp = {
                "type":"CALL",
                "askprice":item["CE"]["askPrice"],
                "bidprice":item["CE"]["bidPrice"],
                "expiry": item["CE"]["expiryDate"],
                "LTP": item['CE']['lastPrice'],
                "symbol": str(item["CE"]["underlying"])+str(item["CE"]["expiryDate"][-2:])+str(item["CE"]["expiryDate"][3])+str(item["CE"]["expiryDate"][:2])+str(item["CE"]["strikePrice"])+"CE"
            }
            call_put_list.append(temp)
        except:
            try:
                temp = {
                    "type":"PUT",
                    "askprice":item["PE"]["askPrice"],
                    "bidprice":item["PE"]["bidPrice"],
                    "expiry": item["PE"]["expiryDate"],
                    "LTP": item["PE"]["lastPrice"],
                    "symbol": str(item["PE"]["underlying"])+str(item["PE"]["expiryDate"][-2:])+str(item["PE"]["expiryDate"][3])+str(item["PE"]["expiryDate"][:2])+str(item["PE"]["strikePrice"])+"PE"
                }
                call_put_list.append(temp)
            except:
                call_put_list = call_put_list
        return call_put_list

# Function to create profiles 
def create_profiles(profilelist, logger):
    profiles = []
    logger.fwrite("[LOG] Creating profiles.")
    for i in profilelist:
        profiles.append(Profile(i['profilename'], i['username'], i['password'], i['totp'], i['api_key'], i['api_secret'], logger))
    
    return profiles

# Function to log into a profile using chrome
def api_weblogin(base_url, profile, logger):
    url = str(base_url+profile.api_key)
    
    username = profile.username
    password = profile.password
    totp = profile.totp_code
    api_secret = profile.api_secret 
    
    
    # Beginning the Chrome GUI based input of profile details.
    

    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)
    driver.maximize_window()
    user = driver.find_element("xpath", "//input[@type = 'text']")
    user.send_keys(username)

    #input password
    pwd = driver.find_element("xpath","//input[@type = 'password']")
    pwd.send_keys(password)

    #click on login
    driver.find_element("xpath", "//button[@type='submit']").click()

    sleep(1)

    #input totp
    ztotp      = driver.find_element("xpath","//input[@type = 'text']")
    totp_token = TOTP(totp)
    token      = totp_token.now()
    ztotp.send_keys(token)

    #click on continue
    try:
        driver.find_element("xpath","//button[@type = 'submit']").click()
    except:
        logger.fwrite(str("Already submitted."))

    sleep(2)
    #Obtaining the request token
    req_url = str(driver.current_url)
    parsed_url = u.urlparse(req_url)
    request_token = u.parse_qs(parsed_url.query)['request_token'][0]

    #Logging into kite and obtaining access token
    kite = k.KiteConnect(api_key=profile.api_key)
    data = kite.generate_session(request_token, api_secret= api_secret)
    access_token = data["access_token"]

    #Setting access token to enable reuse of one login.

    profile.set_access_token(access_token)
    profile.set_kite_object(kite)
    driver.quit()
    if profile.access_token is not None:
        return profile 
    
    return None 

# Get Quote for different keys 
def get_quotes(profile, watchlist, logger, exchange = "NFO", num_retries = 0):
    if num_retries >=5:
        logger.error_mail("Quote number of retries exceeded.")
        return 200
    p = profile
    quotes = {}
    #creating list of instruments
    ins = []
    for i in watchlist:
        ins.append(str(str(exchange)+":"+str(i)).upper())
    
    try:
        response = p.kite.quote(ins)
        for i in range(len(watchlist)):
            try:
                quotes[watchlist[i]]=float(response[ins[i]]["last_price"])
                logger.fwrite(str("[LOG] Quote fetched for "+watchlist[i]+" price: "+str(response[ins[i]]['last_price'])))
            except:
                logger.fwrite("GET QUOTE - QUOTE MISSING, retrying")
                quotes = get_quotes(profile, watchlist, logger, exchange, num_retries+1)
        return quotes 

    except:
        logger.fwrite("GET QUOTE - NO RESPONSE, retrying")
        return get_quotes(profile, watchlist, logger, exchange, num_retries+1)
    
# Get order status in text format
def get_orders_status_text(profile):
    response = profile.kite.orders()
    returntext = str("\nProfile for: "+profile.name+"\n\n")
    returntext = str(returntext + response.text+'\n\n')
    return returntext
                     
        
# Buy order placing, ACTIVE sell order & stoploss monitoring function
# Rework this to use threading

def buy_active_sell(profiles, variety, exchange, tradingsymbol, quantity, product, order_type, price, validity, logger, target=250, stoploss=0, interval = 1):
    orderids = []
    for p in profiles:
        orderid = p.kite.place_order(tradingsymbol = tradingsymbol,
                                     variety = variety,
                                     exchange = exchange,
                                     transaction_type = 'BUY',
                                     quantity = quantity,
                                     product = product,
                                     order_type = order_type,
                                     price = price,
                                     validity = validity
            )
        orderids.append(orderid)
        logger.fwrite(str("[LOG] BUY Order created for "+p.name+" with orderid "+orderid))
    
    while(True):
        quote = get_quotes(profiles[0], [tradingsymbol], logger, exchange)
        if quote[tradingsymbol] >= target:
            for p in profiles:
                orderid = p.kite.place_order(tradingsymbol = tradingsymbol,
                                             variety = variety,
                                             exchange = exchange,
                                             transaction_type = 'SELL',
                                             quantity = quantity,
                                             product = product,
                                             order_type = order_type,
                                             price = price,
                                             validity = validity
                    )
                logger.fwrite(str("[LOG] SELL Order created for "+p.name+" with orderid "+orderid+" at price "+str(quote[tradingsymbol])))
            logger.order_list_mail(profiles)
            return True
        if quote[tradingsymbol] <= stoploss:
            for p in profiles:
                orderid = p.kite.place_order(tradingsymbol = tradingsymbol,
                                             variety = variety,
                                             exchange = exchange,
                                             transaction_type = 'SELL',
                                             quantity = quantity,
                                             product = product,
                                             order_type = order_type,
                                             price = stoploss,
                                             validity = validity
                    )
                
            logger.fwrite(str("[LOG] SELL Order created for "+p.name+" with orderid "+orderid+" at price "+str(quote[tradingsymbol])))
            logger.order_list_mail(profiles)
            return True
        sleep(interval)

def get_watchlist_200x(profile, bot_price, logger):
    expirylist = ["2023-02-02","2023-02-09", "2023-02-16", "2023-02-23", "2023-03-02", "2023-03-09", "2023-03-16", "2023-03-23", "2023-03"]
    watchlist = []
    i = 0
    while(len(watchlist)==0):
        logger.fwrite(str("[LOG] getting data with expiry: "+expirylist[i]))
        OptionStream = OptionChain("NIFTY",expirylist[i], profile.api_key, access_token = profile.access_token)
        OptionStream.sync_instruments()
        StreamData = OptionStream.create_option_chain()
        temp = None
        for data in StreamData:
            if len(data)==0:
                i = i+1
                continue 
            temp = data
            if type(temp) == list:
                break 
        for t in temp:
            if t['last_price']>=bot_price and t['last_price']<=200:
                watchlist.append({'symbol':t['symbol'], 'last_price':t['last_price']})
        i = i+1
    return watchlist 



    
    
    


