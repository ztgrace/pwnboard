#!/usr/bin/env python3

from flask import Flask, request, render_template, make_response
import redis
import datetime
import json
import random

# Old data from original app
TEAMS = list(range(21, 33))
HOSTS = (3, 9, 11, 23, 27, 39, 100)
NETWORK = "172.25"


r = redis.StrictRedis(host='localhost', charset="utf-8", decode_responses=True)

# Create the Flask app
app = Flask(__name__, static_url_path='/static')
app.debug = True
# Create the Config dict
global CONFIG
CONFIG = {}

@app.route('/', methods=['GET'])
def index():
    error = ""
    board = genHostsList()
    resp = make_response(render_template('index.html', error=error,
                         board=board, teams=CONFIG['teams']))
    return resp

def init():
    '''
    Initialize all the data and the config info
    '''
    global CONFIG
    CONFIG_FILE = 'config.json'
    # Load a configuration file for the data
    with open(CONFIG_FILE) as of:
        CONFIG = json.load(of)
    
    # Generate a base host list based on the infrustructure configuration
    teams = CONFIG.get("teams",())
    hostsBase = []
    for network in CONFIG['networks']:
        netip = network.get("ip","")
        for host in network.get("hosts",()):
            hostsBase += [{'ip': netip+"."+host.get("ip","0"),
                           'name': host.get('name','')}]
    
    # Add the base host list to the config for later use
    CONFIG['base_hosts'] = hostsBase

def genHostsList():
    '''
    Generate a game board based on the config file
    Get all the DB info for each host
    '''
    # Get the teams and the basehost list from the config
    teams = CONFIG.get("teams",())
    baseHosts = CONFIG.get("base_hosts", ())
    
    # Loop through each host for each team and get the data
    # Turn this data into JSON for the Jinja template
    board = []
    for baseHost in baseHosts:
        data = {}
        data['name'] = baseHost.get("name","UNKNOWN")
        data['hosts'] = []
        for team in teams:
            # Generate the ip and get the host data for the ip
            ip = baseHost['ip'].replace("x", str(team))
            # Add the host to the list of hosts
            data['hosts'] += [getHostData(ip)]
        board += [data]
    return board


def getHostData(host):
    '''
    Get the host data for a single host.
    Returns and array with the following information:
    last_seen - The last known callback time
    type - The last service the host called back through
    '''
    # Request the data from the database
    h, s, t, last = r.hmget(host, ('host', 'session',
                                 'type', 'last_seen'))
    # Add the data to a dictionary
    status = {}
    status['ip'] = host
    status['host'] = h
    status['session'] = s
    status['type'] = t
    # Set the last seen time based on the results
    if isinstance(last, type(None)):
        status['last_seen'] = 9999
    else:
        status['last_seen'] = getTimeDelta(last)
    return status


def getBoardDict():
    board = dict()
    for team in TEAMS:
        board[team] = dict()
        for host in HOSTS:
            ip = NETWORK + ".%i.%i" % (team, host)
            status = dict()
            status['host'] = h
            status['session'] = s
            status['type'] = t
            if isinstance(last, type(None)):
                # print "last: %s" % last
                status['last_seen'] = None
            else:
                print("last: %s" % last)
                status['last_seen'] = getTimeDelta(last)
            board[team][ip] = status

    return board


def getTimeDelta(ts):
        try:
            checkin = datetime.datetime.fromtimestamp(float(ts))
        except Exception as E:
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
    # text = event['text']
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

    print(status)
    status.save()


def parse_empire(event):
    text = event['text']
    status = Status(type='empire')
    if "new agent" in text:
        # kali new agent on 10.0.2.15; agent: HLT4VKEK;
        # platform: Linux,kali,4.7.0-kali1-amd64,#1 SMP Debian 4.7.5-1kali3
        # (2016-09-29),x86_64; type: empire

        status.ip = text.split(' ')[4].replace(';', '')
        status.host = text.split(' ')[0]
        status.session = text.split(' ')[6].replace(';', '')
        status.last_seen = event['ts']
        print(status)
        status.save()

    else:
        # kali empire agent EHUDM1C7 checked in
        session = text.split(' ')[3]
        status = Status(session=session, type='empire')
        status.ip = r.get(status.session)
        status.host, s, t, status.last_seen = r.hmget(status.ip,
                                                      ('host', 'session',
                                                       'type', 'last_seen'))
        status.last_seen = event['ts']
        print(status)
        status.save()


def parse_cobaltstrike(event):
    text = event['text']
    print(text)
    status = Status(type='cobaltstrike')
    if "new beacon" in text:
        # teamserver new beacon on 192.168.1.160; beacon id: 94945;
        # platform: Windows; type: cobaltstrike
        status.ip = text.split(' ')[4].replace(';', '')
        status.host = text.split(' ')[0]
        status.session = text.split(' ')[7].replace(';', '')
        status.last_seen = event['ts']
        print(status)
        status.save()

    else:
        # cobaltstrike beacon 94945 checked in
        session = text.split(' ')[2]
        status = Status(session=session, type='cobaltstrike')
        status.ip = r.get(status.session)
        status.host, s, t, status.last_seen = r.hmget(status.ip,
                                                      ('host', 'session',
                                                       'type', 'last_seen'))
        status.last_seen = event['ts']
        print(status)
        status.save()


class Status(object):
    def __init__(self, ip=None, host=None, session=None, type=None,
                 last_seen=None):
        self.ip = ip
        self.host = host
        self.session = session
        self.type = type
        self.last_seen = last_seen

        self.redis = redis.StrictRedis(host='localhost')

    def __str__(self,):
        return "ip: %s, host: %s, session: %s, type: %s, last_seen: %s" % (
            self.ip, self.host, self.session, self.type, self.last_seen)

    def save(self,):
        r.hmset(self.ip, {'host': self.host, 'session': self.session,
                          'type': self.type, 'last_seen': self.last_seen})
        if self.type == 'empire':
            r.set(self.session, self.ip)


if __name__ == '__main__':
    init()
    app.run(host='0.0.0.0', port=80)
