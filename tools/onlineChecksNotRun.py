# Get all devices with checks, see how long ago it was since the checks ran.  If they havent run in the last 3 days (Default) then alert.
# List agent version as well
from NAbleAPI import NAble
import os
from toolkit import selectClients, simpleCSVCreator
import logging
import csv
from datetime import datetime, date, timedelta

NABLE_KEY = os.getenv("NABLE_KEY")
nsite = NAble('uk',NABLE_KEY,useOriginalValues=False)

allClients = nsite.clients()
today = datetime.now()
lastRun = simpleCSVCreator('OutdatedChecks.csv', fields=['Client', 'Site', 'Device', 'Last Online (Last Response)', 'Last Run', 'Agent Version', 'Last Boot']) # Leave device blank for all

if input('Do you want to check all clients? Y/n: ').lower() == 'n':
    clients = selectClients(allClients) # All clients is used to match against the requested clients.  Allows for limiting what clients can be selected
else:
    clients = allClients


for client in clients:
    logging.info(f'Checking {client.name}')
    siteDevices = []
    if int(client.device_count) == 0: # Skip clients with no devices
        logging.info(f'{client.name} has no devices.')
        continue
    
    if int(client.workstation_count) == 0: # Check for workstations
        logging.info(f'{client.name} has no workstations.')
    else:
        siteDevices += nsite.clientDevices(clientid=client.clientid,devicetype='workstation').sites

    if int(client.server_count) == 0: # Check for workstations
        print(f'{client.name} has no servers.')
        
    else:
        siteDevices += nsite.clientDevices(clientid=client.clientid,devicetype='server').sites
    
    # Check the devices
    for site in siteDevices:
        for device in site.devices:
            for checkcounts in device.checkcount: # See if the device even has checks
                if checkcounts['dsc_247'] > 0:
                    break
            else: 
                print(f'{device.name}: No checks')
                continue
            
            try:
                print(f'{device.name}: Looking for checks')
                deviceDetails = nsite.deviceDetails(deviceid=device.deviceid) 
                if deviceDetails.agent_version == '10.14.4': # Issue seems limited to 10.13.8
                    continue
                if (today - deviceDetails.lastresponse) > timedelta(days=90): # Skip offline devices
                    continue 
                
                checks = nsite.checks(deviceid=device.deviceid, includeOutput=True)
                lastRunDate = None
                for check in checks:
                    if check.date and (lastRunDate == None or check.date > lastRunDate): # Device has been online in the last 3 days, but check has not run in the last 6
                        lastRunDate = check.date
                 
                if lastRunDate and (today.date() - lastRunDate) > timedelta(days=90): # check that a last run date was set
                    with open(lastRun,'a') as lastRunCSV: # Write as the data is collected in case the script crashes
                        csvwriter = csv.writer(lastRunCSV)
                        csvwriter.writerow([
                            client.name, # Client
                            site.name, # Site
                            device.name, # Device
                            deviceDetails.lastresponse, # Last Response from device
                            lastRunDate, # Last Run
                            deviceDetails.agent_version, # Agent Version
                            deviceDetails.lastboot # Last Boot
                        ])
            except ValueError: # No checks
                print(f'{device.name}: No checks')
