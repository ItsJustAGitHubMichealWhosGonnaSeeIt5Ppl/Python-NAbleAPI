# Command line app to run reports

# BUILT-IN

from NAbleAPI import NAble
from toolkit import selectClients, simpleCSVCreator, getDevicesForClients
from datetime import datetime, date
import os
import sys
import csv
import logging
import argparse





parser = argparse.ArgumentParser(
    prog='NSight Tools',
    description='An assortment of tools that use the NSight API',
    epilog='ADD SOMETHING HERE')


parser.add_argument('--test')
args = parser.parse_args()
print(args.test)
exit()
#print(sys.argv, len(sys.argv))
if len(sys.argv) > 1: 
    if sys.argv[1] in ['-h', '--help']: # Print help command
        sys.exit() # TODO help
        
        
    else:
        print(f'Unknown option \'{sys.argv[1]}\'.  Use --help to see possible options.') #TODO consolidate
        sys.exit()
    
    '--configure' # Allow user to set environment variables once and have them saved

else: # No options passed, print help?
    print('No options passed.  Use -h to see possible options.')
    #sys.exit() 

# EXTERNAL


# INTERNAL
NABLE_KEY = os.getenv("NABLE_KEY")
nsight = NAble('uk', NABLE_KEY, useOriginalValues=False)

pass

# Variables


def deviceOSes(operatingSystem:str=None, allClients:bool=False): # List devices with OS
    validOSes = ['Windows 10', 'Windows 11'] #TODO allow this to be used with other OSes
    global nsight
    csvfile = simpleCSVCreator(filename='Device Operating Systems.csv', fields=['Client', 'Site', 'Device', 'OS', 'Make', 'Model', 'Serial'])
    
    devices = getDevicesForClients(nsight, nsight.clients() if allClients else selectClients(nsight.clients()))
    for client in devices:
        for site in client['devices']:
            workstations = nsight.workstations(site.siteid)
            for workstation in workstations:
                if workstation.os == None:
                    continue # Skip devices that don't have any OS?
                elif 'Microsoft' in workstation.os:
                        osStr = workstation.os.split(',')[0].replace('Microsoft','')
                else:
                    osStr = workstation.os
                
                if (operatingSystem and operatingSystem.lower() in osStr.lower()) or not operatingSystem:
                        with open(csvfile,'a') as deviceCSV: # Write as the data is collected in case the script crashes
                            csvwriter = csv.writer(deviceCSV)
                            csvwriter.writerow([
                                client['client'].name,
                                site.name,
                                workstation.name,
                                osStr,
                                workstation.manufacturer,
                                workstation.model,
                                workstation.device_serial
                            ])
            
            if False: # Runs on device instead of workstations.
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
deviceOSes('Windows 10', True)

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