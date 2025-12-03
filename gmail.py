
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

def get_messages(sender, retries=3):
    print('Gmail imap: getting messages for {sender}'.format(sender=sender))
    for attempt in range(retries):
        try:
            imap.literal = f'from:({sender}) newer_than:1d in:inbox'.encode('utf-8')
            response, data = imap.uid('SEARCH', 'CHARSET', 'UTF-8', 'X-GM-RAW')
            if response != 'OK':
                print('Gmail imap: No gmail messages found')
                return
            print(f'Gmail imap: messages for {sender} -> {data}')
            return data[0].split()
        except imaplib.IMAP4.abort as e:
            print(f'Attempt {attempt + 1} failed: {e}. \nRetrying...')
    print('Max retries reached. Exiting.')
    return

def get_message(msg_id, retries=3):
    print('Gmail imap: getting message with id {msg_id}'.format(msg_id=msg_id))
    for attempt in range(retries):
        try:
            response, data = imap.uid('FETCH', msg_id, '(RFC822)')
            msg = email.message_from_bytes(data[0][1])
            # Check if the message is multipart
            if msg.is_multipart():
                # Iterate through the parts to find the text/plain or text/html part
                for part in msg.walk():
                    if part.get_content_type() == 'text/html':
                        charset = part.get_content_charset() or 'utf-8'
                        content = part.get_payload(decode=True).decode(charset, errors='replace').encode('utf-8')
                        break
                else:
                    # Fallback if no HTML part is found
                    charset = msg.get_content_charset() or 'utf-8'
                    content = msg.get_payload(decode=True).decode(charset, errors='replace').encode('utf-8')
            else:
                charset = msg.get_content_charset() or 'utf-8'
                content = msg.get_payload(decode=True).decode(charset, errors='replace').encode('utf-8')
            message = BeautifulSoup(content, 'html.parser')
            return message
        except imaplib.IMAP4.abort as e:
            print(f'Attempt {attempt + 1} failed: {e}. \nRetrying...')
    print('Max retries reached. Exiting.')
    return
