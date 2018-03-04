#!/usr/bin/env python

import redis
import random
from pwnboard import getTimeDelta
import datetime as dt
import time
import string

r = redis.StrictRedis(host='localhost')
for team in range(21, 31):
    for host in (3, 9, 11, 23, 27, 39, 240, 241, 254):
        if random.randint(1, 10) % 2 == 0:
            continue

        ip = "172.25.%i.%i" % (team, host)
        status = dict()
        status['host'] = "RT%i" % random.randint(1,5)
        if random.randint(1, 10) % 3 == 0:
            status['type'] = "meterpreter"
            status['session'] = random.randint(1,100)
            status['last_seen'] = None
        elif random.randint(1, 10) % 2 == 0:
            status['type'] = "backdoor"
            status['session'] = random.choice(('root', 'admin' 'nobody'))
            status['last_seen'] = time.mktime((dt.datetime.now() - dt.timedelta(minutes=random.randint(1, 10))).timetuple())
        else:
            status['type'] = "empire"
            status['session'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            status['last_seen'] = time.mktime((dt.datetime.now() - dt.timedelta(minutes=random.randint(1, 10))).timetuple())
        
        r.hmset(ip, status)
