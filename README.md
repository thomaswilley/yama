=======
yama
====

yet another mail app

work in progres

syncs a local db (probably couchdb) instance with an email inbox (imap)
i.e., enables a local RESTful interface to plain remote email with
a powerful database to use for fun things later.

---
install:
---

```bash
virtualenv --no-site-packages --distribute -pPython2.7 venv
source venv/bin/activate
pip install git+https://github.com/balsagoth/imbox
pip install -r requirements.txt
```

---
usage:
---
```bash
couchdb
source venv/bin/activate
python yama.py -imap "imap.gmail.com" -u "you@gmail.com" -p
"YOUR_GMAIL_PW" -db "http://127.0.0.1:5984/"
```
