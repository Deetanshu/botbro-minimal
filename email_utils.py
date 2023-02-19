# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 15:30:18 2019

@author: Deeptanshu Paul

This file is a Utility file that is used to send emails and create them.

Feature Log:
- Added send_email with basic SSL.
- Added ability to pass a server and multiple messages.
- Added Config object.
- Made basic functions: html_table, default_header, body, table_from_pandas
- Added attachment feature.
- created more hygiene functions: default body, default footer, basicMessage, add_text, add_html
- Phased out SSL and switched to TLS.

To do:
- Make a gmail connector that uses OAuth 2.
- Make the ability to import HTML.
- Make an HTML generation engine.

"""

# Email utility file

#Imports

import email, smtplib, ssl
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
import pandas as pd
import io
import base64

class Config():
    def __init__(self, email_id, password=None, smtp_server = "smtp.gmail.com", port = 587):
        self.email_id=email_id
        self.password=password
        self.smtp_server=smtp_server
        self.port=port

def send_email(config=None, to_list=[], subject="", message="", messages = None, server = None, subjects = None, service = None):
    """
    This function sends a batch of emails/one email depending on the length of to_list. 
    Parameter description:
    config: An object of the Config class that is used to log into the smtp server and send mails.
    to_list: A list of email IDs that are the target email IDs.
    subject: The subject of the email. If left blank, its assumed that the message already has a subject.
    message: An object of MIMEMultipart().
    messages: An array of message objects. If this is None only one message is considered. Note that if the messages array is not of the same size as that of the to_list there may be errors.
    server = an object of smtplib.SMTP_SSL. In the event that this is empty, the config is used to create a server.
    """
    
    if service is not None:
        if subject != "":
            message["Subject"]=subject
        for user in to_list:
            msg = message
            msg['to'] = user
            #msg["from"]=config.email_id
            msg_2 =  {'raw': base64.urlsafe_b64encode(msg.as_string().encode()).decode()}
            message_i = (service.users().messages().send(userId='me', body=msg_2).execute())
            print('Message Id: %s' % message_i['id'])
        return True

    if config is None and server is None:
        print("""[ERROR] Config is none. 
        \t[INFO] Please create a config object as follows: 
        \t>> config = Config(email_id, password, smtp_server, port)
        \t>> send_email(config, to_list, subject, message)
        \tPlease note that the smtp server by default is set to "smtp.gmail.com" and port as 465. 
        \tIn the event that you only intend to send an email to just one person, please pass a LIST as an argument.
        \t>> send_email(config, ["example@gmail.com"], subject, message)""")
        return False
    if server is None:
        
        server = smtplib.SMTP(config.smtp_server, config.port)
        server.starttls()
    
    server.login(config.email_id, config.password)
    if messages is None:
        if subject != "":
            message["Subject"]=subject
        if config is not None:
                message["From"] = "BotBro Info <info.botbro@gmail.com>"
        to_str = ""
        length = len(to_list)
        for x in range(length):
            if x != (length-1):
                to_str = to_str + to_list[x] +','
            else:
                to_str = to_str + to_list[x]
        message["To"] = to_str
        server.sendmail(config.email_id, to_list, message.as_string())
    else:
        for x in range(len(to_list)):
            if subjects is not None:
                messages[x]["Subject"] = subjects[x]
            if config is not None:
                messages[x]["From"] = config.email_id
            messages[x]["To"] = to_list[x]
            server.sendmail(config.email_id, to_list[x], messages[x].as_string)
    return True

def simple_mail(config, to_list, subject="", body=""):
    message=basicMessage()
    message=add_text(message, body)
    message["Subject"]=subject
    return send_email(config = config, to_list = to_list, message = message)

def html_table(table, isHeader = False, style = None, header_names = None):
    """
    This function creates a table in HTML.
    Returns two strings:
    1. style = style tag for the table.
    2. tr = the table built
    """
    if style is None:
        style = """
        <style>
        table {
            font-family: arial, sans-serif;\n
            width: 100%;\n
            border-collapse: collapse;\n
        }
        td, th{
            border: 1px solid #dddddd;\n
            text-align: left;\n
        }
        </style>"""
    
    tr = """\
    <table>"""
    
    for row in table:
        if row is None:
            continue
        tr = tr+ """<tr>"""

        for col in row:
            if isHeader:
                if header_names is None:
                    tr = tr+"""\n<th>"""+str(col)+"""</th>"""
                else:
                    tr = tr+"""\n<th>"""+header_names[col]+"""</th>"""
            else:
                tr = tr+"""\n<td>"""+str(col)+"""</td>"""
        if isHeader:
            isHeader = False
        tr = tr+"""\n</tr>"""
    tr = tr + """\n</table>"""

    return style, tr

def default_header(style = "", title = ""):
    header = """\
    <html>
    <head>
    """+title+style+"""</head>"""
    return header

def body(content=[]):
    bodytext = """<body>"""
    for c in content:
        bodytext = bodytext + c
    bodytext = bodytext + """</body>"""
    return bodytext

def table_from_pandas(dataf, limit=100, header_names=None):
    """
    If the dataframe is > 100 lines, it stops there.
    """
    df = dataf[:limit] if len(dataf)>limit else dataf 
    temp = [None, None]
    temp[0] = df.columns.values.tolist()
    values = df.values.tolist()
    for value in values:
        temp.append(value)
    return html_table(temp, True, header_names = header_names)

def attachment(message, filename, filepath = None):
    """
    This should be the last thing added to the email.
    """
    if filepath is None:
        filepath = filename
    with open(filepath, 'rb') as attach:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attach.read())
    
    encoders.encode_base64(part)
    part.add_header("content-Disposition",f"attachment; filename={filename}")
    message.attach(part)
    return message

def default_body(content):
    return "<body>"+content+"</body>"

def default_footer():
    return "</html>"

def basicMessage():
    message = MIMEMultipart('mixed')
    return message

def add_text(message, text):
    part = MIMEText(text, "plain")
    message.attach(part)
    return message

def add_html(message, html):
    part = MIMEText(html, "html")
    message.attach(part)
    return message

def attach_df_csv(message, df, filename):
  with io.StringIO() as buffer:
    df.to_csv(buffer)
    attachment = MIMEApplication(buffer.getvalue())
    attachment['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    message.attach(attachment)
    return message
    
def attach_df_excel(message, df, filename):
  with io.BytesIO() as buffer:
    writer = pd.ExcelWriter(buffer)
    df.to_excel(writer)
    writer.save()
    attachment = MIMEApplication(buffer.getvalue())
    attachment['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    message.attach(attachment)
    return message
