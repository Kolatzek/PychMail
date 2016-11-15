# PychMail
Forward emails from foo.com to bar.com without changing content or From field

PychMail is a FetchMail similar software. The main difference is the usage of SMTP authentification for delivery to other server. The second difference isthe usage of config files as python module from config folder. (So you can have more configurations and set more then once receiver in To field by using python lists SMTP_To variable.)

## Example

   You get mails on gmail server. Now you got a message from xyz@yahoo.com and you will forward it to abc@foo.com and abc@bar.com (or only one of them).     You have to authenticate at gmail and make a forward by using SMTP     authentification of gmail. (Two authentifications) The message changes the     from field and the recipients (abc@...) answers to you.     This script will make it for you without changing the From field. So you can     forward the message also to a mailing list manager like ezmlm which will     accept a mail for delivery only if its adress is in To or Cc mail header.

## Configuration

Configuration is a simple python file (.py) in *config* folder. The content is:

```python
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
```

##Usage
```
bash
    ./PychMail.py <config_file_name_without_.py_from_config_folder>
    or
    python3 PychMail.py <config_file_name_without_.py_from_config_folder>
```