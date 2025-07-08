# CSV of devices and whether they have patch management
from NAbleAPI import NAble
import os
from toolkit import simpleCSVCreator, NSightFromEnv
import logging
import csv

nsight = NSightFromEnv(useOriginalValues=False)

lastUsers = simpleCSVCreator('patch_management.csv', ['Client', 'Site', 'Device', 'Patch Management', 'Check Status', 'Last Run', 'Consecutive Fails', 'Output'])

csvRows = []
clients = nsight.clients()
for client in clients:
    try:
        clientDevices = nsight.clientDevices(clientid=client.clientid, devicetype='workstation')
    except ValueError as e: # No devices
        continue
        
    for site in clientDevices.sites:
        for device in site.devices:
            print(f'Checking {device.name} for {client.name}')
            deviceDetails = nsight.deviceDetails(deviceid=device.deviceid)
            if 'macos' in str(deviceDetails.os).lower(): # Skip macs, they dont have patch management
                continue
            outputStr = 'N/A'
            PMELastRun = 'No Check'
            PMECheckStatus = 'No Check'
            consecFails = 'N/A'
            if device.patch: # Try and find the patch management check
                checks = nsight.checks(deviceid=device.deviceid, includeOutput=True)
                for check in checks:
                    if check.description == 'Patch Status Check':
                        PMECheckStatus = check.status
                        outputStr = check.output if check.output else 'Check Exists, no extra info'
                        PMELastRun = check.date.strftime("%Y-%m-%d") if check.date else "Unknown"
                        consecFails = check.consecutive_fails
            print(f'Adding {device.name} for {client.name}')
            csvRows.append([
                client.name,
                site.name,
                device.name,
                'Yes' if device.patch else 'No',
                PMECheckStatus,
                PMELastRun,
                consecFails,
                outputStr
                ])
        
    pass
with open(lastUsers,'a') as csvF: # Save to CSV
    csvwriter = csv.writer(csvF)
    csvwriter.writerows(csvRows)