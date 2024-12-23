# NAble modules
# Will eventually add some better documentation

# Imports
import requests
import xmltodict
import logging
from datetime import date,datetime

# # Known issues
# mobile devices may not work


#TODO add logger
#TODO add testing
#TODO Add typeddict or similar to document responses from items https://peps.python.org/pep-0589/
#TODO add reference ability for things like clientid, etc.
#TODO Document errors in readthedocs
#TODO fix bumpver
#TODO add siteDevices to get all site devices


class NAble:
    f"""NAble Data Extraction API Wrapper
    Version: 0.0.8
        
    Official Documentation: https://documentation.n-able.com/remote-management/userguide/Content/api_calls.htm
    
    Notes:
        If describe is set to True, the actual response will not be given, just a description of the service.

    Args:
        region (str): Your dashboard region (not all URLs have been verified)
        key (str): Your NAble API key
    """
    def _requester(self,mode,endpoint,rawParams=None):
        """Make requests to NAble API and do basic response handling. Also handles errors.

        Args:
            mode (str): Request mode [get,post,delete]
            endpoint (str): API endpoint URL
            rawParams (dict, optional): Parameters, copied from .local()

        Returns:
            dict: Partially formatted API response
        """
        
        url = self.queryUrlBase + endpoint # Set URL for requests
        
        if rawParams!= None: # Format params
            paramsDict = self._requestFormatter(rawParams)
        else:
            paramsDict = {}
        
        try:
            response  = requests.request(mode, url, params = paramsDict)
        except Exception as e:
            raise e
            
        # Error checking
        if response.status_code == 403: # invalid URL
            raise requests.exceptions.InvalidURL('invalid URL')
        
        elif response.status_code != 200: # Some other bad code
            raise Exception(f'Unknown response code {response.status_code}')
        
        #TODO figure out describe data and format it here
        
        else: # Valid URL
            if endpoint == 'get_site_installation_package' and ('describe' in paramsDict and paramsDict['describe'] != True): # Some items are returned as bytes object
                return response.content 
            elif 'describe' not in paramsDict or paramsDict['describe'] != True:
                return self._responseFormatter(response,endpoint=endpoint)
            else:
            
                try:
                    content = xmltodict.parse(response.content)['result'] # Response content
                except KeyError:
                    content = xmltodict.parse(response.content)
                except Exception as e: # BAD BAD BAD but maybe will help me figure out whats gone wrong here
                    raise e
                return content

    def __init__(self,region:str,key:str,logLevel:str=None,useOriginalValues:bool=True):
        """Intitialize your N-Sight instance.

        Args:
            region (str): Your tenant region, see wiki for complete list of regions.
            key (str): API key.
            logLevel (str, optional): Log Level. Defaults to normal level.
            useOriginalValues (bool, optional): Use Original values (keys and responses) in items. Names and values of some items in responses are confusing and onconsistent, so I have tried to clean them up and make them easier to use.  The downside to this is that NAbles documentation cannot be used when working with this library.  Anything that has been changed is documented in the ReadTheDocs for that method. Defaults to False (original names and values are kept).

        Raises:
            ValueError: _description_
            requests.exceptions.ConnectionError: _description_
        """
        
        self.version = '0.0.8' # Remember to update the docstring at the top too!
        self.useOgValues = useOriginalValues # Defaults to True
        self.session = requests.Session() #TODO test reuqets.session
        #TODO Make LogLevel actually do something
        
        dashboardURLS = {
            ('americas','ams'): 'www.am.remote.management', # Untested
            ('asia'): 'wwwasia.system-monitor.com', # Untested
            ('australia','au','aus'): 'www.system-monitor.com', # Untested
            ('europe','eu','eur'): 'wwweurope1.systemmonitor.eu.com', # Untested
            ('france','fr',): 'wwwfrance.systemmonitor.eu.com', # Untested
            ('france1','fr1'): 'wwwfrance1.systemmonitor.eu.com', # Untested
            ('germany','de','deu'): 'wwwgermany1.systemmonitor.eu.com', # Untested
            ('ireland','ie','irl'): 'wwwireland.systemmonitor.eu.com', # Untested
            ('poland','pl','pol'): 'wwwpoland1.systemmonitor.eu.com', # Untested
            ('united kingdom','uk','gb','gbr'): 'www.systemmonitor.co.uk', # Tested
            ('united states','us','usa'): 'www.systemmonitor.us' # Untested
        }
        regionURL = None
        for regionName, url in dashboardURLS.items(): # Search URLs for matching region
            
            if isinstance(regionName,tuple): # Allows tupled items to be properly checked, otherwise us can be seen in australia
                regionName =list(regionName)
            else:
                regionName = [regionName]
            
            if region.lower() in regionName: # Check regions. No longer case sensitive
                regionURL = url
                break
        if regionURL == None:
            raise ValueError(f'{region} is not a valid region')
        
        self.queryUrlBase = f"https://{regionURL}/api/?apikey={key}&service=" # Key and service for use later
        
        try: # Test URL 
            testRequest = self.session.get(self.queryUrlBase + 'list_clients') 
        except requests.exceptions.ConnectionError:
            raise requests.exceptions.ConnectionError('The request URL is not valid, this is an issue with the module. Pleae report your region and correct API url.')
            
        self._requester(endpoint='list_clients',mode='get')  # Test that key is valid.
        
    def _requestFormatter(self,params):
        """Formats parameters for request. Removes any parameter with value of None.

        Args:
            params (dict): Request parameters

        Returns:
            dict: URL Encoded request parameters
        """
        paramsToAdd = params # Shouldn't be needed, but had weird issues when it worked directly from the params before.
        
        popList = ['self','endpoint','includeDetails'] # Things that should not be added to params
        if 'describe' in paramsToAdd and paramsToAdd['describe'] != True: # Remove describe unless its true
            popList += ['describe']
        
        #TODO make the list to string converter generic
        if 'patchids' in paramsToAdd and isinstance(paramsToAdd['patchids'],list): # Reformat patchIDs sent as a list to a comma separated string.
            paramsToAdd['patchids'] = ','.join(map(str, paramsToAdd['patchids']))
        
        if 'guids' in paramsToAdd and isinstance(paramsToAdd['guids'],list): # Reformat GUIDs for AV sent as a list to a comma separated string.
            paramsToAdd['guids'] = ','.join(map(str, paramsToAdd['guids']))
            
        if 'details' in paramsToAdd:
            paramsToAdd['details'] = 'YES' if paramsToAdd['details'] == True else 'NO' # Fix details toggle for MAV
            
        for popMe in popList:
            try: # Skips nonexistent keys
                paramsToAdd.pop(popMe)
            except KeyError:
                continue
        formattedData = {}
        
        for item, value in paramsToAdd.items(): # Check params, add anything that isn't blank to the query
            
            if value !=None:
                if item == 'av': # Fix AV formatting
                    formattedData.update({'v' : 1 if value.lower() == 'vipre' else 2}) # Fix AV type
                else:
                    formattedData.update({item : value})
        return formattedData
    
    def _responseFormatter(self,response:any,endpoint:str=None): # Clean up response data. Only non-describe items should ever be sent here
        #TODO add docstring!
        #TODO add single item response handling either in this tool or for the method (when only a single item can ever be returned, a list would not be needed)
        needsWrapper = ['list_device_asset_details', # Responds with everything in a list, why in gods name?
                        ]
        
        # Getting and parsing raw response data from requests
        if endpoint == 'get_site_installation_package': # Some items are returned as bytes object
            content = response.content
        elif isinstance(response,requests.models.Response): # Check if object is a response from requests
            try:
                content = xmltodict.parse(response.content)['result'] # Response content
            except KeyError:
                content = xmltodict.parse(response.content)
            except Exception as e: # BAD BAD BAD but maybe will help me figure out whats gone wrong here
                raise e
        else:
            content = response

        try: # Check status
            status = content['@status']
        except KeyError: # Sometimes no status is sent, in which case assume its OK
            status = 'OK'
        
        if status == 'OK' or endpoint.startswith('mav'): # Valid key/request # Mav likes to return this shit #TODO fix this
            if 'items' in content: # Check for 'items' list in content keys.
                content = content['items']
        
        # Errors       
        elif status == 'FAIL': 
            if int(content['error']['errorcode']) == 3: # Login failed, invalid key
                raise ValueError(f'Login failed. Your region or API key is wrong.')
            elif int(content['error']['errorcode']) == 4: 
                #Invalid param, EG: bad checkid, bad deviceid.
                raise ValueError(f'{content['error']['message']}')
            else:
                raise Exception(content['error']['message'])
        else:
            raise Exception(f'Unknown error: {status}')

        #Wrap non-standard responses
        if endpoint in needsWrapper: # Fix responses that send everyhing at the "root"
            popMe = list()
            for item in content: # Pop unneeded things
                if item.startswith('@'):
                    popMe.append(item)
            for pop in popMe:
                content.pop(pop)
                
            content = {'wrapper': content} # Add the remaining items a dictionart
            
        endpointKeys = list()
        if content == None:
            return None
        else:
            for key, data in content.items(): # Fix data
                if isinstance(data,list):
                    endpointKeys.append(key)
                elif isinstance(data,dict):
                    content[key] = [content[key]]
                    endpointKeys.append(key)
        
        
        #Fixing keys with bad, inconsistent, or confusing names. ll items should at the very least have a note about where they appear.  Ideally details about why a change is being made should also be added
         #TODO should IDs for client, site, device, etc. be returned under the name "ID" for ease of use?
        betterKeyNames = {'workstationid':'deviceid', # Makes it easier to work with a large list of devices. Appears in workstations()
                          'serverid': 'deviceid', # Makes it easier to work with a large list of devices. Appears in servers()
                          }
        
        #TODO should these actually be lists instead?
        # Fixing values where they would be better suited as True/False or actual numbers. All items should at the very least have a note about where they appear.  Ideally details about why a change is being made should also be added.
        betterValueInfo = {'view_dashboard':bool, # Sent as '0' or '1'. Appears in clients() 
                           'view_wkstsn_assets':bool, # Sent as '0' or '1'. Appears in clients()
                           'dashboard_username': 'none', # DOES NOTHING RIGHT NOW. Should be replaced with Actual NoneType if 'none' in returned. Appears in clients()
                           'server_count':int, # Number but sent as string. Appears in clients()
                           'workstation_count':int, # Number but sent as string. Appears in clients()
                           'mobile_device_count':int, # Number but sent as string. Appears in clients()
                           'device_count': int, # Number but sent as string. Appears in clients()
                           'connection_ok': bool, # Appears in sites() 
                           'agent_mode': int, # Number but sent as string. Appears in workstations()
                           'online': bool, # Appears in workstations()
                           'active_247':bool, # Appears in workstations()
                           'creation_date':'date', # Appears in clients(), sites()
                           'workstationid': int, # Appears in workstations()
                           'serverid': int, # Appears in servers()
                           'install_date': 'date', # Appears in workstations(), servers(), assetSoftware()
                           'last_boot_time': 'timestamp', # Appears in workstations(), servers()
                           'dsc_active':bool, # Appears in workstations(), servers()
                           'processor_count':int, # Appears in workstations(), servers()
                           'assetid':int, # Appears in workstations(), servers()
                           'clientid':int, # Appears in clients()
                           'last_scan_time': 'datetime', # Appears in workstations(), servers()
                           'lastresponse': 'datetime', # Appears in deviceDetails()
                           'lastboot': 'datetime', # Appears in deviceDetails()
                           'utc_offset': int, # Appears in workstations(), servers()
                           'takecontrol': bool, # Appears in clientDevices()
                           'patch': bool, # Appears in clientDevices()
                           'mav': bool, # Appears in clientDevices()
                           'mob': bool, # Appears in clientDevices()
                           'systray': bool, # Appears in clientDevices()
                           'mavbreck': bool, # Appears in clientDevices()
                           'webprotection': bool, # Appears in clientDevices()
                           'riskintelligence': bool, # Appears in clientDevices()
                           'id':int, # Appears in clientDevices()
                           'osinstalldate':'datetime', # Appears in assetDetails()
                           'scantime':'datetime', # Appears in assetDetails()
                           'hardwareid': int, # Appears in assetHardware()
                           'email':bool, # Appears in listChecks()
                           'sms':bool, # Appears in listChecks()
                           'emailrecovery':bool, # Appears in listChecks()
                           'smsrecovery':bool, # Appears in listChecks()
                           'date':'custom', # Custom datetime for listChecks()
                           'checkid':int, # Appears in listChecks()
                           'consecutive_fails': int, # Appears in listChecks()
                           'utc_run':'datetimeUTC', # Appears in listChecks()
                           'utc_start':'datetimeUTC', # Appears in listOutages()
                           'utc_end':'datetimeUTC', # Appears in listOutages()
                           'outage_id':int, # Appears in listOutages()
                           'check_id':int, # Appears in driveSpaceHistory()
                           'templateid':int, # Appears in templates()
                           'show24x7problems':bool, # Appears in wallchartSettings()
                           'showdailysafetycheckproblems':bool, # Appears in wallchartSettings()
                           'showautomatedtaskproblems':bool, # Appears in wallchartSettings()
                           'includeoverdueservers':bool, # Appears in wallchartSettings()
                           'includeofflineservers':bool, # Appears in wallchartSettings()
                           'clear24x7checks':bool, # Appears in generalSettings()
                           'cleardailysafetychecks':bool, # Appears in generalSettings()
                           'forcenotes':bool, # Appears in generalSettings()
                           }
        
        if self.useOgValues:
            pass # Don't change any of the actual dictionary items
        else: # Fix them
            for endpKey in endpointKeys:
                if isinstance(content[endpKey], dict): # fix single object responses (put them in a list)
                    content[endpKey] = [content[endpKey]]
                for item in content[endpKey]:
                    keysToRemove = list()
                    toAdd = {}
                    for key, val in item.items(): # Iterate through each individual key/value pair
                        if key in betterKeyNames.keys(): 
                            keysToRemove.append(key) # Add to list of keys to be deleted
                            toAdd[betterKeyNames[key]] = val # Set value to better key name
                        if key in betterValueInfo.keys() and val !=None: #TODO is there a need for None to be allowed?
                            if betterValueInfo[key] == bool:
                                item[key] = bool(int(val)) # This may need some work
                            elif betterValueInfo[key] == int:
                                item[key] = int(val)
                            elif betterValueInfo[key] == 'date':
                                item[key] = datetime.strptime(val,'%Y-%m-%d').date()
                            elif betterValueInfo[key] == 'datetime':
                                item[key] = datetime.strptime(val,'%Y-%m-%d %H:%M:%S')
                            elif betterValueInfo[key] == 'timestamp':
                                item[key] = datetime.fromtimestamp(int(val))
                            elif betterValueInfo[key] == 'custom':
                                if endpKey == 'check': # check datetime combiner
                                    try:
                                        toAdd['last_run'] = datetime.strptime(f'{item['date']} {item['time']}','%Y-%m-%d %H:%M:%S')
                                    except ValueError: # Never run
                                        toAdd['last_run'] = None
                                    keysToRemove.append('date')
                                    keysToRemove.append('time')
                            elif betterValueInfo[key] == 'datetimeUTC':
                                item[key] = datetime.strptime(str(val +' UTC'),'%Y-%m-%d %H:%M:%S %Z')
                                    
                    if len(keysToRemove) > 0: # TODO gotta be a better way to do this
                        item.update(toAdd) # Add new items
                        for key in keysToRemove:
                            item.pop(key) # Remove redundant items
                    
        return content[endpointKeys[0]] if isinstance(endpointKeys,list) and len(endpointKeys) == 1 else content # Fix data
    
    

    # Clients, Sites and Devices
    # https://documentation.n-able.com/remote-management/userguide/Content/devices.htm
    # Add Client, Add Site not yet working
    
    def clients(self,
        devicetype:str=None,
        name:str=None,
        describe:bool=False):
        """Get all clients.  Optionally, filter by 'devicetype' and/or name.
        
        Device types
        - workstation
        - server
        - mobile_device

        Args:
            devicetype (str, optional): Filter by device type.
            name (str, optional): Filter/search for client by name. Helpful if trying to get a specific ID
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: List of clients
        """
        #TODO improve search
        #TODO cache client list
        #TODO Add IDONLY mode to return only a client anme and ID?
        response = self._requester(mode='get',endpoint='list_clients',rawParams=locals().copy())
        if describe != True and name != None and response !=True:
            popList = []
            for inxID, client in enumerate(response):
                if name.lower().strip() not in client['name'].lower().strip():
                    popList.append(inxID)
                    
            popList.reverse() # invert list so highest number is first.
            for pop in popList:
                response.pop(pop)
        return response

    def sites(self,
        clientid:int,
        describe:bool=False):
        """Get all sites for a client.

        Args:
            clientid (int): Client ID.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: List of client sites
        """
        
        response = self._requester(mode='get',endpoint='list_sites',rawParams=locals().copy())
        return response

    def servers(self,
        siteid:int,
        describe:bool=False):
        """Get all servers for site (including top level asset information if available).

        Args:
            siteid (:obj:`int`): Site ID.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: List of servers.
        """
        
        response = self._requester(mode='get',endpoint='list_servers',rawParams=locals().copy())
        return response

    def workstations(self,
        siteid:int,
        describe:bool=None):
        """Get all workstations for site (including top level asset information if available).
        
        This will NOT provide check information details.
        
        N-Able documentation: https://documentation.n-able.com/remote-management/userguide/Content/listing_workstations_.htm

        Args:
            siteid (:obj:`int`): Site ID.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: List of workstations.
        """

        response = self._requester(mode='get',endpoint='list_workstations',rawParams=locals().copy())
        return response
        
    def agentlessAssets(self,# Unclear what an output from this would look like
        siteid:int,
        describe:bool=False):
        """Get all agentless and mini-agent asset devices for site (including top level asset information)

        Args:
            siteid (:obj:`int`): Site ID.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: List of agentless devices.
        """
        
        response = self._requester(mode='get',endpoint='list_agentless_assets',rawParams=locals().copy())
        return response
    
    def clientDevices(self,
        clientid:int,
        devicetype:str,
        describe:bool=False,
        includeDetails:bool=False,
        experimentalChecks:bool=False
        ): # TODO allow filtering by site ID
        """Get all devices of type 'server/workstation' for a client.  Optionally, get their details.

        Args:
            clientid (:obj:`int`): Client ID.
            devicetype (str): Device type. [server, workstation, mobile_device].
            includeDetails (bool, optional): Include full device details for all devices. Defaults to False.
            experimentalChecks (bool, optional): Whether to try experimental checks. includeDetails must be True. More information can be found in the documentation. Defaults to False.
            describe (bool, optional): Returns a discription of the service. Defaults to False.
            

        Returns:
            list: All devices for a client.
        """
    
        response = self._requester(mode='get',endpoint='list_devices_at_client',rawParams=locals().copy())
        if describe != True:
            if response == None:
                raise ValueError(f'{clientid} has no {devicetype} devices')
            else:
                clientDevices = response[0]
            if isinstance(clientDevices['site'],dict):
                clientDevices['site'] = [clientDevices['site']]
            for site in clientDevices['site']:
                site = self._responseFormatter(site)
                if includeDetails == True:
                    deviceList = list()
                    for device in site:
                        #Items which are not returneed in device details, but are in the overview (Why is there a difference?)
                        devStatus = device['status']
                        checkCount = device['checkcount']
                        webProtect = device['webprotection']
                        riskInt = device['riskintelligence']
                        device = self.deviceDetails(deviceid=device['id'],experimentalChecks=experimentalChecks)
                        # Re-add mising items
                        device['status'] = devStatus
                        device['checkcount'] = checkCount
                        device['webprotection'] = webProtect
                        device['riskintelligence'] = riskInt
                        deviceList+= [device]
                    site = deviceList
            return clientDevices
        else:
            return response #TODO simplify this
    
    def deviceDetails(self,
        deviceid:int,
        experimentalChecks:bool=False,
        describe:bool=False):
        """Get all monitoring information for the device (server or workstation).  This information can also be gotten using the clientDevices() method.

        Args:
            deviceid (:obj:`int`): Device ID.
            experimentalChecks (bool, optional): Whether to try experimental checks. More information can be found in the documentation. Defaults to False.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            dict: Full device details
        """
        response = self._requester(mode='get',endpoint='list_device_monitoring_details',rawParams=locals().copy())[0]

        #TODO will this handle describe?
        if int(response['checks']['@count']) > 0 and isinstance(response['checks']['check'], dict): # Convert single check from dict to list for consistency
            response['checks']['check'] = [response['checks']['check']]
            
        if experimentalChecks: # Run experimental Checks
            edrCheck = int(self.edrPresent(deviceid)['installed'])
            response['edr'] = str(edrCheck) if self.useOgValues else bool(edrCheck) # Make value consistent with everything else, I know its dumb but whatever
            
        return response
    
    def addClient(self, 
        name:str,
        timezone:str=None,
        licenseconfig:str=None, #XML
        reportconfig:str=None, #XML
        officehoursemail:str=None,
        officehourssms:str=None,
        outofofficehoursemail:str=None,
        outofofficehourssms:str=None,
        describe:bool=False
        ):
        """Create a new client, must at least provide a name.

        Args:
            name (str): New client name.
            timezone (str, optional): Timezone if different than company. Available timezones can be found here: https://documentation.n-able.com/remote-management/userguide/Content/api_timezones.htm
            licenseconfig (str, optional): Xml license config.
            reportconfig (str, optional): Xml report config.
            officehoursemail (str, optional): Email for in hours alerts. 
            officehourssms (str, optional): SMS for in hours alerts. 
            outofofficehoursemail (str, optional): Email for out of hours alerts. 
            outofofficehourssms (str, optional): SMS for out of hours alerts.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            dict: Status and new client ID if successful. 
        """
        
        #TODO add error handling
        response = self._requester(mode='get',endpoint='add_client',rawParams=locals().copy())
        return response
    
    
    def addSite(self, 
        clientid:int,
        sitename:str,
        router1:str=None,
        router2:str=None,
        workstationtemplate:str='inherit',
        servertemplate:str=None,
        describe:bool=False
        ):
        """Create a new site for a client.

        Args:
            sitename (str): New Site Name.
            router1 (str, optional): Primary router IP address.
            router2 (str, optional): Secondary router IP address.
            workstationtemplate (str, optional): Template ID of default workstation template or "inherit" to inherit the site template. Defaults to inherit. A list of templates and their IDs can be gotten using templates()
            servertemplate (str, optional):  Template ID of default server template or "inherit" to inherit the site template. Defaults to inherit. A list of templates and their IDs can be gotten using templates()
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            dict:  Status and site ID is successful. 
        """
        #TODO add better error handling
        response = self._requester(mode='get',endpoint='add_site',rawParams=locals().copy())
        return response
    
    def siteInstallPackage(self,
        endcustomerid:int,
        siteid:int,
        os:str,
        type:str,
        beta:bool=False,
        mode:str=None,
        proxyenabled:bool=None,
        proxyhost:str=None,
        proxyport:int=None,
        proxyusername:str=None,
        proxypassword:str=None,
        describe:bool=False
        ):
        """Creates a Site Installation Package based on the specified installer type. Where successful a package is created and downloaded.
        
        
        Notes:
            By default this package is based on the latest General Availability Agent unless the beta=true parameter is used. In this case the Site Installation Package contains the current Release Candidate Agent.
        
            Support for Mac and Linux Site Installation Packages was introduced in Dashboard v2020.05.21. To maintain previously configured API calls, the Site Installation Package defaults to Windows where an os parameter is not provided.

        Args:
            endcustomerid (int): Client ID.
            siteid (int): Site ID.
            os (str): OS that package should be for [mac,windows,linux]
            type (str): Type of installer to download [remote_worker,group_policy]. Note: group_policy only works with Windows
            beta (bool, optional): Download the beta (RC) agent. Defaults to False.
            mode (str, optional): Mode [authenticate, downloadgp, downloadrwbuild]. Defaults to None.
            proxyenabled (bool, optional): (DEPRECATED) Use Proxy. Defaults to None.
            proxyhost (str, optional): (DEPRECATED) Proxy Host. Defaults to None.
            proxyport (int, optional): (DEPRECATED) Proxy Port. Defaults to None.
            proxyusername (str, optional): (DEPRECATED) Proxy username. Defaults to None.
            proxypassword (str, optional): (DEPRECATED)Proxy password. Defaults to None.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            bytes: raw bytes object.
        """
        
        response = self._requester(mode='get',endpoint='get_site_installation_package',rawParams=locals().copy())
        return response

    # Checks and results
    def checks(self,
        deviceid:int,
        describe:bool=False
        ):
        """Lists all checks for device.  Gets slightly more infromation than the device details.

        Args:
            deviceid (int): Device ID
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: List of checks for device
        """
        
        response = self._requester(mode='get',endpoint='list_checks',rawParams=locals().copy())
        return response
    
    def failingChecks(self,
        clientid:int=None,
        check_type:str=None,
        describe:bool=False
        ):
        """List all failing checks for all clients


        Args:
            clientid (int, optional): Client ID.
            check_type (str, optional): Check type [checks,tasks,random]. Random will return all failing checks
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: failing checks by client
        """
        
        response = self._requester(mode='get',endpoint='list_failing_checks',rawParams=locals().copy())
        return response

    def checkConfig(self,
        checkid:int,
        describe:bool=False
        ):
        """Lists configuration for the specified check.

        Args:
            checkid (int): Check ID
            describe (bool, optional): Returns a discription of the service. Defaults to False.
        
        Returns:
            dict: Single check configuration
        """
        
        response = self._requester(mode='get',endpoint='list_check_config',rawParams=locals().copy())
        return response
    
    def formattedCheckOutput(self,
        checkid:int,
        describe:bool=False
        ):
        """Returns formatted Dashboard More Information firstline result of check (error or otherwise)

        Args:
            checkid (int): Check ID
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            any: First line of check result (usually a string)
        """
        
        response = self._requester(mode='get',endpoint='get_formatted_check_output',rawParams=locals().copy())
        return response
    
    def outages(self,
        deviceid:int,
        describe:bool=False
        ):
        """Returns list of outages which are either still open, or which were closed in last 61 days.

        Args:
            deviceid (int): Device ID. 
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: List of outages
        """
        
        
        response = self._requester(mode='get',endpoint='list_outages',rawParams=locals().copy())
        return response
    
    def performanceHistory(self, #TODO test performance history
        deviceid:int,
        interval:int=15,
        since:str=None,
        describe:bool=False
        ):
        """Obtains the data relating to all the Performance and Bandwidth Monitoring Checks running on the specified device.

        Data is available for 24 hours at 15 minute intervals and for 8 days at hourly intervals. If data is needed for longer then it will need to be stored; for efficiency use the since parameter to only obtain new data.

        Note: The Windows Agent supports the Performance Monitoring Check for workstations.

        Args:
            deviceid (int): Device ID.
            interval (int, optional): Interval duration (in minutes). Valid options[15, 60]. 15 will get previous 24 hours, 60 will get up to 8 days. Defaults to 15.
            since (str, optional): Set a start date (ISO-8601). Defaults to None.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            _type_: _description_
        """
        
        response = self._requester(mode='get',endpoint='list_performance_history',rawParams=locals().copy())
        return response

    def driveSpaceHistory(self,
        deviceid:int,
        interval:str='DAY',
        since:str=None,
        describe:bool=False
        ):
        """Returns the daily , weekly or monthly disk space usage information for a device. Only available for devices which have active FREE_DRIVE_SPACE check(s).

        Args:
            deviceid (int): Device ID
            interval (str): Inverval length. [DAY, WEEK, MONTH]. Defaults to DAY
            since (str, optional): Set a start date (ISO-8601, format depends on interval).
            - DAY = [year]-[month]-[day]
            - WEEK = [year]W[week number]
            - MONTH = [year]-[month]
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            dict: Dict with drive letter and check ID, includes LIST (history) with historical information
        """
        
        #TODO add a date standartisation system to replace theirs
        response = self._requester(mode='get',endpoint='list_drive_space_history',rawParams=locals().copy())
        return response
    
    def exchangeStorageHistory(self, #TODO Find someone to test Exchange Space history
        deviceid:int,
        interval:str,
        since:str=None,
        describe:bool=False
        ):
        """Returns the daily (interval=DAY), weekly (interval=WEEK) or monthly (interval=MONTH) Exchange Store Size information for a device. Only available for devices where the (Windows server only) Exchange Store Size Check is configured.

        Args:
            deviceid (int): Device ID
            interval (str): Inverval length. [DAY,WEEK,MONTH]
            since (str, optional): Set a start date (ISO-8601, format depends on interval).
            - DAY = [year]-[month]-[day]
            - WEEK = [year]W[week number]
            - MONTH = [year]-[month]
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            _type_: _description_
        """
        response = self._requester(mode='get',endpoint='list_exchange_storage_history',rawParams=locals().copy())
        return response
    
    def clearCheck(self, #TODO test clearing check
        checkid:int,
        private_note:str=None,
        public_note:str=None,
        clear_type:str=None,
        clear_until:str=None,
        describe:bool=False
        ):
        """Clear a check status. After a check has failed, mark it as 'cleared', thereby acknowledging the cause of the failure.The check will be shown using an amber tick. A note describes the reason for the failure and the action taken by the engineer.

        This API call is only supported where Check Clearing is enabled on the account for this check frequency type, i.e. 24x7 and/or Daily Safety Check.
        
        Learn more about enabling check clearing here: https://documentation.n-able.com/remote-management/userguide/Content/configure_check_clearing.htm

        Notes

        Where the option to Prompt for notes when clearing failed checks is enabled in Settings > General Settings> Notes, both the public

        note (customer facing) and the private note (for engineers) must be non-empty.

        Any Check clearing action adds an entry in the User Audit Report.

        Args:
            checkid (int): Check ID.
            private_note (str, optional): Private (technical) note. 
            public_note (str, optional): Public (customer) note. 
            clear_type (str, optional): Action taken on clearing check untilpasses, untilnextrun, or untildatetime*. 
            clear_until (str, optional): *If untildatetime is selected as the clear_type then this date/time value is required to determine how long a check will be cleared until (ISO-8601). 
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            _type_: _description_
        """
        response = self._requester(mode='get',endpoint='clear_check',rawParams=locals().copy())
        return response
    
    def addNote(self,
        checkid:int,
        private_note:str=None,
        public_note:str=None,
        describe:bool=False
        ):
        """Add a public/private note to a check.  Check will be added by the admin account/account API key was retrieved from.

        Args:
            checkid (int): Check ID
            private_note (str, optional): Private (technical) note. 
            public_note (str, optional): Public (customer) note. 
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            dict: Confirmation of note being added
        """
        # TODO possibly make this return True/False depending on whether note is added or not
        #TODO why does this work with get?
        response = self._requester(mode='get',endpoint='add_check_note',rawParams=locals().copy())
        return response

    def templates(self, 
        devicetype:str=None,
        describe:bool=False,          
        ):
        """List all monitoring templates. Optionally, filter by device type.
        
        

        Args:
            devicetype (str, optional): Device type [server, workstation].
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: List of templates with template IDs. No details are provided.
        """
        response = self._requester(mode='get',endpoint='list_templates',rawParams=locals().copy())
        return response

    # Antivirus Update Check Information
    
    def supportedAVs(self, # TODO what is the point of this.
        describe:bool=False
        ):
        """Lists display name and identifier for all supported antivirus products.

        Args:
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: List of supported AVs with ID"""

        response = self._requester(mode='get',endpoint='list_supported_av_products',rawParams=locals().copy())
        return response

    def AVDefinitions(self,
        product:str, #TODO maybe allow search here and use supported AVs endpoint
        max_results:int=20,
        describe:bool=False):
        """Lists the most recent definition versions and date released for a given AV product.

        Args:
            product (str): AV product ID (can be retrieved with supportedAVs endpoint)
            max_results (int, optional): Max number of definitions to return. Defaults to 20.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: List of AV definitions with version and date released
        """

        response = self._requester(mode='get',endpoint='list_av_definitions',rawParams=locals().copy())
        return response
    
    def AVDefinitionsReleaseDate(self, # TODO what is the point of this if the date is already provided in the versions endpoint
            product:str, # TODO allow searching here?
            version:str, # TODO Allow 'latest' tag to be used instead of a version?
            describe:bool=False
        ):
        """Given an antivirus product ID and a definition version, returns the date and time a definition was released.


        Args:
            product (str): AV product ID (can be retrieved with supportedAVs endpoint)
            version (str): Version (can be retrieved with AVDefinitions endpoint)
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            dict: Product name, version, release date.
        """


        response = self._requester(mode='get',endpoint='get_av_definition_release_date',rawParams=locals().copy())
        return response
    
    def AVHistory(self, # TODO maybe allow date filtering here? #TODO why did it return 90?
        deviceid:int, # Claims string in documentation, but all others are int?
        describe:bool=False
        ):
        """List status of Antivirus Update Checks on device for last 60 days.

        Args:
            deviceid (int): Device ID
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: Previous 60 days AV status/history.  Will show status of "UNKNOWN" if AV is not enabled/running
        """

        
        response = self._requester(mode='get',endpoint='list_av_history',rawParams=locals().copy())
        return response
    
    # Backup Check History
    
    def backupHistory(self,
        deviceid:int,
        describe:bool=False
        ):
        """Lists status of backup (based on check) for the last 60 (or 90) days.
        Requires backup check to be present on device.
        Works with MoB/Cove.
        May not work with MacOS devices. 

        Args:
            deviceid (int): Device ID.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: Previous 60 days backup history.  Will show status of "UNKNOWN" if backup check is not present.
        """
        
        response = self._requester(mode='get',endpoint='list_backup_history',rawParams=locals().copy())
        return response
    
    # Asset Tracking Information
    # https://documentation.n-able.com/remote-management/userguide/Content/asset_tracking_information.htm
    
    def assetHardware(self, 
        assetid:int,
        describe:bool=False
        ):
        """Get all hardware for an asset.
        
        Included in each hardware item will be a hardware ID and hardware type.  Hardware types listed below
        
        Hardware Types:
        
        - 1: Network Adapter
        - 2: BIOS
        - 3: Sound device
        - 4: Motherboard
        - 5: Keyboard
        - 6: Pointing device
        - 7: Monitor
        - 8: Video Controller
        - 9: Disk Drive
        - 10: Logical Disk
        - 11: Physical Memory
        - 12: Cache Memory
        - 13: Processor
        - 14: Tape Drive
        - 15: Optical Drive
        - 16: Floppy Disk Drive (yes, really)
        
        Note: Manufacturer may show as None for some components on Apple devices.

        Args:
            assetid (int): Asset ID. Can be gotten in using workstations() under 'assetid' or by using assetDetails() with a device ID.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: List of asset hardware.
        """

        response = self._requester(mode='get',endpoint='list_all_hardware',rawParams=locals().copy())
        return response

    def assetSoftware(self,
        assetid:int,
        describe:bool=False
        ):
        """Get all software for an asset.
        
        Note:
        
        - Version and install date may not work on Apple devices.

        Args:
            assetid (int): Asset ID. Can be gotten in using workstations() under 'assetid' or by using assetDetails() with a device ID.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: List of asset software.
        """

        response = self._requester(mode='get',endpoint='list_all_software',rawParams=locals().copy())
        return response[0]
    
    def licenseGroups(self,
        describe:bool=False
        ):
        """Get all software license groups for account/tenant.

        Args:
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: List of license groups and IDs
        """

        response = self._requester(mode='get',endpoint='list_license_groups',rawParams=locals().copy())
        return response

    def licenseGroupItems(self,
        license_group_id:int,
        describe:bool=False
        ):
        """Get software in a software license group.

        Args:
            license_group_id (int): License Group ID.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            dict: License Software group information (very limited)
        """
        # TODO dig into this more, what is the point?
        response = self._requester(mode='get',endpoint='list_license_group_items',rawParams=locals().copy())
        return response
    
    def clientLicenseCount(self,
        clientid:int,
        describe:bool=False
        ):
        """Get client software license counts.

        Args:
            clientid (int): Client ID.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: License counts for software?
        """

        response = self._requester(mode='get',endpoint='list_client_license_count',rawParams=locals().copy())
        return response
    
    def assetLicensedSoftware(self, # TODO test assetLicensedSoftware (find an asset that is using this correctly)
        assetid:int,
        describe:bool=False
        ):
        """_summary_

        Args:
            assetid (int): Asset ID. Can be gotten in using workstations() under 'assetid' or by using assetDetails() with a device ID.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            _type_: _description_
        """

        response = self._requester(mode='get',endpoint='list_licensed_software',rawParams=locals().copy())
        return response
        
    def assetDetails(self, 
        deviceid:int,
        describe:bool=False
        ):
        """Get device asset details by device ID.
        
        Includes some software and hardware asset details.  These details are NOT the same as the ones provided from the dedicated endpoints!

        Args:
            deviceid (int): Device ID.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            dict: Asset details including asset ID, asset hardware, and asset software.
        """
        #TODO cleanup response as it contains @host, @status, and @created for some reason. Fucking why
        response = self._requester(mode='get',endpoint='list_device_asset_details',rawParams=locals().copy())
        return response[0]
    
    # Settings
    
    def wallchartSettings(self,
        describe:bool=False
        ):
        """Lists general Wall Chart settings for account including what should and shouldn't be shown.
        
        Args:
            describe (bool, optional): Returns a discription of the service. Defaults to False.
            
        Returns:
            dict: Wallchart settings.
        """
    
        response = self._requester(mode='get',endpoint='list_wallchart_settings',rawParams=locals().copy())[0]
        response = self._responseFormatter(response['wallchart'])
        response['servers'] = response['servers'][0]
        response['workstations'] = response['workstations'][0]
        return response

    def generalSettings(self,
        describe:bool=False
        ):
        """Lists general (basic) settings for account including language, whether checks can be cleared, and the timezone.
        
        Args:
            describe (bool, optional): Returns a discription of the service. Defaults to False.
            
        Returns:
            dict: General settings.
        """
        
        response = self._requester(mode='get',endpoint='list_general_settings',rawParams=locals().copy())
        response = self._responseFormatter(response[0]['items'])[0]
        return response

    # Windows Patch Management
    
    def listPatches(self, 
        deviceid:int,
        describe:bool=False
        ):
        """Get all patch information for a device using the device ID.
        
        Included in the response is the patch status, and the patch policy currently applied.  Below is a list of Polices, Status, and their IDs.
        
        Policies and IDs
        
        - Ignore: 1 or 65 if set by user (via API or dashbaord).  If you find a patch ignored by a policy, please send me the ID!
        - Approve: 2 or 66 if set by user (via API or dashbaord)
        - Do Nothing: 4 or 68 if set by user (via API or dashbaord)
        
        
        Statuses and IDs
        
        - Missing: 1
        - Pending: 2
        - Queued: 4
        - Installed: 8
        - Failed: 16
        - Ignored: 23
        - Reboot Required: 64
        
        If you find additional statuses or IDs, please let me know!

        Args:
            deviceid (int): Device ID
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: List of patches (both available and installed).
        """

        response = self._requester(mode='get',endpoint='patch_list_all',rawParams=locals().copy())
        return response
    
    #TODO figure out what should be returned for patch management calls since by default nothing is sent back. Maybe return the patch information from listPatches for the ones that were modified?
    def approvePatches(self,
        deviceid:int,
        patchids:list, # Comma separated
        describe:bool=False
        ):
        """Approve patch(es) for a specific device. Approving a patch that has already been approved does not cause an issue.  
        
        Patches set to Approve will install at the next scheduled installation time as set by the devices Patch Management policy.
        
        Patches that are approved using this will show policy ID 66 instead of 2.

        Args:
            deviceid (int): Device ID
            patchids (str,list): Patch ID(s).  Use a list or comma separated string to send multiple at once
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            dict: Nothing of value is returned. May remove this
        """

        response = self._requester(mode='get',endpoint='patch_approve',rawParams=locals().copy())
        return response

    def doNothingPatches(self,
        deviceid:int,
        patchids:str, # Comma separated
        describe:bool=False        
        ):
        """Set patch(es) to "Do Nothing" for a specific device.
        
        Patches set to "Do Nothing" will be installed according to the applied Patch Management policy.
        
        Patches that are changed using this will show policy ID 68 instead of 4.

        Args:
            deviceid (int): Device ID
            patchids (str,list): Patch ID(s).  Use a list or comma separated string to send more than 1 at once.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            dict: Nothing of value is returned.
        """
        
        response = self._requester(mode='get',endpoint='patch_do_nothing',rawParams=locals().copy())
        return response

    def ignorePatches(self,
        deviceid:int,
        patchids:str, # Comma separated
        describe:bool=False        
        ):
        """Ignore patch(es) for a specific device.
        
        Patches set to "Ignore" will be explicitely blocked (ignored) and will not show as "missing" in reports or dashboard.
        
        Patches that are changed using this will show policy ID of 65.

        Args:
            deviceid (int): Device ID
            patchids (str,list): Patch ID(s).  Use a list or comma separated string to send more than 1 at once.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            dict: Nothing of value is returned.
        """
        
        response = self._requester(mode='get',endpoint='patch_ignore',rawParams=locals().copy())
        return response

    def reprocessPatches(self,
        deviceid:int,
        patchids:str, # Comma separated
        describe:bool=False        
        ):
        """Reprocess failed patch(es) for a specific device.
        
        If a patch has reviously failed to install, use this to retry the install. Patches will attempt to install at the next scheduled installation time as set by the devices Patch Management policy.
        
        Failed Patches will show status ID 16. The policy ID will not change if a patch has failed to install. Patches that are changed using this will show their original polcy, and status ID 2 (pending)
        
        If you try to reprocess a patch that has not failed to install (installed, pending, ignored) you will get a response stating "Patches already applied: {PATCH IDS}".

        Args:
            deviceid (int): Device ID
            patchids (str,list): Patch ID(s).  Use a list or comma separated string to send more than 1 at once.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            str: Additional information (if any) about selected patches.
        """
        
        response = self._requester(mode='get',endpoint='patch_reprocess',rawParams=locals().copy())
        return response

    def retryPatches(self, # TODO confirm if this is any different than reprocess
        deviceid:int,
        patchids:str, # Comma separated
        describe:bool=False        
        ):
        """Retry failed patch(es) for a specific device. Appears to do exactply the same thing as reprocess, even provides the same messages.
        
        If a patch has reviously failed to install, use this to retry the install. Patches will try to install at the next scheduled installation time as set by the devices Patch Management policy.
        
        Failed Patches will show status ID 16. The policy ID will not change if a patch has failed to install. Patches that are changed using this will show their original polcy, and status ID 2 (pending)
        
        If you try to reprocess a patch that has not failed to install (installed, pending, ignored) you will get a response stating "Patches already applied: {PATCH IDS}".

        Args:
            deviceid (int): Device ID
            patchids (str,list): Patch ID(s).  Use a list or comma separated string to send more than 1 at once.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            str: Additional information (if any) about selected patches.
        """
        
        response = self._requester(mode='get',endpoint='patch_retry',rawParams=locals().copy())
        return response

    # Managed Antivirus
    # https://documentation.n-able.com/remote-management/userguide/Content/managed_antivirus2.htm
    
    def mavQuarantine(self, #TODO test actual response for this
        deviceid:int,
        av:str='bitdefender', 
        describe:bool=False
        ):
        """Get quarantined threats for a device.

        Args:
            deviceid (int): Device ID.
            av (str, optional): Specify which AV should be checked [vipre, bitdefender]. Defaults to bitdefender.
            describe (bool, optional): Returns a discription of the service. Defaults to False.
            

        Returns:
            list,none: List of quarantined items or None if nothing is quarantined
        """
        

        response = self._requester(mode='get',endpoint='mav_quarantine_list',rawParams=locals().copy())
        return response
    
    
    def mavQuarantineRelease(self, #TODO test mavQuarantineRelease
        deviceid:int,
        guids:str, # comma separated
        describe:bool=False
        ):
        """Release threat(s) from Managed Antivirus quarantine. 

        Args:
            deviceid (int): Device ID.
            guids (str): GUID(s) of quarantined threats. Use a list or comma separated string to send multiple at once.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            str: Status message (if any).  If no message is returned, assume successful.
        """

        response = self._requester(mode='get',endpoint='mav_quarantine_release',rawParams=locals().copy())
        return response

    def mavQuarantineRemove(self, #TODO test mavQuarantineRemove
        deviceid:int,
        guids:str, # comma separated
        describe:bool=False
        ):
        """Remove threat(s) from Managed Antivirus quarantine. 

        Args:
            deviceid (int): Device ID.
            guids (str): GUID(s) of quarantined threats. Use a list or comma separated string to send multiple at once.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            str: Status message (if any).  If no message is returned, assume successful.
        """

        response = self._requester(mode='get',endpoint='mav_quarantine_remove',rawParams=locals().copy())
        return response
    
    def mavScanStart(self,
        deviceid:int,
        describe:bool=False        
        ):
        """Start quick scan on a device. 
        
        Scan will not start immediately.  If a scan is already running, an error will be returned.
        
        Args:
            deviceid (int): Device ID.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            str: Status message (if any).  If no message is returned, assume successful. If a scan is already running, 'An error has occurred' may be returned.
        """
        
        response = self._requester(mode='get',endpoint='mav_scan_start',rawParams=locals().copy())
        return response
    
    def mavScanPause(self, 
        deviceid:int,
        describe:bool=False        
        ):
        """Pause scan on a device. 
        
        Scan will not be paused immediately.
        
        Args:
            deviceid (int): Device ID.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            str: Status message (if any).  If no message is returned, assume successful. If no scan is running, 'Unsupported action type' may be returned.
        """
        
        response = self._requester(mode='get',endpoint='mav_scan_pause',rawParams=locals().copy())
        return response
    
    def mavScanResume(self,
        deviceid:int,
        describe:bool=False        
        ):
        """Resume/unpause scan on a device. 
        
        Scan will not be resumed immediately.
        
        Args:
            deviceid (int): Device ID.
            describe (bool, optional): Returns a discription of the service. Defaults to False. If no scan is running, 'Unsupported action type' may be returned.

        Returns:
            str: Status message (if any).  If no message is returned, assume successful.
        """
        
        response = self._requester(mode='get',endpoint='mav_scan_resume',rawParams=locals().copy())
        return response
    
    def mavScanCancel(self,
        deviceid:int,
        describe:bool=False        
        ):
        """Cancel scan on a device. 
        
        Scan will not be cancelled immediately.
        
        Args:
            deviceid (int): Device ID.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            str: Status message (if any).  If no message is returned, assume successful. If no scan is running, 'An error has occurred' may be returned.
        """
        
        response = self._requester(mode='get',endpoint='mav_scan_cancel',rawParams=locals().copy())
        return response
    
    def mavScanList(self,
        deviceid:int,
        av:str='bitdefender', 
        describe:bool=False
        ):
        """Get a list of scans for a device. Scans currently running may not be included.

        Args:
            deviceid (int): Device ID.
            av (str, optional): Specify which AV should be checked [vipre, bitdefender]. Defaults to bitdefender.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: List of scans.
        """
        
        response = self._requester(mode='get',endpoint='mav_scan_device_list',rawParams=locals().copy())
        return response
    
    def mavScans(self,
        deviceid:int,
        details:bool=True,
        av:str='bitdefender', 
        describe:bool=False
        ):
        """Get a list of scans for a device, should include active scans (but sometimes it doesn't)
        
        This will return slightly different information than mavScanList() although I don't know why they aren't the same thing.

        Args:
            deviceid (int): Device ID.
            details (bool, optional): Wheter to provide extra details, including threats and errors. Defaults to True (yes).
            av (str, optional): Specify which AV should be checked [vipre, bitdefender]. Defaults to bitdefender.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: List of scans.
        """
        
        
        response = self._requester(mode='get',endpoint='list_mav_scans',rawParams=locals().copy())
        return response
    
    def mavThreats(self,
        deviceid:int,
        av:str='bitdefender', 
        describe:bool=False
        ):
        """Get the most recent occurence of each threat found on a device.
        
        These threats may or may not be in quarantine.

        Args:
            deviceid (int): Device ID.
            av (str, optional): Specify which AV should be checked [vipre, bitdefender]. Defaults to bitdefender.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: List of threats.
        """
        
        response = self._requester(mode='get',endpoint='list_mav_threats',rawParams=locals().copy())
        return response
    
    def mavQuarantineList(self, # TODO seems to return nothing?
            deviceid:int,
            items:str=None,
            av:str='bitdefender', 
            describe:bool=False
        ):
        
        response = self._requester(mode='get',endpoint='list_mav_quarantine',rawParams=locals().copy())
        return response
    
    def mavUpdate(self,
        deviceid:int,
        describe:bool=False
        ):
        """Update the bitdefender definitions on a device (does not work with Vipre)

        Args:
            deviceid (int): Device ID.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            str: Status message (if any).  If update is already pending 'There is already a MAV definition update pending' will be returned here.  If nothing is returned, assume successful.
        """
        
        response = self._requester(mode='get',endpoint='mav_definitions_update',rawParams=locals().copy())
        return response

    # Backup & Recovery
    def backupSelectionSize(self, #TODO Find someone to test backupSelectionSize
        cliendid:int,
        siteid:int,
        deviceid:int,
        year:int,
        month:int,
        describe:bool=False
        ):
        
        """Returns the Backup & Recovery - previously known as Managed Online Backup - (MOB) selection size for the specified device for the entered month and year combination. Please be aware that the backup values stated in this API call are in Bytes.

        Args:
            cliendid (int): Client ID.
            siteid (int): Site ID.
            deviceid (int): Device ID.
            year (int): Year.
            month (int): Month (00-12).
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            _type_: _description_
        """

        response = self._requester(mode='get',endpoint='mob/mob_list_selection_size',rawParams=locals().copy())
        return response
    
    def backupSessions(self, #TODO Find someone to test backupSessions
        deviceid:int,
        describe:bool=False
        ):
        """ists all Backup & Recovery - previously known as Managed Online Backup - (MOB) sessions for a device.

        Note: Backups are recorded in batches after the whole batch finishes; once recorded the information about all backup sessions is available for the lifespan of the device, whilst Backup & Recovery remains enabled.

        Please be aware that the backup values stated in this API call are in Bytes. 

        Args:
            deviceid (int): Device ID.
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            _type_: _description_
        """

        response = self._requester(mode='get',endpoint='list_mob_sessions',rawParams=locals().copy())
        return response
    
    # Run task now
    
    def runTask(self,
        checkid:int,
        describe:bool=False
        ):

        response = self._requester(mode='get',endpoint='task_run_now',rawParams=locals().copy())
        return response
    
    # List Active Directory Users
    
    def activeDirectoryUsers(self, #TODO Find someone to test activeDicectoryUsers.
        siteid:int,
        describe:bool=False
        ):

        response = self._requester(mode='get',endpoint='task_run_now',rawParams=locals().copy())
        return response

    # CUSTOM METHODS
    
    def edrPresent(self,
        deviceid:int
        ):
        """Check if EDR is present on a device.
        
        Note:
        
        - Install date and version may not work on Apple devices.
        - May not work at all on apple devices
        
        Args:
            deviceid (int): Device ID.

        Returns:
            dict: Whether EDR is installed, if EDR is installed a version and install date will also be provided
        """
        
        edrNames = ['Sentinel Agent','SentinelOne Extensions'] 
        edrCatIDs = ['2244686'] # 2244686 = Mac ID
        
        response = {'installed': False, # Create response object and set information to False/None for consistency
                    'version': None,
                    'installDate':None} 
        assetSoftware = self.assetDetails(deviceid=deviceid)#
        if assetSoftware['software']:
            for software in assetSoftware['software']['item']: # scan through software
                if software['name'] in edrNames and software['deleted'] == '0': # EDR is on the list and not marked as deleted:
                    response['installed'] = True
                    response['version'] = software['version']
                    response['installDate'] = software['install_date']
                    break
        #TODO add warning here about missing EDR check
        return response


    
#class Patches(NAble): # TODO move Patch management to its own class?
#    pass