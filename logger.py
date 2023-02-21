# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 15:30:18 2023

@author: Deeptanshu Paul

This is the logger class for the main program.

Feature Log:
    - Ability to log data to a file
    - Ability to send emails from the bot email account.

To do:
    - Figure out what improvements can be made lol.

"""

from datetime import datetime as dt
import pytz
import email_utils as e
import bot_utils as b

class Logger():
    def __init__(self, log_file_name, header = None):
        self.log_file_name = log_file_name
        self.header = header
        if header is None:
            header = "Log file created at "+str(dt.now(pytz.timezone('Asia/Kolkata')))
        f = open(log_file_name+".txt", 'w+')
        f.write(header)
        f.close()
        self.data = """"""
        self.all_logs = """"""
        self.config = e.Config("info.botbro@gmail.com", "bqkbdousbipsbfhu")

    def add(self, text):
        try:
            self.data = self.data+"\n"+str(dt.now(pytz.timezone('Asia/Kolkata')))+" --> "+text
            if len(self.all_logs) > 50000:
                self.dump()
                self.dump_mail(["deeptanshupaul@gmail.com"])
                self.all_logs = """"""
                self.refresh()
            self.all_logs = self.all_logs + self.data
        except:
            self.error_mail("add")
    
    def write(self):
        try:
            with open(self.log_file_name+".txt", "a+") as f:
                f.write(self.data)
                self.data = """"""
                f.close()
        except:
            self.error_mail("write")
    
    def dump(self):
        try:
            now = dt.now(pytz.timezone('Asia/Kolkata'))
            filename = self.log_file_name + "_DUMP.txt"
            with open(filename, "w+") as f:
                f.write("DUMP CREATED AT "+str(now))
                f.write(self.all_logs)
                f.close()
        except:
            self.error_mail("dump")

    def fwrite(self, text):
        try:
            self.add(text)
            self.write()
        except:
            self.error_mail("fwrite")
    
    def csv_write(self, log):
        try:
            self.all_logs = self.all_logs+log
            with open(self.log_file_name+".txt", "a+") as f:
                wstr = "\n"+log
                f.write(wstr)
                f.close()
        except:
            self.error_mail("csv_write") 
    
    def error_mail(self, source):
        now = dt.now(pytz.timezone('Asia/Kolkata'))
        to_list = ["deeptanshupaul@gmail.com"]
        subject= "Error Logging at "+str(now)
        body = "Hi, \nPlease find the logs below: "+self.all_logs
        body = body +"\n The time that the service went down is "+str(now)+" and the source is "+str(source)
        e.simple_mail(self.config, to_list, subject, body)
    
    def log_mail(self, to_list):
        now = dt.now(pytz.timezone('Asia/Kolkata'))
        to_list = to_list
        subject= "Logs status "+str(now)
        body = "Hi, \nPlease find the logs below: "+self.all_logs
        body = body +"\nKind Regards, \nDeeptanshu on the cloud"
        e.simple_mail(self.config, to_list, subject, body)
    
    def order_list_mail(self, profiles):
        now = dt.now(pytz.timezone('Asia/Kolkata'))
        to_list = ["deeptanshupaul@gmail.com", "paulutkarsh@gmail.com"]
        subject = str("Orders placed as of "+str(now))
        body = "Hi,\nPlease find the order details below: \n"
        for p in profiles:
            text = b.get_orders_status_text(p)
            body = body+text
        e.simple_mail(self.config, to_list, subject, body)
    
    def dump_mail(self, to_list):
        now = dt.now(pytz.timezone('Asia/Kolkata'))
        to_list = to_list
        subject = "Logs dump created at "+str(now)
        body = "Hi,\nPlease find the dump of logs created at "+str(now)+" below:\n"+self.all_logs
        body = body+"\nKind regards, \nDeeptanshu from a tiny cloud somewhere."
        e.simple_mail(self.config, to_list, subject, body)
    
    def refresh(self):
        if self.header is None:
            self.header = "Log file created at "+str(dt.now(pytz.timezone('Asia/Kolkata')))
        f = open(self.log_file_name+".txt", 'w+')
        f.write(self.header)
        f.close()
