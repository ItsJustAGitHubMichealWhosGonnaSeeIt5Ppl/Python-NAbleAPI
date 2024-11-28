# NAble modules
# Will eventually add some better documentation

# Imports
import requests
import xmltodict
import os
from urllib.parse import urlencode


# CONSTANTS
## N-Able
NABLE_KEY = os.getenv("NABLE_KEY") 


class NAble:
    def _requester(self,mode,endpoint,rawParams=None):
        
        
        url = self.queryUrlBase + endpoint # Set URL for requests
        
        if rawParams!= None: # Format params
            paramsDict = self._formatter(rawParams)
        else:
            paramsDict = {}
        
        try:
            response  = requests.request(mode, url, params = paramsDict)
        except Exception as e:
            raise e
            
        # Error checking
        if response.status_code == 403: # invalid URL
            raise requests.exceptions.InvalidURL('invalid URL')
            print('Add an error here, URL is bad')
        elif response.status_code != 200: # Some other bad code
            raise Exception(f'Unknown response code {response.status_code}')
        
        else: # Valid URL 
            content = xmltodict.parse(response.content)['result'] # Response content
            try: # Check status
                status = content['@status']
            except KeyError: # Sometimes no status is sent, in which case assume its OK
                status = 'OK'
            
            if status == 'OK': # Valid key/request
                if 'describe' in paramsDict and paramsDict['describe']: # Check what type of response is being returned
                    #TODO maybe this should print out the information insteaed
                    return content['service']
                elif endpoint == 'list_device_monitoring_details': # Does not have items tag, is instead the devicetype
                    content 
                else:
                    return content['items']
            elif status == 'FAIL':
                if content['error']['errorcode'] == 3: # Login failed, invalid key
                    raise ValueError(f'Login failed.  You may be using the wrong regoin, or your API key is invalid')
                elif content['error']['errorcode'] == 4:
                    raise ValueError(f'{content['error']['message']}')
                else:
                    raise Exception(content['error']['message'])
            else:
                raise Exception(f'Unknown error: {status}')

    
    def __init__(self,region,key):
        """NAble Data Extraction API Wrapper
        
        Official Documentation: https://documentation.n-able.com/remote-management/userguide/Content/api_calls.htm
        
        Notes:
            If describe is set to True, the actual response will not be given, just a description of the service.

        Args:
            region (str): Your dashboard region (not all URLs have been verified)
            key (str): Your NAble API key

        """
        
        
        dashboardURLS = {
            'americas': 'dashboard.am.remote.management', # Unverified
            'asia': 'dashboardasia.system-monitor.com', # Unverified
            'australia': 'www.system-monitor.com', # Unverified
            'europe': 'dashboardeurope1.systemmonitor.eu.com', # Unverified
            ('france','fr'): 'www.systemmonitor.eu.com', # Unverified
            ('france1','fr1'): 'dashboardfrance1.systemmonitor.eu.com', # Unverified
            'germany': 'dashboardgermany1.systemmonitor.eu.com', # Unverified
            'ireland': 'www.systemmonitor.eu.com', # Unverified
            'poland': 'dashboardpoland1.systemmonitor.eu.com', # Unverified
            ('united kingdom','uk','gb'): 'www.systemmonitor.co.uk', # Verified
            ('united states','us','usa'): 'www.systemmonitor.us' # Verified
        }
        regionURL = None
        for regionName, url in dashboardURLS.items(): # Search URLs for matching region
            
            if isinstance(regionName,tuple): # Allows tupled items to be properly checked, otherwise us can be seen in australia
                regionName =list(regionName)
            else:
                regionName = [regionName]
            
            if region in regionName:
                regionURL = url
                break
        if regionURL == None:
            raise ValueError(f'{region} is not a valid region')
        
        self.queryUrlBase = f"https://{regionURL}/api/?apikey={key}&service=" # Key and service for use later
        
        try: # Test URL 
            testRequest = requests.get(self.queryUrlBase + 'list_clients') 
        except requests.exceptions.ConnectionError:
            raise requests.exceptions.ConnectionError('The request URL is not valid, this is an issue with the module. Pleae report your region and correct API url.')
            
        self._requester(endpoint='list_clients',mode='get')  # Test that key is valid.
        
    def _formatter(self,params):
        """Formats parameters for request

        Args:
            params (dict): Request parameters

        Returns:
            dict: URL Encoded request parameters
        """
        paramsToAdd = params # Shouldn't be needed, but had weird issues when it worked directly from the params before.
        
        popList = ['self','endpoint','includeDetails'] # Things that should not be added to params
        if 'describe' in paramsToAdd and paramsToAdd['describe'] != True: # Remove describe unless its true
            popList += ['describe']
            
        for popMe in popList:
            try: # Skips nonexistent keys
                paramsToAdd.pop(popMe)
            except KeyError:
                continue
        formattedData = {}
        
        for item, value in paramsToAdd.items(): # Check params, add anything that isn't blank to the query
            if value !=None:
                formattedData.update({item : value})
        return formattedData
        
    # Clients, Sites and Devices
    # https://documentation.n-able.com/remote-management/userguide/Content/devices.htm
    
    def clients(self,
        devicetype:str=None,
        describe:bool=False):
        """Lists all clients.  If devicetype is given, only clients with active devices matching that type will be returned.

        Args:
            devicetype (str, optional): Filter by device type [server, workstation, mobile_device]. Defaults to None.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: List of clients
        """
        response = self._requester(mode='get',endpoint='list_clients',rawParams=locals().copy())
        return response['client'] if describe != True else response

    def sites(self,
        clientid:int,
        describe:bool=False):
        """Lists all sites for a client.

        Args:
            clientid (int): Client ID
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: List of client sites
        """
        
        response = self._requester(mode='get',endpoint='list_sites',rawParams=locals().copy())
        return response['site'] if describe != True else response

    #TODO if only a single device is returned, it will be in DICT format instead of LIST (applies to server and workstation)
    def servers(self,
        siteid:int,
        describe:bool=None):
        """Lists all servers for site (including top level asset information if available).

        Args:
            siteid (int): Site ID
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: List of servers
        """
        
        
        response = self._requester(mode='get',endpoint='list_servers',rawParams=locals().copy())
        return response['server'] if describe != True else response

    
    def workstations(self,
        siteid:int,
        describe:bool=None):
        """Lists all workstations for site (including top level asset information if available).

        Args:
            siteid (int): Site ID
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: List of workstations
        """

        response = self._requester(mode='get',endpoint='list_workstations',rawParams=locals().copy())
        return response['workstation'] if describe != True else response
        

    def agentlessAssets(self,# Unclear what an output from this would look like
        siteid:int,
        describe:bool=False):
        """Lists all agentless and mini-agent asset devices for site (including top level asset information)

        Args:
            siteid (int): Site ID
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: List of agentless devices
        """
        
        response = self._requester(mode='get',endpoint='list_agentless_assets',rawParams=locals().copy())
        return response if describe != True else response
    

    def clientDevices(self,
        clientid:int,
        devicetype:str,
        describe:bool=False,
        includeDetails:bool=False):
    
        response = self._requester(mode='get',endpoint='list_devices_at_client',rawParams=locals().copy())
        if describe != True:
        
        
            if response == None:
                raise ValueError(f'{clientid} has no {devicetype} devices')
            else:
                clientDevices = response['client']
            
            if includeDetails == True: # Return devices with details
                if isinstance(clientDevices['site'], dict): 
                    clientDevices['site'] = [clientDevices['site']]
                for site in clientDevices['site']:
                    if isinstance(site,dict):
                        site = [site]
                    for siteDevices in site:
                        if isinstance(siteDevices[devicetype],dict):
                            siteDevices[devicetype] = [siteDevices[devicetype]]
                        
                        deviceList = []
                        for device in siteDevices[devicetype]:
                            
                            #Items which are not returneed in device details, but are in the overview (Why is there a difference?)
                            devStatus = device['status']
                            checkCount = device['checkcount']
                            webProtect = device['webprotection']
                            riskInt = device['riskintelligence']
                            device = self.deviceDetails(deviceid=device['id'])
                            # Re-add mising items
                            device['status'] = devStatus
                            device['checkcount'] = checkCount
                            device['webprotection'] = webProtect
                            device['riskintelligence'] = riskInt
                            deviceList+= [device]
                        siteDevices[devicetype] = deviceList
            return clientDevices
        else:
            return response 
    
    def deviceDetails(self,
        deviceid:int,
        describe:bool=False):
        
        response = self._requester(mode='get',endpoint='list_device_monitoring_details',rawParams=locals().copy())
        
        devType = list(response.keys())
        return response[devType[0]] if describe != True else response
    
    
    def addClient(self):
        pass
    
    def addSite(self):
        pass
    
    def siteInstallationPackage(self):
        pass

    # Checks and results
    def checks(self):
        pass

    def failingChecks(self):
        pass

    def checkConfig(self):
        pass
    
    def formattedCheckOutput(self):
        pass
    
    def outages(self):
        pass
    
    def performanceHistory(self):
        pass

    def driveSpaceHistory(self):
        pass
    
    def exchangeStorageHistory(self):
        pass
    
    def clearCheck(self):
        pass
    
    def addNote(self):
        pass

    def templates(self):
        pass

    # Antivirus Update Check Information
    
    def supportedAVs(self):
        pass

    def AVDefinitions(self):
        pass
    
    def AVDefinitionsReleaseDate(self):
        pass

    def AVHistory(self):
        pass
    
    # Backup Check History
    
    def backupHistory(self):
        pass

    # Asset Tracking Information
    # https://documentation.n-able.com/remote-management/userguide/Content/asset_tracking_information.htm
    
    def assetHardware(self):
        pass

    def assetSoftware(self):
        pass
    
    def licenseGroups(self):
        pass
    
    def licenseGroupItems(self):
        pass
    
    def clientLicenseCount(self):
        pass
    
    def assetLicensedSoftware(self):
        pass
        
    def assetDetails(self):
        pass
    
    # Settings
    
    def wallchartSettings(self):
        pass
    
    def generalSettings(self):
        pass
    
    # Windows Patch Management
    
    def listPatches(self):
        pass

    def approvePatches(self):
        pass

    def doNothingPatches(self):
        pass

    def ignorePatches(self):
        pass

    def reprocessPatches(self):
        pass

    def retryPatches(self):
        pass

if __name__ == '__main__':
    naybl = NAble('uk',NABLE_KEY)
    
    clients = naybl.clients()
    
    
    
    for client in clients:
        if int(client['device_count']) < 1: # Skip clients with no devices
            continue
        devices = naybl.clientDevices(clientid=client['clientid'],devicetype='workstation',includeDetails=True)
