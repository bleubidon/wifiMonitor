#!/bin/bash
cd /home/pi/wifi_monitor
mkdir logs
tmux new-session -d -s tmux_wifi_monitor "./WifiMonitor.py > logs/log.log 2>&1"
