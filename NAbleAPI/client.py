# NAble modules
# Will eventually add some better documentation

# Imports
import requests
import xmltodict

# # Known issues
# mobile devices do not work

#TODO Publish to PyPi
#TODO Add real documentation
#TODO Create usable scripts/tools
#TODO Add a changelog https://keepachangelog.com/en/1.0.0/




class NAble:
    """NAble Data Extraction API Wrapper
    Version: 0.0.1
        
    Official Documentation: https://documentation.n-able.com/remote-management/userguide/Content/api_calls.htm
    
    Notes:
        If describe is set to True, the actual response will not be given, just a description of the service.

    Args:
        region (str): Your dashboard region (not all URLs have been verified)
        key (str): Your NAble API key
    """
    def _requester(self,mode,endpoint,rawParams=None):
        """Make requests to NAble API

        Args:
            mode (str): Request mode [get,post,delete]
            endpoint (str): API endpoint URL
            rawParams (dict, optional): Parameters, copied from .local()

        Returns:
            dict: Partially formatted API response
        """
        
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
            if endpoint == 'get_site_installation_package' and ('describe' in paramsDict and paramsDict['describe'] != True): # Some items are returned as bytes object
                return response.content
            else: 
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
                    return content 
                else:
                    return content['items']
            elif status == 'FAIL':
                if int(content['error']['errorcode']) == 3: # Login failed, invalid key
                    raise ValueError(f'Login failed. Your region or API key is wrong.')
                elif int(content['error']['errorcode']) == 4:
                    raise ValueError(f'{content['error']['message']}')
                else:
                    raise Exception(content['error']['message'])
            else:
                raise Exception(f'Unknown error: {status}')

    
    def __init__(self,region,key):
        self.version = '0.0.1' # Remember to update the docstring at the top too!
        
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
    # Add Client, Add Site not yet working
    
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

    def servers(self,
        siteid:int,
        describe:bool=False):
        """Lists all servers for site (including top level asset information if available).

        Args:
            siteid (int): Site ID
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: List of servers
        """
        
        response = self._requester(mode='get',endpoint='list_servers',rawParams=locals().copy())
        if describe !=True and isinstance(response['server'],dict): # Make responses consistent
            response['server'] = [response['server']] # Fixes issue where a site with a single server would return as a dictionary.
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
        if describe !=True and isinstance(response['workstation'],dict): # Make responses consistent
            response['workstation'] = [response['workstation']] # Fixes issue where a site with a single workstation would return as a dictionary. #TODO consider moving this into the requester/response parser
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
        """Lists all devices of type 'server/workstation' for a client.

        Args:
            clientid (int): Client ID
            devicetype (str): Device type. [server, workstation, mobile_device]
            includeDetails (bool, optional): Include full device details for all devices. Defaults to False.
            describe (bool, optional): Returns a discription of the service. Defaults to False.
            

        Returns:
            list: All devices for a client
        """
    
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
        """Lists all monitoring information for the device (server or workstation)

        Args:
            deviceid (int): Device ID
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            dict: Full device details
        """
        
        response = self._requester(mode='get',endpoint='list_device_monitoring_details',rawParams=locals().copy())

        devType = 'workstation' if 'workstation' in response.keys() else 'server' # Allows device object to be returned as a dictionary
        return response[devType] if describe != True else response
    
    
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
        #TODO figure out if these are POST or GET requests (this one and sites)
        pass
    
    def addSite(self,
        clientid:int,
        sitename:str,
        router1:str=None,
        router2:str=None,
        workstationtemplate:str=None,
        servertemplate:str=None,
        describe:bool=False # Confirm this actually exists 
        ):
        pass
    
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
        """Lists all checks for device



        Args:
            deviceid (int): Device ID
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            list: List of device checks
        """
        
        response = self._requester(mode='get',endpoint='list_checks',rawParams=locals().copy())
        return response['check'] if describe != True else response
    
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
        return response if describe != True else response

    def checkConfig(self, #TODO test checkConfig
        checkid:int,
        describe:bool=False
        ):
        """Lists configuration for the specified check.

        Args:
            checkid (int): Check ID
            describe (bool, optional): Returns a discription of the service. Defaults to False.
        
        Returns:
            _type_: 
        """
        
        response = self._requester(mode='get',endpoint='list_check_config',rawParams=locals().copy())
        return response if describe != True else response
    
    def formattedCheckOutput(self, # TODO test formattedCheckOutput
        checkid:int,
        describe:bool=False
        ):
        """Returns formatted Dashboard More Information firstline result of check (error or otherwise)

        Args:
            checkid (int): Check ID
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            _type_: _description_
        """
        
        response = self._requester(mode='get',endpoint='get_formatted_check_output',rawParams=locals().copy())
        return response if describe != True else response
    
    def outages(self, #TODO test outages
        deviceid:int,
        describe:bool=False
        ):
        """Returns list of outages which are either still open, or which were closed in last 61 days.

        Args:
            deviceid (int): Device ID. 
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            _type_: _description_
        """
        
        
        response = self._requester(mode='get',endpoint='list_outages',rawParams=locals().copy())
        return response if describe != True else response
    
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
        return response if describe != True else response

    def driveSpaceHistory(self, #TODO test drive space history
        deviceid:int,
        interval:str,
        since:str=None,
        describe:bool=False
        ):
        """Returns the daily (interval=DAY), weekly (interval=WEEK) or monthly (interval=MONTH) disk space usage information for a device. Only available for devices which have active FREE_DRIVE_SPACE check(s).

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
        #TODO add a date standartisation system to replace theirs
        response = self._requester(mode='get',endpoint='list_drive_space_history',rawParams=locals().copy())
        return response if describe != True else response
    
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
        return response if describe != True else response
    
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
        return response if describe != True else response
    
    def addNote(self, #TODO test add note
        checkid:int,
        private_note:str=None,
        public_note:str=None,
        describe:bool=False
        ):
        """Add a public/private note to a check based on the provided public_note and/or private_note value.

        Args:
            checkid (int): Check ID
            private_note (str, optional): Private (technical) note. 
            public_note (str, optional): Public (customer) note. 
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            _type_: _description_
        """
        
        response = self._requester(mode='get',endpoint='add_check_note',rawParams=locals().copy())
        return response if describe != True else response

    def templates(self, #TODO test templates
        devicetype:str=None,
        describe:bool=False,          
        ):
        """List all of the account's server or workstation monitoring templates.

        Args:
            devicetype (str, optional): Device type [server, workstation].
            describe (bool, optional): Returns a discription of the service. Defaults to False.

        Returns:
            _type_: _description_
        """
        response = self._requester(mode='get',endpoint='list_templates',rawParams=locals().copy())
        return response if describe != True else response

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

    # Managed Antivirus
    
    def deviceMavQuarantine(self):
        pass
    
    def deviceMavQuarantineRelease(self):
        pass

    def deviceMavQuarantineRemove(self):
        pass
    
    def mavScanStart(self):
        pass
    
    def mavScanPause(self):
        pass
    
    def mavScanCancel(self):
        pass
    
    def mavScanList(self):
        pass
    
    def mavScans(self):
        pass
    
    def mavScanThreats(self):
        pass
    
    def mavUpdate(self):
        pass

    # Backup & Recovery
    def backupSelectionSize(self):
        pass
    
    def backupSessions(self):
        pass
    
    # Run task now
    
    def runTask(self):
        pass
    
    # List Active Directory Users
    
    def activeDirectoryUsers(self):
        pass
    