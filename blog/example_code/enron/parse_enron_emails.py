from __future__ import annotations
import pathlib
import email
import email.message
import doctable
import datetime
import dataclasses
import dateutil.parser
import pprint
import sqlalchemy

@dataclasses.dataclass
class Email:
    id: int
    path: str
    message_id: str 
    date: datetime.datetime 
    frm: str 
    to: str 
    subject: str 
    cc: str 
    mime_version: str 
    content_type: str 
    content_transfer_encoding: str 
    bcc: str 
    x_frm: str 
    x_to: str 
    x_cc: str 
    x_bcc: str 
    x_folder: str 
    x_origin: str 
    x_file_name: str 
    body: str 
    
    @classmethod
    def from_message(cls, msg: email.message.Message, fp: pathlib.Path) -> Email:
        return cls(
            id = None,
            path = str(fp),
            message_id=msg.get('Message-ID'),
            date=dateutil.parser.parse(msg.get('Date')),
            frm=msg.get('From'),
            to=msg.get('To'),
            subject=msg.get('Subject'),
            cc=msg.get('Cc'),
            mime_version=msg.get('MIME-Version'),
            content_type=msg.get('Content-Type'),
            content_transfer_encoding=msg.get('Content-Transfer-Encoding'),
            bcc=msg.get('Bcc'),
            x_frm=msg.get('X-From'),
            x_to=msg.get('X-To'),
            x_cc=msg.get('X-cc'),
            x_bcc=msg.get('X-bcc'),
            x_folder=msg.get('X-Folder'),
            x_origin=msg.get('X-Origin'),
            x_file_name=msg.get('X-FileName'),
            body=msg.get_payload(),
        )
        
    def info(self) -> dict[str, str]:
        info = dataclasses.asdict(self)
        if 'body' in info:
            del info['body']
        return info
    

if __name__ == '__main__':
    root = pathlib.Path('maildir/')
    
    import sqlite3
    #con = sqlite3.connect("db/v1_enron.db")
    engine = sqlalchemy.create_engine('sqlite:///db/v1_enron.db')
    
    with engine.connect() as conn:
        result = conn.execute('SELECT * FROM emails')
    
    cur = con.cursor()
    cur.execute('DROP TABLE IF EXISTS emails')
    cur.execute('''CREATE TABLE IF NOT EXISTS emails(
        id INTEGER PRIMARY KEY, 
        path TEXT, 
        message_id TEXT, 
        date DATETIME, 
        frm TEXT, 
        to TEXT, 
        subject TEXT, 
        cc TEXT, 
        mime_version TEXT, 
        content_type TEXT, 
        content_transfer_encoding TEXT, 
        bcc TEXT, 
        x_frm TEXT, 
        x_to TEXT, 
        x_cc TEXT, 
        x_bcc TEXT, 
        x_folder TEXT, 
        x_origin TEXT, 
        x_file_name TEXT, 
        body TEXT
    )''')
    
    email_files = [fp for fp in root.rglob('*') if fp.is_file()]
    for ef in email_files:
        with ef.open('r') as f:
            msg = email.message_from_file(f)
            print(msg.keys())
            emsg = Email.from_message(msg, fp=ef.relative_to(root))
            pprint.pprint(emsg.info())




