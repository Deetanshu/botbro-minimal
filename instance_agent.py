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

while(True):
    proc_objs = findProcessIdByName("python")
    num_proc = len(proc_objs)

    temp = psutil.virtual_memory()
    perc_ram = temp[2]
    tot_ram_used = temp[3]
    cpu_usage = psutil.cpu_percent(5)

    query_string='insert into botbro.log_monitor values( now(), '+cpu_usage+', '+perc_ram+', '+tot_ram_used+', '+num_proc+');'
    connection.execute(query_string)

    sleep(60)

