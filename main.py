import StringIO
import json
import logging
import random
import yaml
import urllib
import urllib2

# for sending images
from PIL import Image
import multipart

# read person data
import csv

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

import requests
import requests_toolbelt.adapters.appengine

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()

# Dropbox
#import dropbox

try:
    with open('config.yaml', 'r') as cfgstream:
        config = yaml.load(cfgstream)
except yaml.YAMLError as e:
    logging.error("config.yaml is required, please see README.md")
    raise

TOKEN = config['bot-token']
dropboxAccessToken = config['dropboxAccessToken']
dropboxFolder = config['dropboxFolder']
# logging.info('bot-token: %s' % TOKEN)

BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'


# ================================

class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)


# ================================

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()

def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False


# ================================

class Person(ndb.Model):
    position = ndb.IntegerProperty()
    orientationGroup = ndb.StringProperty()
    name = ndb.StringProperty()
    nickName = ndb.StringProperty()
    internalJobTitle = ndb.StringProperty()
    groupName = ndb.StringProperty()
    regCode = ndb.StringProperty()
    gender = ndb.StringProperty()
    originCity = ndb.StringProperty()
    originProvince = ndb.StringProperty()
    originStreet = ndb.StringProperty()
    ethnicity = ndb.StringProperty()
    marriageStatus = ndb.StringProperty()
    birthPlace = ndb.StringProperty()
    birthDate = ndb.StringProperty()
    citizenId = ndb.StringProperty()
    mobileNumber = ndb.StringProperty()
    whatsappNumber = ndb.StringProperty()
    email = ndb.StringProperty()
    lineId = ndb.StringProperty()
    twitterScreenName = ndb.StringProperty()
    instagramScreenName = ndb.StringProperty()
    currentCity = ndb.StringProperty()
    currentProvince = ndb.StringProperty()
    currentStreet = ndb.StringProperty()
    jobTitle = ndb.StringProperty()
    resignDate = ndb.StringProperty()
    prevProgramSchool = ndb.StringProperty()
    prevProgramCountry = ndb.StringProperty()
    prevProgramCity = ndb.StringProperty()
    prevProgramName = ndb.StringProperty()
    nextProgramSchool = ndb.StringProperty()
    nextProgramCountry = ndb.StringProperty()
    nextProgramCity = ndb.StringProperty()
    nextProgramName = ndb.StringProperty()
    scholarshipKind = ndb.StringProperty()
    admissionDate = ndb.StringProperty()
    expectedGraduationDate = ndb.StringProperty()
    departureDate = ndb.StringProperty()
    visaStatus = ndb.StringProperty()

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


class ExportPersonHandler(webapp2.RequestHandler):
    def get(self):
        q = Person.query()
        rows = []
        for person in q.fetch(5):
            rows.append(person)
        logging.info("Persons: %s" % rows)
        self.response.headers['Content-Type'] = 'text/plain'   
        self.response.write(rows)

class WhoisHandler(webapp2.RequestHandler):
    def get(self):
        q = self.request.get('q').lower()
        if len(q) < 4:
            raise RuntimeError("Search term must be at least 4 characters")
        query = Person.query()
        rows = []
        resp_string = ""
        for person in query.fetch(200):
            if q in person.name.lower():
                rows.append(person)
                logging.info("Matched Person: %s" % person)
                s = """{name}
Kelompok: {groupName}
No. Reg: {regCode}
Jenis Kelamin: {gender}
Asal: {originCity}, {originProvince}
Status: {marriageStatus}
Kelahiran: {birthPlace}, {birthDate}
No. HP: {mobileNumber} / {whatsappNumber}
Email: {email}
Line: {lineId}
Twitter: {twitterScreenName}
Instagram: {instagramScreenName}
Domisili: {currentCity}, {currentProvince}
Pekerjaan: {jobTitle}
Universitas Asal: {prevProgramName}, {prevProgramSchool}, {prevProgramCity}, {prevProgramCountry}
Universitas Tujuan: {nextProgramName}, {nextProgramSchool}, {nextProgramCity}, {nextProgramCountry}
Beasiswa: {scholarshipKind}""".format(**person.to_dict())
                resp_string += s + "\n\n"
        self.response.headers['Content-Type'] = 'text/plain'   
        self.response.write(resp_string)

