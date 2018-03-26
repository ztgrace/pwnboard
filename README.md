# PWNboard
CCDC Red Team PWNboard

# Install
apt-get install -y redis-server python3-redis python3-flask

# Slack Information

Ensure that the slackbot cna script (cobaltstrike) and the helper.py script (empire) has the proper Slack API webhook 

# Empire

copy the helper.py and agent.py scripts into empire

# Pwnboard Specific

Ensure that you add the channel ID to line 62 of pwnboard.py

Network information configured at the top

Headings modified in ./templates/index.html

![PWNboard](https://raw.githubusercontent.com/ztgrace/pwnboard/master/img/PWNboard.png)
