from imbox import Imbox
from getpass import getpass
import couchdb
import sha
import json
import pdb

imap_server = raw_input('imap url: ')
username = raw_input('username: ')
password = getpass('password [%s]: ' % username)

def default(obj):
    """Default JSON serializer."""
    import calendar, datetime

    if isinstance(obj, datetime.datetime):
        if obj.utcoffset() is not None:
            obj = obj - obj.utcoffset()
        millis = int(
            calendar.timegm(obj.timetuple()) * 1000 +
            obj.microsecond / 1000
        )
        return millis
    if isinstance(obj, set):
        return list(obj)

    #pdb.set_trace()
    return obj.__dict__

def sync_message_with_couchdb(message_uid, message, db):
    json_message = json.dumps(message, default=default)

    #pdb.set_trace()
    return db.save(json_message, _id=message_uid)

# https://pythonhosted.org/CouchDB/getting-started.html
# assumes couchdb is running prior to running this...
couch = couchdb.Server('http://127.0.0.1:5984/')
db = 'messages_%s' % sha.sha(username).hexdigest()
couchdb = None
try:
    couchdb = couch[db]
except:
    couchdb = couch.create(db) # db didn't exist so create

# https://github.com/martinrusev/imbox
# note: using fresher fork: https://github.com/balsagoth/imbox
imbox = Imbox(imap_server, username=username, password=password, ssl='SSL')

# todo: sync point (set from_date to) day prior to most recent day stored in db
from_date = '14-Apr-2013'
all_messages = imbox.messages(date__gt=from_date)

print "syncing messages to couch db [%s]" % db
for uid, message in all_messages:
    print uid, message.subject, sync_message_with_couchdb(uid, message, couchdb)
