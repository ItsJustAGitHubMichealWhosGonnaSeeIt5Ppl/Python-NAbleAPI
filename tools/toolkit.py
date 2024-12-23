# Used by multiple tools
from NAbleAPI import NAble
import logging

def clearConsole(): # Clears the console
   print('\n' * 100)

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