#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PychMail is a FetchMail similar software. The main difference is the usage of 
SMTP authentification for delivery to other server. The second difference is
the usage of config files as python module from config folder. (So you can have
more configurations and set more then once receiver in To field by using 
python lists SMTP_To variable.)

Example:

    You get mails on gmail server. Now you got a message from xyz@yahoo.com and 
    you will forward it to abc@foo.com and abc@bar.com (or only one of them).
    You have to authenticate at gmail and make a forward by using SMTP 
    authentification of gmail. (Two authentifications) The message changes the 
    from field and the recipients (abc@...) answers to you. 
    This script will make it for you without changing the From field. So you can
    forward the message also to a mailing list manager like ezmlm which will 
    accept a mail for delivery only if its adress is in To or Cc mail header.

Configuration:

    IMAP4_SSL_Server = IMAP server host name
    IMAP_User = IMAP user name
    IMAP_Password = IMAP user password
    IMAP_Folder = IMAP folder to check

    SMTP_Server = SMTP server host name
    SMTP_Port = SMTP port
    SMTP_Debugevel = debug level for SMTP
    SMTP_User = SMTP user name
    SMTP_Password = SMTP user password
    SMTP_To = receiver of the forwarded message ["abc@foo.com", 'abc@bar.com'] or simply "abc@foo.com"
    SMTP_From = email address of the SMTP user

Usage:

    ./PychMail.py <config_file_name_without_.py_from_config_folder>
    oder
    python3 PychMail.py <config_file_name_without_.py_from_config_folder>
"""
__author__ = "Robert Kolatzek"
__copyright__ = "Copyright 2016, Robert Kolatzek"
__license__ = "GPL"
__version__ = "1.0"

from imaplib import IMAP4_SSL
from smtplib import SMTP
import email, sys, importlib
from email.mime.text import MIMEText
from email.parser import Parser
from email.utils import *


if len(sys.argv) < 2:
    print ('One argument is expected: the name of the configuration (filename without .py from config folder).')
    sys.exit()
    
config = importlib.import_module('config.'+sys.argv[1])

def connectImap(IMAP4_SSL_Server, IMAP_User, IMAP_Password, IMAP_Folder):
    """
    Make a connection to the IMAP Server and select the folder 
    
    Args:
        IMAP4_SSL_Server (string): host name of the IMAP server
        IMAP_User (string): name of the IMAP user for authentification
        IMAP_Password (string): password of the IMAP user for authentification
        IMAP_Folder (string): name of the IMAP folder to retrive the messages
        
    Returns:
        obj: IMAP4_SSL connection object
    """
    conn = IMAP4_SSL(IMAP4_SSL_Server)
    conn.login(IMAP_User, IMAP_Password)
    conn.select(IMAP_Folder, False)
    return conn

def disconnectImap(conn):
    """
    Close given IMAP connection
    
    Args:
        conn (obj): IMAP connection object
        
    Returns:
        void
    """
    conn.logout()
    
def connectSmtp(SMTP_Server, SMTP_User, SMTP_Port, SMTP_Password, SMTP_Debugevel):
    """
    Create a SMTP connection
    
    Args:
        SMTP_Server (string): SMTP host name
        SMTP_User (string): SMTP user name for authentification
        SMTP_Port (int): SMTP port number
        SMTP_Password (string): SMTP user password for authentification
        SMTP_Debugevel (int): Level of debug messages
    
    Returns:
        SMTP: connection object 
    """
    server = SMTP(SMTP_Server, SMTP_Port)
    server.ehlo()
    server.set_debuglevel(SMTP_Debugevel)
    server.starttls()
    server.ehlo()
    server.login(SMTP_User, SMTP_Password)
    return server

def disconnectSmtp(server):
    """
    Close given SMTP connection
    
    Args:
        server (obj): SMTP connection object
        
    Returns:
        void
    """
    server.quit()

def setHeader(mail, SMTP_To, SMTP_From):
    """
    Set the right header in the mail to be compatible with the RFC822 
    and to forward to the destination address.
    
    Args:
        mail (obj): mail object
        SMTP_To (string): the address of the new destination
        SMTP_From (string): the sender address corresponding to the SMTP authentification
        
    Returns:
        obj: mail with new headers
    """
    
    """
    Set the destination address. If "To" was missing, set it instead of replacing / KeyError-catch. 
    The right "To" address is importand for mailing lists managers like ezmlm or mailman
    """
    try:
        mail.replace_header('To', SMTP_To)
    except KeyError:
        mail.add_header('To', SMTP_To)
    """
    Sender is the mail account responsible for sending the message. It overwrites the From field for 
    check at the destination MDA if the sending MTA and the sending account (address) are corresponding 
    to each other. In other words: If you send a mail from yahoo.com with From linke ...@microsoft.com 
    you are probably a spamer and will be not able to deliver youre mail - but with 
    "Sender: ...@yahoo.com" it should be accepted.
    See also: 4.4.2. SENDER / RESENT-SENDER in https://www.w3.org/Protocols/rfc822/
    """
    try:
        mail.replace_header('Sender', SMTP_From)
    except KeyError:
        mail.add_header('Sender', SMTP_From)
    return mail
    
# connect to IMAP
imapConn = connectImap(config.IMAP4_SSL_Server, config.IMAP_User, config.IMAP_Password, config.IMAP_Folder)
# search for any mail in the connected IMAP folder
typ, data = imapConn.search(None, 'ALL')
# connect to SMTP (MTA)
smtpConn = connectSmtp(config.SMTP_Server, config.SMTP_User, config.SMTP_Port, config.SMTP_Password, config.SMTP_Debugevel)

for num in data[0].split():
    typ, msgdata = imapConn.fetch(num, '(RFC822)')
    msg = msgdata[0][1]
    mail = email.message_from_bytes(msg)
    From = mail.get_all('From')
    To = mail.get_all('To')
    # if SMTP_To is a list make a copy of the mail to each receiver and send it
    if isinstance(config.SMTP_To, list):
        for SMTP_To_One in config.SMTP_To:
            newmail = setHeader(mail, SMTP_To_One, config.SMTP_From)
            smtpConn.sendmail(config.SMTP_From, SMTP_To_One, newmail.as_string())
    else:
        mail = setHeader(mail, config.SMTP_To, config.SMTP_From)
        smtpConn.sendmail(config.SMTP_From, config.SMTP_To, mail.as_string())
    # mark this mail as to be deleted
    imapConn.store(num, '+FLAGS', '\\Deleted')
    # remove alls messages with the "Deleted" flag 
    imapConn.expunge()
    print('Email from {} to {} copied to {} and deleted'.format(From, To, config.SMTP_To))

disconnectImap(imapConn)
disconnectSmtp(smtpConn)

