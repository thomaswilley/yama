import argparse
from imbox import Imbox
from getpass import getpass
import couchdb
import sha
import json
import pdb

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

    return obj

def sync_message_with_couchdb(message_uid, message, db):
    # hackishly try to seralize across a couple unicode encodings
    try:
        json_message = json.dumps(message.__dict__, default=default, encoding="utf-8")
    except:
        try:
            json_message = json.dumps(message.__dict__, default=default, encoding="ISO-8859-1")
        except:
            pass
    if not json_message:
        print "failed to seralize message %s" % message_uid
        return None

    dict_message = json.loads(json_message)
    dict_message['_id'] = message_uid

    try:
        id, rev = db.save(dict_message, _id=message_uid)
    except couchdb.http.ResourceConflict:
        print "message %s already exists, skipping" % message_uid
        return None

    return (id, rev)

def sync(imap_endpoint, couchdb_endpoint, username, password):
    # https://pythonhosted.org/CouchDB/getting-started.html
    # assumes couchdb is running prior to running this...
    couch = couchdb.Server(couchdb_endpoint)
    dbname = 'messages_%s' % sha.sha(username).hexdigest()
    db = None
    try:
        db = couch[dbname]
    except:
        db = couch.create(dbname) # db didn't exist so create

    # https://github.com/martinrusev/imbox
    # note: using fresher fork: https://github.com/balsagoth/imbox
    imbox = Imbox(imap_endpoint, username=username, password=password, ssl='SSL')

    # todo: sync point (set from_date to) day prior to most recent day stored in db
    from_date = '14-Apr-2013'
    all_messages = imbox.messages(date__gt=from_date)

    print "syncing messages to couch db [%s]" % db

    for uid, message in all_messages:
        print uid, message.subject, sync_message_with_couchdb(uid, message, db)

def deletedb(couchdb_endpoint, username):
    couch = couchdb.Server(couchdb_endpoint)
    dbname = 'messages_%s' % sha.sha(username).hexdigest()
    print couch.delete(dbname) # db didn't exist so create

def main():
    parser = argparse.ArgumentParser(
            description='sync mail account to couchdb'
            )
    parser.add_argument('-imap', metavar="imap_endpoint",
            type=str, help='url to imap endpoint', required=True)
    parser.add_argument('-u', metavar="imap_username",
            type=str, help='imap username (typically email address)', required=True)
    parser.add_argument('-p', metavar="imap_password",
            type=str, help='imap password for username', required=True)
    parser.add_argument('-db', metavar="couchdb_endpoint",
            type=str, help='url to couchdb endpoint', required=True)
    parser.add_argument('-deletedb',
            action='store_true',
            default=False,
            help='will DELETE the local couchdb database associated with this account')

    args = parser.parse_args()

    if args.deletedb:
        deletedb(args.db, args.u)
    else:
        sync(args.imap, args.db, args.u, args.p)

if __name__ == "__main__":
    main()
