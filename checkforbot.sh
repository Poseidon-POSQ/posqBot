#!/bin/bash

ps aux | grep python3 | grep posqBot.py
if [ $? -eq 0 ]; then
    #echo OK
    :
else
    cd /home/bunchies/posqBot
    python3 /home/bunchies/posqBot/posqBot.py
fi

