import argparse
from imbox import Imbox
from getpass import getpass
import couchdb
import sha
import json
import pdb
import StringIO
import base64

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

    if isinstance(obj, StringIO.StringIO):
        b64_obj = base64.b64encode(obj.read())
        return b64_obj

    if isinstance(obj, set):
        return list(obj)

    return obj

def sync_message_with_couchdb(message_uid, message, db):
    # hackishly try to seralize across a couple unicode encodings
    json_message = None
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

    # peel off the attachments, sort of annoying but seems they must follow
    #   the couchdb attachments api, will be available again at doc._attachments
    attachments = dict_message['attachments']
    del dict_message['attachments']

    try:
        doc_id, doc_rev = db.save(dict_message, _id=message_uid)
        # if there were attachments, save them now
        if attachments:
            doc = db[doc_id]
            # save each attachment under doc._attachments
            for attachment in attachments:
                a_id = db.put_attachment(doc,
                        StringIO.StringIO(
                            base64.b64decode(attachment['content'])
                            ),
                        filename=attachment['filename'],
                        content_type=attachment['content-type'])
                print a_id
    except couchdb.http.ResourceConflict:
        print "message %s already exists, skipping" % message_uid
        return None

    return (doc_id, doc_rev)

def sync(imap_endpoint, couchdb_endpoint, username, password, from_date, starttls=False):
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
    imap_server = imap_endpoint
    imap_port = None
    imbox = None
    ssl = 'SSL'
    if starttls:
        ssl = 'STARTTLS'
    try:
        imap_server, imap_port = imap_endpoint.split(":")
        imbox = Imbox(imap_server, port=imap_port, username=username, password=password, ssl=ssl)
    except:
        imbox = Imbox(imap_server, username=username, password=password, ssl=ssl)

    # todo: sync point (set from_date to) day prior to most recent day stored in db
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
    parser.add_argument('-fromdt', metavar="from_date",
            type=str, help='sync on/after this datetime, e.g., 28-Apr-2014', required=True)
    parser.add_argument('-starttls',
            action='store_true',
            default=False,
            help='use SSL/STARTTLS, e.g., working with exchange imap')
    parser.add_argument('-deletedb',
            action='store_true',
            default=False,
            help='will DELETE the local couchdb database associated with this account')

    args = parser.parse_args()

    if args.deletedb:
        deletedb(args.db, args.u)
    else:
        sync(args.imap, args.db, args.u, args.p, args.fromdt, args.starttls)

if __name__ == "__main__":
    main()
