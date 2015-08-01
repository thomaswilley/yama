yama
==============

yet another mail app

yama syncs couchdb instance with an email inbox (imap)
i.e., enables a local RESTful interface to your email with
a powerful database to use for fun things later.

installation:
---
```bash
$ virtualenv --no-site-packages --distribute -pPython2.7 venv
$ source venv/bin/activate
$ pip install git+https://github.com/balsagoth/imbox
$ pip install -r requirements.txt
```

usage:
---
```bash
$ couchdb
$ source venv/bin/activate
$ python yama.py -imap "imap.gmail.com" -u "you@gmail.com" -p "YOUR_GMAIL_PW" -db "http://127.0.0.1:5984/"
```

Running yama.py should spin thru your imap endpoint (gmail account in
this case) and pull down all messages and sync each one with the local
couchdb instance running at the db endpoint. This means you can visit
your mail locally now by opening your browser to: 
  http://localhost:5984/

Useful local urls:
* /_all_dbs: lists databases (look for messages_<SHA1HASH>, the
  yama-generated db name for this imap endpoint account)
* /messages_<SHA1HASH>/_all_docs: lists all docs (emails) saved in this
  database
* /messages_<SHA1HASH>/<id of doc>: GETs the doc (email) with the given
  id
