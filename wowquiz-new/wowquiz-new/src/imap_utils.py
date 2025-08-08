import imaplib

def connect_imap(user, password, server):
    imap = imaplib.IMAP4_SSL(server)
    imap.login(user, password)
    return imap

def fetch_unseen_emails(imap):
    imap.select("INBOX")
    typ, msgs = imap.search(None, "UNSEEN")
    if typ != "OK":
        return []
    ids = msgs[0].split()
    return ids

def fetch_email(imap, num):
    typ, msg_data = imap.fetch(num, "(RFC822)")
    if typ != "OK" or not msg_data[0] or not msg_data[0][1]:
        return None
    return msg_data[0][1]