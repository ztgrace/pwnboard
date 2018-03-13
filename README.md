# PWNboard
CCDC Red Team PWNboard

Install:
pip install flask

pip install redis

apt-get install -y redis-server

Slack Information:

Ensure that the slackbot cna script (cobaltstrike) and the helper.py script (empire) has the proper Slack API webhook 

Empire:

copy the helper.py and agent.py scripts into empire

Pwnboard:

Ensure that you add the channel ID to line 62 of pwnboard.py

Network information configured at the top

Headings modified in ./templates/index.html

![PWNboard](https://raw.githubusercontent.com/ztgrace/pwnboard/master/img/PWNboard.png)
