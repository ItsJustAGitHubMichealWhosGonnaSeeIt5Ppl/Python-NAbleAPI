# Used by multiple tools
from NAbleAPI import NAble
import logging
from time import sleep
from datetime import date
import csv
import os
from typing import Optional
from NAbleAPI.nsight_dataclasses import Client, Clients

def clearConsole(): # Clears the console
   print('\n' * 100)
   
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

def NSightFromEnv(region:str = 'uk', env_name:str="NABLE_KEY",useOriginalValues:bool=False):
    NABLE_KEY = os.getenv(env_name)
    assert isinstance(NABLE_KEY, str)
    return NAble(region, NABLE_KEY, useOriginalValues=useOriginalValues)

def authNSight(existingSettings=None):
    loop = 0
    while True:
        if loop == 10:
            print('I believe in you')
        elif loop == 100:
            print('I\'m losing hope')
        
        # get key and region
        if loop == 0 and existingSettings != None and existingSettings[1]['key'] != None: # Use saved settings (only try once)
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
    return NAbleSession


def selectClients(clientList:list[Client]):
    """Allow user to select client(s)

    Args:
        clientList (list): List of clients. 
        
    Returns:
        _type_: _description_
    """
    selectedClients = []
    if not clientList:
        from typing import Optional

    allClients = clientList # get all clients
    while True:
        userSearchRaw = input('Please enter the IDs or name of the clients you want to check (comma separated, mix of IDs and names supported): ')
        userSearchList = userSearchRaw.split(',')
        
        for userSearchItem in userSearchList:
            userSearchItem = userSearchItem.strip() # Remove whitespace
            validClient = False
            if userSearchItem.isnumeric(): # Client ID
                for client in allClients:
                    if str(client.clientid) in str(userSearchItem):
                        validClient = True
                        print(f'Client found: {client.name}')
                        selectedClients += [client]
                        break
                if validClient == False:
                    logging.warning(f'No client with ID {userSearchItem} found.')
            else: # Try to find the client
                #TODO improve search function, name must be near perfect match right now
                matches = []
                logging.info(f'Searching for {userSearchItem}')
                for client in allClients:
                    logging.debug(f'Checking against {client.name}')
                    if client.name.lower().startswith(userSearchItem.lower()):
                        matches += [client]
                        logging.debug(f'MATCHED {client.name} with search {userSearchItem}')
                
                if len(matches) == 0: # No names found
                    logging.warning(f'No clients found with search {userSearchItem}.')
                    
                elif len(matches) > 1: # Multiple matches, allow user to pick the right one
                    print(f'Multiple matches for {userSearchItem} found.')
                    sleep(.4)
                    while True:
                        count = 1
                        for match in matches:
                            print(f'[{count}] {match.name}')
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
            [print (client.name) for client in selectedClients]# TODO clean this up a bit
            addMore = inputValidation('Would you like to add any additional clients? [Y/N]: ')
            clearConsole()
            if addMore == False:
                break
    return selectedClients


def simpleCSVCreator(filename:str, fields:list): # Creates CSVs
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

def getDevicesForClients(nsight, clients:Optional[list]=None): # Get all devices for clients, does not include device details
    if clients == None: # More explicit
        clients = nsight.clients()
        
    clientDevices = list() 
    for client in clients:
        logging.info(f'Checking {client.name}')
        siteDevices = []
        if int(client.device_count) == 0: # Skip clients with no devices
            logging.info(f'{client.name} has no devices.')
            continue
        
        if int(client.workstation_count) == 0: # Check for workstations
            logging.info(f'{client.name} has no workstations.')
        else:
            siteDevices += nsight.clientDevices(clientid=client.clientid,devicetype='workstation').sites

        if int(client.server_count) == 0: # Check for workstations
            print(f'{client.name} has no servers.')
            
        else:
            siteDevices += nsight.clientDevices(clientid=client.clientid,devicetype='server').sites
        
        clientDevices.append({'client':client, 
                              'devices':siteDevices})
        
    return clientDevices