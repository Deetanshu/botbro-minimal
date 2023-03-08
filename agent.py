"""
Interpretation Agent v1
Basic features:
1. Ability to store events
2. Different types of events
"""

import connector_v2 as conn 
import email_utils as email
import logger 

class Agent():
    def __init__(self, module_name, override_config = None):
        self.module_name = module_name
        self.connection = None
        self.email_address = "deeptanshupaul@gmail.com"
        self.tables = {'action': 'botbro.action',
                        'error': 'botbro.error',
                        'next_up': 'botbro.next_up',
                        'price_watch': 'botbro.price_watch',
                        'trade': 'botbro.trade',
                        'price_action': 'botbro.price_action'
                        }
        self.logger = logger.Logger("Agent")
        self.config = email.Config("info.botbro@gmail.com", "bqkbdousbipsbfhu")
        self.override_config = override_config
        if override_config = None:
            self.connection = conn.sql_connector("mysql", "root", "Deeptanshu97007", "34.93.184.62", 3306, "botbro")
        else:
            self.connection = conn.sql_connector(override_config.db_type, override_config.username, override_config.password, override_config.ip, override_config.port, override_config.dbname)
    
    def create_connector(self):
        try:
            if self.override_config is None:
                return conn.sql_connector("mysql", "root", "Deeptanshu97007", "34.93.184.62", 3306, "botbro")
            else:
                return conn.sql_connector(override_config.db_type, override_config.username, override_config.password, override_config.ip, override_config.port, override_config.dbname)
        except Exception as e:
            self.error_mail("Create Connection for Agent", e)
            self.logger.fwrite(str("Attempted to send error mail for exception "+str(e)))
            self.create_connector()


    def error_mail(self, location, exception):
        try:
            subject = "BOTBRO error at "+location
            message = """
            Hi Deeptanshu,
            
            I messed up, the exception that occurred is at """+location+""" and the exception that occurred is """+str(exception)+"""
            
            Pls help,
            BotBro"""

            email.simple_mail([self.email_address], subject, message)
        except Exception as e:
            log_msg = "Error in sending error mail with exception: "+str(e)
            self.logger.fwrite(log_msg)


    def action(self, function, action, description=""):
        try:
            query_string = "insert into "+self.tables['action']+" values (\""+self.module_name+"\", now(), \""+function+"\", \""+action+"\", \""+description+"\");"
            self.connection.execute(query_string)
        except Exception as e:
            self.error_mail("Action insert", e)
            self.logger.fwrite(str("Attempted to send error mail for exception "+str(e)))
    
    def next_up(self, function, action, description=""):
        try:
            query_string = "insert into "+self.tables['next_up']+" values (\""+self.module_name+"\", now(), \""+function+"\", \""+action+"\", \""+description+"\");"
            self.connection.execute(query_string)
        except Exception as e:
            self.error_mail("Next Up insert", e)
            self.logger.fwrite(str("Attempted to send error mail for exception "+str(e)))
    
    def price_watch(self, symbol, price, strategy_name):
        try:
            query_string = 'insert into '+self.tables['price_watch']+' values ("'+self.module_name+'", now(), "'+symbol+'", '+price+', "'+strategy_name+'");'
            self.connection.execute(query_string)
        except Exception as e:
            self.error_mail("Price watch insert", e)
            self.logger.fwrite(str("Attempted to send error mail for exception "+str(e)))
    
    def trade(self, account_name, strategy_name, trade_type, isMarket, price, orderid):
        try:
            query_string = 'insert into '+self.tables['trade']+' values ("'+self.module_name+'", now(), "'+account_name+'", "'+strategy_name+'", "'+trade_type+'", '+isMarket+', '+price+', "'+orderid+'");'
            self.connection.execute(query_string)
        except Exception as e:
            self.error_mail("Trade insert", e)
            self.logger.fwrite(str("Attempted to send error mail for exception "+str(e)))
    
    def price_action(self, symbol, price, strategy_name, action):
        try:
            query_string = 'insert into '+self.tables['price_action']+' values ("'+self.module_name+'", now(), "'+symbol+'", '+price+', "'+strategy_name+'", "'+action+'");'
            self.connection.execute(query_string)
        except Exception as e:
            self.error_mail("Price action insert", e)
            self.logger.fwrite(str("Attempted to send error mail for exception "+str(e)))
    
    def error(self, function, description, error_type):
        try:
            query_string = 'insert into '+self.tables['error']+' values ("'+self.module_name+'", now(), "'+function+'", "'+description+'", "'+error_type+'");'
            self.connection.execute(query_string)
        except:
            print("Error in logging error")
            self.error_mail("Error insert", e)
