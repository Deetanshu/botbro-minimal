"""
Instance monitoring agent 
"""

import connector_v2 as conn 
import email_utils as email
import logger 
import psutil
from time import sleep

logger = logger.Logger("is_alive")
config = email.Config("info.botbro@gmail.com", "bqkbdousbipsbfhu")

connection = conn.sql_connector("mysql", "root", "Deeptanshu97007", "34.93.184.62", 3306, "botbro")
def findProcessIdByName(processName):
    '''
    Get a list of all the PIDs of a all the running process whose name contains
    the given string processName
    '''
    listOfProcessObjects = []
    #Iterate over the all the running process
    for proc in psutil.process_iter():
       try:
           pinfo = proc.as_dict(attrs=['pid', 'name', 'create_time'])
           # Check if process name contains the given name string.
           if processName.lower() in pinfo['name'].lower() :
               listOfProcessObjects.append(pinfo)
       except (psutil.NoSuchProcess, psutil.AccessDenied , psutil.ZombieProcess) :
           pass
    return listOfProcessObjects;

num_inserts = 0
while(True):
    proc_objs = findProcessIdByName("python")
    num_proc = len(proc_objs)

    temp = psutil.virtual_memory()
    perc_ram = temp[2]
    tot_ram_used = temp[3]
    cpu_usage = psutil.cpu_percent(5)

    query_string='insert into botbro.log_monitor values( now(), '+str(cpu_usage)+', '+str(perc_ram)+', '+str(tot_ram_used)+', '+str(num_proc)+');'
    connection.execute(query_string)
    num_inserts = num_inserts+1
    sleep(60)
    if num_inserts >= 1500:
        connection.engine.dispose()
        connection.welcome()
        query_str = "delete from botbro.log_monitor where date(time) < date(now);"
    

