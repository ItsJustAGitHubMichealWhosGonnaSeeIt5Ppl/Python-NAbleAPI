# Command line app to run reports

from NAbleAPI import NAble
import os
import sys
from toolkit import selectClients, simpleCSVCreator, getDevicesForClients
import logging
import csv
from datetime import datetime, date

print(sys.argv)
pass

# Variables
NABLE_KEY = os.getenv("NABLE_KEY")
nsight = NAble('uk', NABLE_KEY, useOriginalValues=False)


def deviceOSes(operatingSystem:str=None): # List devices with OS
    validOSes = ['Windows 10', 'Windows 11']
    global nsight
    csvfile = simpleCSVCreator(filename='Device Operating Systems.csv', fields=['Client', 'Site', 'Device', 'OS'])
    devices = getDevicesForClients(nsight, selectClients(nsight.clients()))
    for client in devices:
        for site in client['devices']:
            for device in site.devices:
                deviceDetails = nsight.deviceDetails(deviceid=device.deviceid)
                if 'Microsoft' in deviceDetails.os:
                    osStr = deviceDetails.os.split(',')[0].replace('Microsoft','')
                else:
                    osStr = deviceDetails.os
                if (operatingSystem and operatingSystem.lower() in osStr.lower()) or not operatingSystem:
                    with open(csvfile,'a') as deviceCSV: # Write as the data is collected in case the script crashes
                        csvwriter = csv.writer(deviceCSV)
                        csvwriter.writerow([
                            client['client'].name,
                            site.name,
                            device.name,
                            osStr
                        ])
         

def outdatedAgent(excludedVersions:list=[]): # Get outdated agents
    global nsight
    csvfile = simpleCSVCreator(filename='Agent Version.csv', fields=['Client', 'Site', 'Device', 'Agent Version', 'Last Boot', 'Last Online (Last Response)'])
    devices = getDevicesForClients(nsight)
    for client in devices:
        for site in client['devices']:
            for device in site.devices:
                deviceDetails = nsight.deviceDetails(deviceid=device.deviceid)
                if deviceDetails.agent_version in excludedVersions: 
                    continue
                else:
                    with open(csvfile,'a') as deviceCSV: # Write as the data is collected in case the script crashes
                        csvwriter = csv.writer(deviceCSV)
                        csvwriter.writerow([
                            client['client'].name,
                            site.name, # Site
                            device.name, # Device
                            deviceDetails.agent_version, # Agent Version
                            deviceDetails.lastboot, # Last Boot
                            deviceDetails.lastresponse, # Last Response from device
                        ])
    
outdatedAgent(['10.14.4', '3.10.0'])