class ImportPersonHandler(webapp2.RequestHandler):
    def post(self):
        # person_keys = Person.all(keys_only=True).fetch(1000)
        # logging.info('Deleting all Person: %s' % person_keys)
        # ndb.delete(person_keys)

        csvs = self.request.get('csv')
        csvf = StringIO.StringIO(csvs)
        # logging.info(csvs)
        reader = csv.reader(csvf)
        next(reader) # skip header
        logging.info('Importing Person ...')
        my_list = list(reader)
        resp = {"csv": []}
        for row in my_list:
            person = Person(
#                 position=row[0],
                orientationGroup=row[1],
                name=row[2], 
                nickName=row[3],
                internalJobTitle=row[4],
                groupName=row[5],
                regCode=row[6],
                gender=row[7],
                originCity=row[8],
                originProvince=row[9],
                originStreet=row[10],
                ethnicity=row[11],
                marriageStatus=row[12],
                birthPlace=row[13],
                birthDate=row[14],
                citizenId=row[15],
                mobileNumber=row[16],
                whatsappNumber=row[17],
                email=row[18],
                lineId=row[19],
                twitterScreenName=row[20],
                instagramScreenName=row[21],
                currentCity=row[22],
                currentProvince=row[23],
                currentStreet=row[24],
                jobTitle=row[25],
                resignDate=row[26],
                prevProgramSchool=row[27],
                prevProgramCountry=row[28],
                prevProgramCity=row[29],
                prevProgramName=row[30],
                nextProgramSchool=row[31],
                nextProgramCountry=row[32],
                nextProgramCity=row[33],
                nextProgramName=row[34],
                scholarshipKind=row[35],
                admissionDate=row[36])
            logging.info("Adding: %s" % person)
            person.put()
        logging.info("Added all Person")
        self.response.write(json.dumps(resp))


def dropbox_search(q):
    logging.info("Searching Dropbox for '%s' ..." % q)
    # http://stackoverflow.com/a/36938507/122441
    args = {
        'path': dropboxFolder,
        'query': q,
        'max_results': 10,
        'mode': 'filename'
    }

    headers = {
        'Authorization': 'Bearer {}'.format(dropboxAccessToken),
        #'Dropbox-API-Arg': json.dumps(args),
        'Content-Type': 'application/json',
    }

    urlfetch.set_default_fetch_deadline(60)
    request = urllib2.Request('https://api.dropboxapi.com/2/files/search', 
        json.dumps(args), headers)
    searchResults = json.load(urllib2.urlopen(request))
    logging.info("Searching Dropbox for '%s' returned %s matches" % (q, len(searchResults['matches'])))
    return searchResults

class DropboxSearchHandler(webapp2.RequestHandler):
    def get(self):
        q = self.request.get('q').lower()
        searchResults = dropbox_search(q)

        # dbx = dropbox.Dropbox(dropboxAccessToken)
        # user = dbx.users_get_current_account()
        # logging.info("Dropbox User: %s" % user)
        # files = dbx.files_search(dropboxFolder, q, max_results=10)

        # self.response.headers['Content-Type'] = 'application/json'
        logging.debug(json.dumps(searchResults))   
        # self.response.write(json.dumps(searchResults))

        s = ""
        i = 0
        for match in searchResults['matches']:
            i = i + 1
            s += "{}. {}\n".format(i, match['metadata']['path_display'].replace(dropboxFolder, "", 1))
        self.response.headers['Content-Type'] = 'text/plain'   
        self.response.write(s)

