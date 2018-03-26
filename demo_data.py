#!/usr/bin/env python3

import redis
import random
import datetime as dt
import time
import json


CONFIG = {}


def init():
    '''
    Initialize all the data and the config info from a file
    '''
    global CONFIG
    CONFIG_FILE = 'config.json'
    # Load a configuration file for the data
    with open(CONFIG_FILE) as of:
        CONFIG = json.load(of)
    # Generate a base host list based on the infrustructure configuration
    hostsBase = []
    for network in CONFIG['networks']:
        netip = network.get("ip", "")
        for host in network.get("hosts", ()):
            hostsBase += [{'ip': netip+"."+host.get("ip", "0"),
                           'name': host.get('name', '')}]
    # Add the base host list to the config for later use
    CONFIG['base_hosts'] = hostsBase


def genDemoData():
    '''
    Shove out demo data for a host
    '''
    def genTime():
        '''
        Generate a random time
        '''
        return time.mktime((dt.datetime.now() - dt.timedelta(
                            minutes=random.randint(1, 10))).timetuple())

    types = ("meterpreter", "colbaltstrike", "empire", "backdoor")
    sessions = ['root', 'nobody', 'www']+[i for i in range(0, 79)]
    # Create the random data
    status = dict()
    status['host'] = "RT%i" % random.randint(1, 5)
    status['session'] = random.choice(sessions)
    # Choose a random callback type
    status['type'] = random.choice(types)
    # Choose a random last_seen time
    status['last_seen'] = random.choice((genTime(), None))
    return status


def populateData():
    '''
    Loop through each host for each team and random assign data, or not
    '''
    # Call the pwnboard init function to read the teams from the CONFIG
    init()
    # Load the database
    r = redis.StrictRedis(host='localhost', charset="utf-8")
    # Loop through each box for each team
    for team in CONFIG['teams']:
        for basehost in CONFIG['base_hosts']:
            if random.randint(1, 10) % 2 == 0:
                continue
            # Generate the IP based on the team number and the hostlist
            ip = basehost.get('ip').replace("x", str(team))
            # Get random data
            status = genDemoData()
            # Put it in the database
            r.hmset(ip, status)


if __name__ == '__main__':
    print("[*] Generating data...")
    init()
    populateData()
    print("[+] Done")
