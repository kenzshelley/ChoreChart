from flask import Flask
from firebase import firebase
from apscheduler.schedulers.background import BackgroundScheduler
from twilio.rest import TwilioRestClient

import json

app = Flask(__name__)

sched = BackgroundScheduler(timezone='utc')

keys_file = open("keys.json", "r")
keys = json.loads(keys_file.read())

account_sid = keys['keys']['twilio']['account_sid']
auth_token = keys['keys']['twilio']['auth_token']

client = TwilioRestClient(account_sid, auth_token)
firebase = firebase.FirebaseApplication('https://doyourchores.firebaseio.com', None)

@app.route("/")
def hello():
    return "Hello World!"

def test_job():
    print "Ran the job!"

def trash_out():
    last_person = firebase.get('/last_out', None)
    next_person_ind = (last_person + 1) % 7
    next_person = firebase.get('/users/%s' % next_person_ind, None)
    name =  next_person['name']
    phone = next_person['phone']
    print "Sending text to %s" % name

    r = firebase.put('/', 'last_out', next_person_ind)
    message = client.messages.create(
            body="Time to take out the trash, %s!" % name.title(),
            to="+%s" % phone,
            from_="+15134492254")

def trash_in():
    last_person = firebase.get('/last_in', None)
    next_person_ind = (last_person + 1) % 7
    next_person = firebase.get('/users/%s' % next_person_ind, None)
    name =  next_person['name']
    phone = next_person['phone']
    print "Sending text to %s" % name

    r = firebase.put('/', 'last_in', next_person_ind)
    message = client.messages.create(
            body="Time to bring the trash back in, %s!" % name.title(),
            to="+%s" % phone,
            from_="+15134492254")
trash_in()

# Times in UTC
sched.add_job(trash_out, 'cron', day_of_week="sun", hour=23, minute=59)
sched.add_job(trash_in, 'cron', day_of_week="mon", hour=23, minute=59)
sched.start()

if __name__ == "__main__":
    app.run()
