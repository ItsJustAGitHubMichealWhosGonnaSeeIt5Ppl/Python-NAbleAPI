# Find missing checks

from NAbleAPI import NAble
from time import sleep
import csv
from datetime import date
import logging
import json
from toolkit import clearConsole

#TODO add a visual interface or enhanced commandline with curses.
#TODO add more logs

toolVer = '0.0.3'
compatibleWith = '0.0.3' # TODO make this actually do something Compatible version of package

def logfig(): # Configure logger
    print('Logging level set to normal. To change, type DEBUG, otherwise press enter/return')
    userInp = input(': ')
    if userInp.lower().strip() == 'debug':
        return 'DEBUG'
    else:
        return 'WARNING'
    
def printList(header,listToPrint):
    if listToPrint == []: # Return nothing if list is empty
        return None
    print(header)
    for item in listToPrint:
        print(item)


  
def inputValidation(text,validOptions=['yes','y','no','n'],returnBool=True,timeout=10): # Input validator
    """Basic input validation

    Args:
        text (str): Message to display to user
        validOptions (list, optional): Valid responses, must be lowercase. Defaults to ['yes','y','no','n'].
        returnBool (bool, optional): Whether to return a boolean. Only use with default validOptions. Defaults to True.
        timeout (int, optional): How many attempts to give the user before timing out. Defaults to 10.

    Returns:
        any: Bool if returnBool is True, else returns raw
    """
    loop = 0
    while loop < timeout:
        userInp = input(text)
        if userInp.lower() not in validOptions: # Invalid input
            print('Invalid response')
            clearConsole()
        else: # Valid input
            if returnBool == True:
                return True if userInp.lower().startswith('y') else False
            else:
                return userInp.lower()
        loop+=1
    
    raise ValueError('Invalid input, max retries reached') # Raise error if max retries is hit

def simpleCSVCreator(filename,fields): # Creates CSVs
    if filename.endswith('.csv'):
        rawName = filename.replace('.csv','')
    else:
        rawName = filename
        filename = filename + '.csv'
        
    todayte = date.today().strftime("%Y.%m.%d") # Todays date
    fileExists = 0 # Allow file to be renamed
    tryCount = 0 # Will be appended to file name each loop that fails
    fileMode = 'x'
    creationType = 'Created'
    while True:
        try: # Try to create file
            csvFile = open(filename,fileMode)
            break
        except FileExistsError:
            if fileExists == 0: # skip after first loop.  Allows filename value to continue ticking up
                fileExists = inputValidation(f'File with name {filename} already exists in directory! What would you like to do?\n[1] Overwrite\n[2] Append\n[3] Create New\nSelection: ',validOptions=['1','2','3'],returnBool=False)
                clearConsole()

            if int(fileExists) == 1: # Overwrite existing file
                fileMode = 'w'
                creationType = 'Overwrote'

            elif int(fileExists) == 2: # Append to existing file
                fileMode = 'a'
                creationType = 'Appending to existing'

            else: # Make a new file
                if tryCount == 0: # Try adding date before adding number
                    rawName = rawName + todayte

                else:
                    rawName = rawName + todayte + str(tryCount) # Creates new filename
                filename = rawName + '.csv'
                tryCount +=1
        except PermissionError: # File permissions denied
            input(f'Permission to edit {filename} denied. Update permissions and then press any key to continue...')
            clearConsole()
        except Exception as e:
            print(e)
            input('TEMP PAUSE - Remove me once you figure out what the exception is that the CSV will raise')
    
    csvFile.close() # Close file
    csvFile = open(filename,'r+')
    
    try: # Check for existing columns
        reader = csv.reader(csvFile)
        if fields != next(reader): # fields do not match existing fields
            raise ValueError(f'Fields in {filename} do not match!') #TODO allow new CSV to be created here
    except StopIteration: # No Columns
        csv.writer(csvFile).writerow(fields)
    except Exception as e: # TODO figure out what the errors are
        csvFile.close()
        raise e
    csvFile.close()

    print(creationType  + f' CSV file: {filename}')
    return filename

def settingsLoader(): # Loads settings file (if it exists)
    try:
        with open('missingChecks.conf','r') as settingsFile:
            settings = json.loads(settingsFile.readline())
    except json.decoder.JSONDecodeError:
        logging.warning('Failed to load settings file: data is invalid (not JSON)')
        return False, None
    except FileNotFoundError:
        logging.info('Failed to load settings file: Does not exist')
        return False, None
    except Exception as e:
        logging.warning('Failed to load settings file: Other error',exc_info=1)
        return False, None
    useExisting = inputValidation('Existing settings founds, would you like to use them? [Y/N]: ')
    if useExisting:
        print('Loading settings')
        return True, settings # Use settings
    else:
        return False, None # Don't use settings
    
