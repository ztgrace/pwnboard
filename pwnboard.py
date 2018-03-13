#!/usr/bin/env python2

from flask import Flask, request, render_template, flash, url_for, make_response
import redis
import datetime

TEAMS = range(21, 33)
HOSTS = (3,9,11,23,27,39,100)
NETWORK = "172.25"

r = redis.StrictRedis(host='localhost')
app = Flask(__name__, static_url_path='/static')
app.debug = True

@app.route('/', methods=['GET'])
def index():
    error = ""
    board = getBoardDict()
    resp = make_response(render_template('index.html', error=error, board=board, teams=sorted(TEAMS), hosts=sorted(HOSTS), network=NETWORK))
    return resp

def getBoardDict():
    board = dict()
    for team in TEAMS:
        board[team] = dict()
        for host in HOSTS:
            ip = NETWORK + ".%i.%i" % (team, host)
            h, s, t, last = r.hmget(ip, ('host', 'session', 'type', 'last_seen'))
            status = dict()
            status['host'] = h
            status['session'] = s
            status['type'] = t
            if isinstance(last, type(None)):
                #print "last: %s" % last
                status['last_seen'] = None
            else:
                print "last: %s" % last
                status['last_seen'] = getTimeDelta(last)
            board[team][ip] = status

    return board

def getTimeDelta(ts):
        try:
            checkin = datetime.datetime.fromtimestamp(float(ts))
        except:
            return 0
        diff = datetime.datetime.now() - checkin
        minutes = int(diff.total_seconds()/60)
        return minutes



@app.route('/slack-events', methods=['POST'])
def slack_events():
    res = request.json
    if res.get('challenge', None):
        return request.json['challenge']

    # to get the 'channel' value right click on the channel and copy link
    # I.E C9PGYTYH5
    if res.get('event', None) and res.get('event')['channel'] == '':
        process_shellz_event(res['event'])

    return ""


def process_shellz_event(event):
    text = event['text']
    if 'empire' in event['text']:
        parse_empire(event)
    elif 'cobaltstrike' in event['text']:
        parse_cobaltstrike(event)
    else:
        parse_linux(event)

def parse_linux(event):
    # "%s %s backdoor active on %s"
    text = event['text']
    status = Status()
    status.ip = text.split(' ')[5]
    status.host = text.split(' ')[0]
    status.session = text.split(' ')[1]
    status.last_seen = event['ts']

    print status
    status.save()

def parse_empire(event):
    text = event['text']
    status = Status(type='empire')
    if "new agent" in text:
        # kali new agent on 10.0.2.15; agent: HLT4VKEK; platform: Linux,kali,4.7.0-kali1-amd64,#1 SMP Debian 4.7.5-1kali3 (2016-09-29),x86_64; type: empire

        status.ip = text.split(' ')[4].replace(';', '')
        status.host = text.split(' ')[0]
        status.session = text.split(' ')[6].replace(';', '')
        status.last_seen = event['ts']
        print status
        status.save()

    else:
        # kali empire agent EHUDM1C7 checked in
        session = text.split(' ')[3]
        status = Status(session=session, type='empire')
        status.ip = r.get(status.session)
        status.host, s, t, status.last_seen = r.hmget(status.ip, ('host', 'session', 'type', 'last_seen'))
        status.last_seen = event['ts']
        print status
        status.save()

def parse_cobaltstrike(event):
    text = event['text']
    print text
    status = Status(type='cobaltstrike')
    if "new beacon" in text:
    # teamserver new beacon on 192.168.1.160; beacon id: 94945; platform: Windows; type: cobaltstrike
      status.ip = text.split(' ')[4].replace(';', '')
      status.host = text.split(' ')[0]
      status.session = text.split(' ')[7].replace(';', '')
      status.last_seen = event['ts']
      print status
      status.save()

    else:
    # cobaltstrike beacon 94945 checked in
      session = text.split(' ')[2]
      status = Status(session=session, type='cobaltstrike')
      status.ip = r.get(status.session)
      status.host, s, t, status.last_seen = r.hmget(status.ip, ('host', 'session', 'type', 'last_seen'))
      status.last_seen = event['ts']
      print status
      status.save()


class Status(object):
    def __init__(self, ip=None, host=None, session=None, type=None, last_seen=None):
        self.ip = ip
        self.host = host
        self.session = session
        self.type = type
        self.last_seen = last_seen

        self.redis = redis.StrictRedis(host='localhost')

    def __str__(self,):
        return "ip: %s, host: %s, session: %s, type: %s, last_seen: %s" % (self.ip, self.host, self.session, self.type, self.last_seen)

    def save(self,):
        r.hmset(self.ip, {'host': self.host, 'session': self.session, 'type': self.type, 'last_seen': self.last_seen})
        if self.type == 'empire':
            r.set(self.session, self.ip)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
