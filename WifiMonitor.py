#!/usr/bin/env python3
# Run as root

from Hardware import Hardware
from time import time, sleep
import json
from glob import glob
import os
from os import system as cmd
from subprocess import check_output as cmd_verbose
os.chdir("/home/pi/wifi_monitor")

class WifiMonitor:
    def __init__(self, log=True, verbose=False):
        self.wifiMonitorRunning = False
        self.parseTimePeriod = 1  # in seconds
        self.startTime = 0
        self.log = log
        if self.log:
            self.logPrefix = "logs/log_"
            self.logPeriod = 10  # in seconds
            self.logStartTime = 0
        WifiMonitor.verbose = verbose

    airodumpOutputFilenamePrefix = "myAirodumpOutput"
    wifiDataFilename = "wifiData.json"

    @classmethod
    def printIfVerbose(cls, to_printIfVerbose):
        if cls.verbose:
            print(to_printIfVerbose)

    @classmethod
    def setupHardware(cls):
        Hardware.setupHardware()

    @classmethod
    def shutdownRpi(cls):
        Hardware.triggerShutdownRpi_attr = False
        cls.printIfVerbose("Shutting down")
        cmd("shutdown now")

    @classmethod
    def killAirodumpPIDs(cls):
        try:
            cls.airodumpPids = cmd_verbose("pgrep airodump-ng", shell=True).decode("utf-8").split("\n")
        except:
            return
        for airodumpPid in cls.airodumpPids:
            if airodumpPid != "":
                cmd("kill -9 {}".format(airodumpPid))

    @classmethod
    def initWifiDataJSON(cls):
        if not os.path.exists(cls.wifiDataFilename):
            initial_json = "{\n\t\"stations\": {\n\t}\n}"
            cmd("echo '{}' > {}".format(initial_json, cls.wifiDataFilename))

    def toggleWifiMonitor(self):
        Hardware.triggerToggleWifiMonitor_attr = False
        self.wifiMonitorRunning = not self.wifiMonitorRunning
        if self.wifiMonitorRunning:
            WifiMonitor.printIfVerbose("resuming airodump")
            WifiMonitor.launchAirodump()
        else:
            WifiMonitor.printIfVerbose("pausing airodump")
            WifiMonitor.killAirodumpPIDs()

    @classmethod
    def toggleInternalLed(cls, status):
        if status not in ("on", "off"):
            return "Wrong argument"
        if status == "on":
            cmd("echo mmc0 | sudo tee /sys/class/leds/led0/trigger")
        elif status == "off":
            cmd("echo none | sudo tee /sys/class/leds/led0/trigger")
            cmd("echo 1 | tee /sys/class/leds/led0/brightness")

    @classmethod
    def launchAirodump(cls):
        cls.printIfVerbose("launching Airodump in the background")
        # Cleanup before start
        airodumpOutputFiles = glob("{}*.csv".format(cls.airodumpOutputFilenamePrefix))
        for filename in airodumpOutputFiles:
            os.remove(filename)
        # Launch airodump in the background with output to file
        cmd("nohup airodump-ng -w {} -o csv -I 1 wlan1 > /dev/null 2>&1 &".format(cls.airodumpOutputFilenamePrefix))
    
    def registerStationEvent(self, station_array):
        do_stationEvent_register = "none"

        # Retrieving and formatting station info
        station_mac = station_array[0]

        last_time_seen = station_array[2].split(" ")
        last_time_seen_date = last_time_seen[0].split("-")
        last_time_seen_date = "-".join([last_time_seen_date[2], last_time_seen_date[1], last_time_seen_date[0][2:]])
        last_time_seen_time = last_time_seen[1].split(":")
        last_time_seen_time = ":".join([last_time_seen_time[0], last_time_seen_time[1]])
        last_time_seen = last_time_seen_date + " " + last_time_seen_time

        # 2019-12-30 16:38:02

        # Polling known station info from json
        with open(WifiMonitor.wifiDataFilename) as wifiDataFile:
            wifiData = json.load(wifiDataFile)
        
        if station_mac not in wifiData["stations"]:
            WifiMonitor.printIfVerbose("unknown MAC detected")
            do_stationEvent_register = "full"
        else:
            WifiMonitor.printIfVerbose("known MAC detected")
            registered_times = wifiData["stations"][station_mac]
            if last_time_seen not in registered_times:
                do_stationEvent_register = "append"
            else:
                do_stationEvent_register = "none"
        
        # Registering new json entry if necessary
        if do_stationEvent_register == "none":
            return
        if do_stationEvent_register == "append":
            registered_times.append(last_time_seen)
            wifiData["stations"][station_mac] = registered_times
        elif do_stationEvent_register == "full":
            wifiData["stations"][station_mac] = [last_time_seen]

        # Dump updated JSON
        with open(WifiMonitor.wifiDataFilename, 'w') as wifiDataFile:
            json.dump(wifiData, wifiDataFile, indent=4)

    def parseAirodumpOutput(self, register=True):
        WifiMonitor.printIfVerbose("parsing Airodump output")
        airodumpOutputFiles = glob("{}*.csv".format(WifiMonitor.airodumpOutputFilenamePrefix))
        if len(airodumpOutputFiles) != 1:
            return "No or too many airodump output file(s)"

        with open(airodumpOutputFiles[0], "r") as f:
            content = f.read()

        content_sections = content.split("Probed ESSIDs\n")
        stations_section = ""
        if len(content_sections) == 2:  # There is at least one station detected by airodump
            stations_section = content_sections[1]
            for station in stations_section.split("\n"):
                if station != "":
                    station_array = station.split(", ")
                    WifiMonitor.printIfVerbose(station_array)
                    if register:
                        self.registerStationEvent(station_array)

    def launch(self):
        if self.log:
            if not os.path.exists(self.logPrefix.split("/")[0]):
                cmd("mkdir {}".format(self.logPrefix.split("/")[0]))
        WifiMonitor.setupHardware()
        WifiMonitor.toggleInternalLed("off")
        WifiMonitor.killAirodumpPIDs()
        WifiMonitor.initWifiDataJSON()
        WifiMonitor.launchAirodump()
        self.wifiMonitorRunning = True
        self.startTime = time()

        while 1:
            # Events polling
            if Hardware.triggerShutdownRpi_attr:
                if self.log:
                    cmd("date >> {}shutdown.log".format(self.logPrefix))
                WifiMonitor.shutdownRpi()
            if Hardware.triggerToggleWifiMonitor_attr:
                if self.log:
                    cmd("date >> {}toggle.log".format(self.logPrefix))
                self.toggleWifiMonitor()
            if self.wifiMonitorRunning:
                Hardware.setLed("off")
            else:
                Hardware.setLed("on")

            # Wifi parsing and registering
            if time() - self.startTime > self.parseTimePeriod:
                self.startTime = time()
                self.parseAirodumpOutput(register=True)

            # Logging rpi's ip address
            if self.log:
                if time() - self.logStartTime > self.logPeriod:
                    self.logStartTime = time()
                    cmd("date >> {}ipaddr.log".format(self.logPrefix))
                    cmd("hostname -I >> {}ipaddr.log".format(self.logPrefix))
            sleep(.1)

myWifiMonitor = WifiMonitor(log=True, verbose=False)
myWifiMonitor.launch()