def settingsCreator(region,key,fullChecks,partialChecks): # Create/save settings
    template = {'region': None,
                'key': None,
                'fullChecks': None,
                'partialChecks': None
                }
    def saveSettings(data):
        data = json.dumps(data) # Write as json
        try:
            with open('missingChecks.conf','w') as settingsFile:
                settingsFile.write(data)
        except: # TODO add failures
            print('Failed to save settings')
            
        
    usrInp = input('Would you like to save these settings for next time?\n[N]o\n[O]nly credentials\n[C]hecks only\n[B]oth credentials and checks\nYour Choice (default = N): ')
    usrInp = usrInp.lower().strip() # Strip the garbage away
    clearConsole()
    if usrInp not in ['n','o','c','b'] or usrInp == 'n':
        print('Settings will not be saved')
    else:
        if usrInp in ['o','b']:
            template['region'] = region
            template['key'] = key
            
            print('Credentials will be saved')
        if usrInp in ['c','b']:
            template['fullChecks'] = fullChecks
            template['partialChecks'] = partialChecks
            print('CHECK SAVING CURRENTLY DOES NOT WORK SORRY')
            #print('Checks will be saved')
        saveSettings(template)
   
     
# START OF PROGRAM

print(f'Missing Check Finder Tool\nVersion: {toolVer}\n This tool is used to find missing checks on your devices!')

logging.basicConfig(level=eval(f'logging.{logfig()}')) # Set logging level
logging.info('Log level set')

existingSettings = settingsLoader() # Get existing settings (if they exist)
logging.debug(f'Existing settings returned {existingSettings}')

loop = 0
while True:
    if loop == 10:
        print('I believe in you')
    elif loop == 100:
        print('I\'m losing hope')
    
    # get key and region
    if loop == 0 and existingSettings[0] and existingSettings[1]['key'] != None: # Use saved settings (only try once)
        userRegion = existingSettings[1]['region']
        api_key = existingSettings[1]['key']
    else:
        userRegion = input('Please enter your region (regions can be found at the package wiki): ')
        api_key = input('Please enter your API key: ')

    # Set up nable
    try:
        NAbleSession = NAble(region=userRegion,key=api_key)
        break
    except Exception as e:
        clearConsole()
        logging.info('Login failed', exc_info=1)
        print(f'[ERROR] {e}')
    loop +=1

clearConsole()
print('Successfully Connected')

checkList = [] # Check names to look for
partialCheckList = [] # Partial check names to look for
while True: # Configuring
    #TODO allow checks to be added from a CSV or txt file
    #TODO allow multiple checks to be added here
    check = input('Enter the check name you would like to search for: ')
    partial = inputValidation('Is the check name a partial name? (if unsure, choose yes) [Y/N]: ')
    if partial: 
        partialCheckList += [check]
    else:
        checkList += [check]

    addMore = inputValidation('Would you like to add another check? [Y/N]: ')
    
    if addMore == False:
        clearConsole()
        break
    else:
        clearConsole()

# TODO allow list to be edited here
# TODO warn if no items have been added to be checked

# Sort lists
checkList.sort()
partialCheckList.sort()

#Print lists (if data is present)
printList('Looking for the following checks',checkList)
printList('Looking for the following partial match checks', partialCheckList)
input('Press any key to continue')

clearConsole()
settingsCreator(userRegion,api_key,checkList,partialCheckList)

saveToCSV = inputValidation('Would you like to save the output of this scan to a CSV? [Y/N]: ')
if saveToCSV:
    csvRowTemplate = []
    for i in range(len(checkList)+len(partialCheckList)): 
        csvRowTemplate += ['Missing'] # Create blank check row
    print('CSV will be created in root directory')
    csvFields = ['Customer', 'Site', 'Device'] + checkList + partialCheckList
    csvFilename = simpleCSVCreator(filename='missing_checks',fiels=csvFields) # Try to create the CSV
else:
    clearConsole()


checkAll = inputValidation('Would you like to check all clients? [Y/N]: ')
allClients = NAbleSession.clients() # get all clients

