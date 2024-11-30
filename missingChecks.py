# Find missing checks

from NAbleAPI import NAble
from time import sleep
import csv
from datetime import date,datetime
#TODO add a visual interface or enhanced commandline with curses.
#TODO add a logger
#TODO Allow use of existing csv file for check names
#TODO add option to save settings

toolVer = '0.0.1'
compatibleWith = '0.0.1' # Compatible version of package

def clearConsole(): # Clears the console
  print('\n' * 100)
  
def inputValidation(text,validOptions=['yes','y','no','n'],returnBool=True,timeout=10):
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

def simpleCSVCreator(filename,fields):
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
    
print(f'Missing Check Finder Tool\nVersion: {toolVer}\n This tool is used to find missing checks on your devices!')

loop = 0
while True:
    if loop == 10:
        print('I believe in you')
    elif loop == 100:
        print('I\'m losing hope')
    
    # get key and region
    userRegion = input('Please enter your region (regions can be found at the package wiki): ')
    api_key = input('Please enter your API key: ')

    # Set up nable
    try:
        NAbleSession = NAble(region=userRegion,key=api_key)
        break
    except Exception as e:
        clearConsole()
        print(f'[ERROR] {e}')
    loop +=1

clearConsole()
print('Successfully Connected')

#TODO Fix partial name check
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

if checkList == []:
    pass
else:
    checkList.sort()
    print('Looking for the following checks')
    for check in checkList:
        print(check)
input('Press any key to continue')
# TODO allow list to be edited here
clearConsole()

if partialCheckList == []: # Skip empty list, not sure this is needed. #TODO is this needed?
    pass
else:
    partialCheckList.sort() # Sort lists
    print('Looking for the following partial match checks')
    for check in partialCheckList:
        print(check)
input('Press any key to continue')
clearConsole()


saveToCSV = inputValidation('Would you like to save the output of this scan to a CSV? [Y/N]: ')
if saveToCSV: 
    csvRowTemplate = []
    for i in range(len(checkList)+len(partialCheckList)): 
        csvRowTemplate += ['Missing'] # Create blank check row
    
    print('CSV will be created root directory')
    csvName = 'missing_checks'
    csvFields = ['Customer', 'Site', 'Device'] + checkList + partialCheckList
    csvFilename = simpleCSVCreator(csvName,csvFields) #CSV Filename
else:
    clearConsole()


checkAll = inputValidation('Would you like to check all clients? [Y/N]: ')
allClients = NAbleSession.clients() # get all clients
#TODO Test client selection system via text

if checkAll == False: # Checking a specific client
    #TODO allow multiple clients to checked
    selectedClient = None
    while True:
        clientInp = input('Please enter the ID or name of the client you want to check: ') # TODO allow multiple customers to be added here (comma separated)
        if clientInp.isnumeric(): # Client ID
            validClient = False
            for client in allClients:
                if str(clientInp) == str(client['clientid']):
                    validClient = True
                    print(f'Client found: {client['name']}')
                    selectedClient = client
                    break
            if validClient == False:
                clearConsole()
                print(f'No client with ID {clientInp} found.')
                
            
        else: # Try to find the client
            
            #TODO improve search function, name must be near perfect match right now
            matches = []
            for client in allClients:
                if client['name'].lower().startswith(clientInp.lower()):
                    matches += [client]
            
            if len(matches) == 0: # more than 1 name found
                clearConsole()
                print(f'No clients found with search {clientInp}. Please try again.')
            elif len(matches) > 1: # Multiple matches, allow user to pick the right one
                clearConsole()
                print(f'Multiple matches for {clientInp} found.')
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
                        selectedClient = matches[choice-1]
                        break
        if selectedClient != None: # Client found, move on
            break


print('WARNING this will take a long time if you have alot of devices. Be patient.')
if checkAll == False:
    clientsToCheck = [selectedClient]
else:
    clientsToCheck = allClients
csvRows = []
for client in clientsToCheck:
    print(f'Checking {client['name']}')
    clearConsole()
    devices = []
    if int(client['device_count']) == 0: # Skip clients with no devices
        print(f'{client['name']} has no devices.')
        continue
    
    if int(client['workstation_count']) == 0: # Check for workstations
        print(f'{client['name']} has no workstations.')
    else:
        devices += NAbleSession.clientDevices(clientid=client['clientid'],devicetype='workstation',includeDetails=True)['site']
    
    if int(client['server_count']) == 0: # Check for workstations
        print(f'{client['name']} has no servers.')
    else:
        devices += NAbleSession.clientDevices(clientid=client['clientid'],devicetype='server',includeDetails=True)['site']
    
    #TODO see if mobile devices can be checked
    if len(devices) == 0: # SHouldnt ever be hit, but adding as a safety
        print(f'{client['name']} has no devices.')
        continue
    
    for site in devices:
        for device in site['workstation' if 'workstation' in site.keys() else 'server']:
            csvDeviceRowBase = [client['name'],site['name'],device['name']] # Create device information for CSV file
            csvDeviceRowChecks = csvRowTemplate.copy() # Create blank rows to be edited later
            if int(device['checks']['@count']) == 0:
                print(f'{device['name']} has no checks!')
            else:
                for check in device['checks']['check']: # Check on device
                    if check['description'] in checkList: # Check from list is present on device
                        listIndex = checkList.index(check['description'])
                        csvDeviceRowChecks.pop(listIndex)
                        csvDeviceRowChecks.insert(listIndex,'Present')
                    else:
                        for partialCheck in partialCheckList: # Look for partial matches
                            if check['description'].lower().startswith(partialCheck.lower()):
                                listIndex = len(checkList) + partialCheckList.index(partialCheck)
                                csvDeviceRowChecks.pop(listIndex)
                                csvDeviceRowChecks.insert(listIndex,'Present')
            csvRows +=[csvDeviceRowBase + csvDeviceRowChecks] # Add device to CSV file
with open(csvFilename,'a') as csvF:
    csvwriter = csv.writer(csvF)
    csvwriter.writerows(csvRows)
print('CSV file completed')
    #TODO add printout here, maybe put a delay on it?
            

        