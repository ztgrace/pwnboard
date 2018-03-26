#!/usr/bin/env python3
import json, yaml
from termcolor import colored as c

COLOR = 'blue'
def prompt(text="", color=COLOR):
    '''
    Generate a prompt with the given color and return the output
    '''
    return input(c(text, color, attrs=('bold',)))

def getTeamRange():
    '''
    Generate a list of the team numbers based on starting and ending values
    '''
    while True:
        try:
            # Get the input
            start = int(prompt("Starting team number: ", COLOR))
            end = int(prompt("Ending team number: ", COLOR))
            # Generate an array with the team numbers
            teams = [i for i in range(start, end+1)]
            # Validate that the input is correct
            print(teams)
            isGood = prompt("Correct? [Y/n]", "green")
            if isGood in ("", "y", "yes"):
                # If its right, return the array
                return teams
            # Loop if not correct
        except Exception as E:
            print("Invalid range")
            # Loop if there is any errors


def addHost(network):
    '''
    Get the input information for a host on the network
    '''
    while True:
        ip = input(c('IP: ',COLOR, attrs=('bold',))+network+".")
        hostname = prompt("Hostname: ")
        os = prompt("OS: ")
        isGood = prompt("Correct? [Y/n]", "green")
        if isGood in ("", "y", "yes"):
            # If its right, return the host info
            return {'ip': ip, 'name': hostname, 'os': os}


def addNetwork():
    '''
    Add a network to the config. add hosts to each network
    '''
    data = {}
    # Get the network ip. Keep trying until it is right
    while True:
        try:
            ip = prompt(
                'Network IP (e.g. "10.2.x.0"): ')
            ip = ".".join(ip.split(".")[:3]).lower()
            data['ip'] = ip
            # Make sure there is an 'x' in the ip
            ip.index("x")
            break
        except Exception as E:
            print("Invalid Network Name")
    # get the network name
    data['name'] = prompt('Network name (e.g. "cloud"): ')
    # Add hosts to the network
    data['hosts'] = []
    while True:
        # Keep adding hosts until we are done
        newHost = prompt("Add a host to this network? [Y/n]", "green")
        if newHost not in ("", "y", "yes"):
            break
        # Create a new host and add it to the dataset
        data['hosts'] += [addHost(ip)]
    return data


def addNetworks():
    data = []
    while True:
        # Keep adding networks until we are done
        newNetwork = prompt("Add network? [Y/n]", "green")
        if newNetwork not in ("", "y", "yes"):
            break
        # Create a new network and add it to the dataset
        data += [addNetwork()]
    return data


def main():
    '''
    Call all the generate functions and build a json config
    '''
    config = {}
    # Get the teams
    config['teams'] = getTeamRange()
    # Get the networks
    config['networks'] = addNetworks()
    print(json.dumps(config, indent=4))
    print(yaml.dump(config, default_flow_style = False))


if __name__ == '__main__':
    main()