if checkAll == False: # Checking a specific client
    selectedClients = []
    while True:
        userSearchRaw = input('Please enter the IDs or name of the clients you want to check (comma separated, mix of IDs and names supported): ')
        userSearchList = userSearchRaw.split(',')
        
        for userSearchItem in userSearchList:
            userSearchItem = userSearchItem.strip() # Remove whitespace
            validClient = False
            if userSearchItem.isnumeric(): # Client ID
                for client in allClients:
                    if str(client['clientid']) in str(userSearchItem):
                        validClient = True
                        print(f'Client found: {client['name']}')
                        selectedClients += [client]
                        break
                if validClient == False:
                    logging.warning(f'No client with ID {userSearchItem} found.')
            else: # Try to find the client
                #TODO improve search function, name must be near perfect match right now
                matches = []
                logging.info(f'Searching for {userSearchItem}')
                for client in allClients:
                    logging.debug(f'Checking against {client['name']}')
                    if client['name'].lower().startswith(userSearchItem.lower()):
                        matches += [client]
                        logging.debug(f'MATCHED {client['name']} with search {userSearchItem}')
                
                if len(matches) == 0: # No names found
                    logging.warning(f'No clients found with search {userSearchItem}.')
                    
                elif len(matches) > 1: # Multiple matches, allow user to pick the right one
                    print(f'Multiple matches for {userSearchItem} found.')
                    sleep(.4)
                    while True:
                        count = 1
                        for match in matches:
                            print(f'[{count}] {match['name']}')
                            count +=1
                        print(f'[{count}] None of the above')
                        choice = input('Please choose: ')
                        if (choice.isnumeric() and (int(choice) -2) > len(matches)) or choice.isnumeric == False:
                            clearConsole()
                            print('Invlaid selection, please choose from the list below')
                        elif len(matches) +1 == int(choice): # User does not want any of the available options
                            clearConsole()
                            break
                        else:
                            selectedClients += [matches[int(choice)-1]]
                            break
                else:
                    selectedClients += [matches[0]]
        if selectedClients != []:
            print('The following clients will be checked')
            [print (client['name']) for client in selectedClients]# TODO clean this up a bit
            addMore = inputValidation('Would you like to add any additional clients? [Y/N]: ')
            clearConsole()
            if addMore == False:
                break
            
    clientsToCheck = selectedClients
else:
    clientsToCheck = allClients  
print('WARNING this will take a long time if you have alot of devices. Be patient.')

results = []
csvRows = []
for client in clientsToCheck:
    logging.info(f'Checking {client['name']}')
    devices = []
    if int(client['device_count']) == 0: # Skip clients with no devices
        logging.info(f'{client['name']} has no devices.')
        continue
    
    if int(client['workstation_count']) == 0: # Check for workstations
        logging.info(f'{client['name']} has no workstations.')
    else:
        devices += NAbleSession.clientDevices(clientid=client['clientid'],devicetype='workstation',includeDetails=True)['site']
    
    if int(client['server_count']) == 0: # Check for workstations
        print(f'{client['name']} has no servers.')
    else:
        devices += NAbleSession.clientDevices(clientid=client['clientid'],devicetype='server',includeDetails=True)['site']
    
    # Storing information
    client['results'] = []
    #TODO see if mobile devices can be checked
    if len(devices) == 0: # SHouldnt ever be hit, but adding as a safety
        print(f'{client['name']} has no devices.')
        continue
    
    for site in devices:
        for device in site['workstation' if 'workstation' in site.keys() else 'server']:
            deviceInfo = {'name':device['name'],
                          'presentChecks': []}
            if saveToCSV:
                csvDeviceRowBase = [client['name'],site['name'],device['name']] # Create device information for CSV file
                csvDeviceRowChecks = csvRowTemplate.copy() # Create blank rows to be edited later
            if int(device['checks']['@count']) == 0:
                print(f'{device['name']} has no checks!')
            else:
                for check in device['checks']['check']: # Check on device
                    if check['description'] in checkList: # Check from list is present on device
                        deviceInfo['presentChecks'] += [check['description']] # Add check to list
                        if saveToCSV:
                            listIndex = checkList.index(check['description'])
                            csvDeviceRowChecks.pop(listIndex)
                            csvDeviceRowChecks.insert(listIndex,'Present')
                    else:
                        for partialCheck in partialCheckList: # Look for partial matches
                            if check['description'].lower().startswith(partialCheck.lower()):
                                deviceInfo['presentChecks'] += [partialCheck]
                                if saveToCSV:
                                    listIndex = len(checkList) + partialCheckList.index(partialCheck)
                                    csvDeviceRowChecks.pop(listIndex)
                                    csvDeviceRowChecks.insert(listIndex,'Present')
            client['results'] += [deviceInfo]
            if saveToCSV:
                csvRows +=[csvDeviceRowBase + csvDeviceRowChecks] # Add device to CSV file


if saveToCSV:
    clearConsole()
    with open(csvFilename,'a') as csvF:
        csvwriter = csv.writer(csvF)
        csvwriter.writerows(csvRows)

    print('CSV file saved')
printResultsMode = inputValidation('Would you like results to pause for each device? (only devices with missing checks will be shown) [Y/N]: ')
for client in clientsToCheck: # Go through checks
    if 'results' not in client: # check that key is even present
        continue
    
    for device in client['results']:
        printQueue = []
        for check in device['presentChecks']:
            if check not in partialCheck and check not in checkList:
                printQueue += [check]
        if printQueue != []:
            print(f'{client['name']}: {device['name']} is missing {len(printQueue)} check(s)')
            [print(f'- {check}') for check in printQueue]
            if printResultsMode: # Pause if desired
                input('Press any key to continue')
