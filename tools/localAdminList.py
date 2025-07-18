# Using the Get Local Admin script, extract and display the local admin list
# Requires 3.12+
from NAbleAPI import NAble
import os
from toolkit import selectClients, simpleCSVCreator
import logging
import csv

localAdmins = simpleCSVCreator('Local Admins.csv', fields=['Client', 'Site', 'Device','Admin User', 'Last Checked']) # Leave device blank for all
knownAdminsInp = input('Provie a list of known admins that should not be included in the report (comma separated): ')
if str(knownAdminsInp) != '':
    knownAdmins = knownAdminsInp.lower().replace(', ', ',').split(',') # Make everything lowercase, remove whitespace after commas, split on commas

NABLE_KEY = os.getenv("NABLE_KEY")
nsite = NAble('uk',NABLE_KEY,useOriginalValues=False)
allClients = nsite.clients()
clients = selectClients(allClients) # All clients is used to match against the requested clients.  Allows for limiting what clients can be selected

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
            try:
                checks = nsite.checks(deviceid=device.deviceid, includeOutput=True)
                with open(localAdmins,'a') as adminCSV: # Write as the data is collected in case the script crashes
                    csvwriter = csv.writer(adminCSV)
                    for check in checks:
                        if 'Script Check - Check Local Admins' in check.description and check.output != None: # Check exists and has run
                            adminUsers =check.output.split('\n')[1:] # Get admin user list (list is split with newline, first line is not needed)
                        
                            if len(adminUsers) >0: # See if there are any admins left
                                print(f'{device.name}: Users with Admin rights\n- {"\n- ".join(adminUsers)}')
                                for user in adminUsers: # Write row for each admin
                                    if user.lower() in  knownAdmins: # Skip
                                        continue
                                    
                                    csvwriter.writerow([
                                        client.name, # Client
                                        site.name, # Site (it does exist idk why its red)
                                        device.name, # Device
                                        user, # Admin User
                                        check.date # Last Checked
                                    ])
                            else: # No admins
                                continue
                            
                            break # Break because we already found the admin script
                    else: # Check doesnt exist
                        print(f'{device.name}: Check not found')
                        csvwriter.writerow([
                            client.name, # Client
                            site.name, # Site (it does exist idk why its red)
                            device.name, # Device
                            'NO CHECK FOUND', # Admin User
                            'N/A' # Last Checked
                        ])
            except ValueError: # No checks
                print(f'{device.name}: No checks')
