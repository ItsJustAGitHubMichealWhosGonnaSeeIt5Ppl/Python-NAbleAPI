# Using the Get Local Admin script, extract and display the local admin list
from NAbleAPI import NAble
import os
from toolkit import selectClients, simpleCSVCreator
import logging
import csv

knownAdminsCSV = simpleCSVCreator('knownAdmins.csv',fields=['User','DeviceID']) # Leave device blank for all

NABLE_KEY = os.getenv("NABLE_KEY")
nsite = NAble('uk',NABLE_KEY,useOriginalValues=False)
allClients = nsite.clients()
selectedClients = selectClients(allClients)

for client in selectedClients:
    logging.info(f'Checking {client.name}')
    siteDevices = []
    if int(client.device_count) == 0: # Skip clients with no devices
        logging.info(f'{client.name} has no devices.')
        continue
    
    if int(client.workstation_count) == 0: # Check for workstations
        logging.info(f'{client.name} has no workstations.')
    else:
        siteDevices += nsite.clientDevices(clientid=client.clientid,devicetype='workstation',includeDetails=True).sites

    if int(client.server_count) == 0: # Check for workstations
        print(f'{client.name} has no servers.')
    else:
        siteDevices += nsite.clientDevices(clientid=client.clientid,devicetype='server',includeDetails=True).sites
    
    # Check the devices
    for site in siteDevices:
        for device in site.devices:
            try:
                checks = nsite.checks(deviceid=device.deviceid, includeOutput=True)
                checkFound = False # Adds an alert if the check wasn't found
                for check in checks:
                    if 'Script Check - Check Local Admins' in check.description: # Check exists and has run
                        adminUsers = check.output.split('\n')[1:] # Get admin user list (list is split with new line)
                        with open(knownAdminsCSV,'r') as adminCSV:
                            adminRowsCSV = csv.DictReader(adminCSV)
                            for row in adminRowsCSV:
                                if row['DeviceID'] and int(row['DeviceID']) != device['deviceid']:
                                    continue
                                else: # Device ID was blank or it matched
                                    try:
                                        adminUsers.remove(row['User']) # Remove admins that we don't want to alert about
                                    except ValueError:
                                        continue
                    
                        if len(adminUsers) >0: # See if there are any admins left
                            print(f'{device.name}: Users with Admin rights\n- {'\n- '.join(adminUsers)}')
                            
                        else:
                            print(f'{device.name}: No abnormal Admins')
                            
                        checkFound = True # Regardless mark that the check was found
                        break
                    
                    #elif 'Script Check - Check Local Admins' in check['description'] and check['checkstatus'] != 'testok':
                        #print(f'{device.name}: ERROR - {check['checkstatus']} ' + str(check['extra']) if 'extra' in check else '')
                        #checkFound = True
                        #break
                    
                if not checkFound:
                    print(f'{device.name}: Check not present')
                        
            except ValueError: # No checks
                print(f'{device.name}: No checks')
