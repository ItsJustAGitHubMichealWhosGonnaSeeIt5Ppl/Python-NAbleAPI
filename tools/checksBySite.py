# Find checks under a specific site name (helpful if you have a "Retired" or "Hiatus" site that you don't want devices having AV, tasks, etc)

from NAbleAPI import NAble
from time import sleep
import csv
from datetime import date
import logging
import json
import os
from toolkit import clearConsole, authNSight

nable = authNSight()

siteNames = input('Enter site name(s) to check for: ') #TODO allow multiple site names to be entered

allClients = nable.clients() # Search all clients

for client in allClients: # Iterate through clients
    if int(client['device_count']) > 0: # Client has devices to be checked
        sites = nable.sites(client['clientid'])
        for site in sites: # Iterate through sites, look for matching names
            if site['name'].lower() == siteNames.lower(): #TODO make this a list so multiple site names can be used
                workstations = nable.workstations(site['siteid'])
                servers = nable.servers(site['siteid'])
                devices = workstations + servers # combine list
                for device in devices:
                    if 'workstationid' in device: # Fix IDs
                        deviceID = device['workstationid']
                    elif 'serverid' in device:
                         deviceID = device['serverid']
                    else:
                        #TODO add warning here
                        continue
                    
                    if device['active_247'] == '1' or device['dsc_active'] == '1':
                        print(f'{device['name']} has active checks!' )

    

