# CSV of devices and whether they have patch management
from NAbleAPI import NAble
import os
from toolkit import simpleCSVCreator, NSightFromEnv
import logging
import csv

nsight = NSightFromEnv(useOriginalValues=False)

lastUsers = simpleCSVCreator('patch_management.csv', ['Client', 'Site', 'Device', 'Patch Management', 'Info'])

csvRows = []
clients = nsight.clients()
for client in clients:
    try:
        clientDevices = nsight.clientDevices(clientid=client.clientid, devicetype='workstation')
    except ValueError as e: # No devices
        continue
        
    for site in clientDevices.sites:
        for device in site.devices:
            deviceDetails = nsight.deviceDetails(deviceid=device.deviceid)
            if 'macos' in str(deviceDetails.os).lower(): # Skip macs, they dont have patch management
                continue
            extraStr = ''
            if device.patch: # Try and find the patch management check
                for check in deviceDetails.checks['checks']:
                    if check.description == 'Patch Status Check':
                        extraStr = check.extra
                        break
            csvRows.append([
                client.name,
                site.name,
                device.name,
                'Yes' if device.patch else 'No',
                extraStr
                ])
        
    pass
with open(lastUsers,'a') as csvF: # Save to CSV
    csvwriter = csv.writer(csvF)
    csvwriter.writerows(csvRows)