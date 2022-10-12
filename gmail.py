
from bs4 import BeautifulSoup
import os
import imaplib
import email

imap_host = 'imap.gmail.com'
imap_user = os.getenv('GOOGLE_USER')
imap_pass = os.getenv('GOOGLE_PASSWORD')
imap = imaplib.IMAP4_SSL(imap_host)
imap.login(imap_user, imap_pass)
imap.select('Inbox')

def get_messages(sender, exclude = None):
    print('Gmail imap: getting messages for {sender}'.format(sender=sender))
    imap.literal = u'from:{sender} newer_than:2d in:inbox transacción {exclude}'.format(sender=sender, exclude='-' + exclude if exclude else '').encode('utf-8')
    response, data = imap.uid('SEARCH', 'CHARSET', 'UTF-8', 'X-GM-RAW')
    if response != 'OK':
        print('Gmail imap: No gmail messages found')
        return
    return data[0].split()

def get_message(msg_id):
    print('Gmail imap: getting message with id {msg_id}'.format(msg_id=msg_id))
    response, data=imap.fetch(msg_id,'(RFC822)')
    msg = email.message_from_bytes(data[0][1])
    content = msg.get_payload(decode=True).decode(msg.get_content_charset()).encode('utf-8')
    message = BeautifulSoup(content, 'html.parser')
    return message
