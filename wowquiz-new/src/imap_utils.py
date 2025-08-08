import imaplib

def connect_imap(user, password, server):
    imap = imaplib.IMAP4_SSL(server)
    imap.login(user, password)
    imap.select("INBOX")
    return imap

def fetch_unseen_emails(imap):
    status, response = imap.search(None, 'UNSEEN')
    if status != "OK":
        return []
    return response[0].split()

def fetch_email(imap, num):
    status, data = imap.fetch(num, '(RFC822)')
    if status != "OK":
        return None
    return data[0][1]