class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        update_id = body['update_id']
        try:
            message = body['message']
        except:
            message = body['edited_message']
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
        fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']

        if not text:
            logging.info('no text')
            return

        def reply(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg.encode('utf-8'),
                    'disable_web_page_preview': 'true',
                    'reply_to_message_id': str(message_id),
                })).read()
            elif img:
                resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
                    ('chat_id', str(chat_id)),
                    ('reply_to_message_id', str(message_id)),
                ], [
                    ('photo', 'image.jpg', img),
                ])
            else:
                logging.error('no msg or img specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        if text.startswith('/'):
            if text == '/start':
                reply('Bot enabled')
                setEnabled(chat_id, True)
            elif text == '/stop':
                reply('Bot disabled')
                setEnabled(chat_id, False)
            elif text == '/image':
                img = Image.new('RGB', (512, 512))
                base = random.randint(0, 16777216)
                pixels = [base+i*j for i in range(512) for j in range(512)]  # generate sample image
                img.putdata(pixels)
                output = StringIO.StringIO()
                img.save(output, 'JPEG')
                reply(img=output.getvalue())
            elif text.startswith('/whois ') or text.startswith('/whois@'):
                splitted = text.split(' ', 1)
                if len(splitted) >= 2:
                    q = splitted[1].lower()
                    if len(q) < 3:
                        reply("Search term must be at least 3 characters")
                    else:
                        query = Person.query()
                        rows = []
                        for person in query.fetch(200):
                            if q in person.name.lower():
                                rows.append(person)
                                logging.debug("Matched person: %s" % person)
                        for person in rows:
                            s = """{name}
Kelompok: {groupName}
No. Reg: {regCode}
Jenis Kelamin: {gender}
Asal: {originCity}, {originProvince}
Status: {marriageStatus}
Kelahiran: {birthPlace}, {birthDate}
No. HP: {mobileNumber} / {whatsappNumber}
Email: {email}
Line: {lineId}
Twitter: {twitterScreenName}
Instagram: {instagramScreenName}
Domisili: {currentCity}, {currentProvince}
Pekerjaan: {jobTitle}
Universitas Asal: {prevProgramName}, {prevProgramSchool}, {prevProgramCity}, {prevProgramCountry}
Universitas Tujuan: {nextProgramName}, {nextProgramSchool}, {nextProgramCity}, {nextProgramCountry}
Beasiswa: {scholarshipKind}""".format(**person.to_dict())
                            reply(s)
                else:
                    reply("Search term argument is required")
            elif text.startswith('/dropboxsearch ') or text.startswith('/dropboxsearch@'):
                splitted = text.split(' ', 1)
                if len(splitted) >= 2:
                    q = splitted[1].lower()
                    if len(q) < 3:
                        reply("Search term must be at least 3 characters")
                    else:
                        searchResults = dropbox_search(q)

                        logging.debug(json.dumps(searchResults))   

                        s = ""
                        i = 0
                        for match in searchResults['matches']:
                            i = i + 1
                            s += "{}. {}\n".format(i, match['metadata']['path_display'].replace(dropboxFolder, "", 1))
                        reply(s)
                else:
                    reply("Search term argument is required")
            else:
                reply('What command?')

        # CUSTOMIZE FROM HERE

        elif 'who are you' in text:
            reply('telebot starter kit, created by yukuku: https://github.com/yukuku/telebot')
        elif 'what time' in text:
            reply('look at the corner of your screen!')
        else:
            if getEnabled(chat_id):
                reply('I got your message! (but I do not know how to answer)')
            else:
                logging.info('not enabled for chat_id {}'.format(chat_id))


app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
    ('/import_person', ImportPersonHandler),
    ('/export_person', ExportPersonHandler),
    ('/whois', WhoisHandler),
    ('/dropboxsearch', DropboxSearchHandler),
], debug=True)
