# NAble Data Extraction API wrapper/Library

This is a Python wrapper/library for the NAble Data Extraction API.  The NAble API returns data in xml format, this tool will convert those to lists and dictionaries for ease of use.

The official API documentation from NAble can be found [here](https://documentation.n-able.com/remote-management/userguide/Content/api_calls.htm). I have tried to keep my naming scheme similar to theirs.

NOTE:  
- This is still in extremely early stages of development, names may change! 
- Most functions have docstrings, but proper documentation has not yet been created.

## Table Of Contents
*I don't know how to make this yet, so it's Coming Soon*


## Installation

Will be published on PyPi, for now just download the whole project


## Getting Started

To use the NAble API, you will need to know your region and have an API key.

1. Download the package (this entire github) and extract it.
2. Get an API key. Follow [these instructions](https://documentation.n-able.com/remote-management/userguide/Content/api_key.htm) to get your API key.
3. Find your region (see below)


### Regions

To find your region, check [this page](https://documentation.n-able.com/remote-management/userguide/Content/determine_url.htm) or view table below. 

Notes: 
- Not all regions have been tested, if your region is marked 'untested' on the table below, please let me know whether or not it works.
- If your dashboard URL starts with `www2`, assume it is just `www` for the region.
- If there is another abbreviation or country code you would like added, let me know!

| Dashboard URL | Region | Status |
| --- | --- | --- |
| www.am.remote.management | americas, ams | Untested |
| wwwasia.system-monitor.com | asia | Untested |
| www.system-monitor.com | australia, au, aus | Untested |
| wwweurope1.systemmonitor.eu.com | europe, eu | Untested |
| wwwfrance.systemmonitor.eu.com | france, fr | Untested |
| wwwfrance1.systemmonitor.eu.com | france1, fr1 | Untested |
| wwwgermany1.systemmonitor.eu.com | germany, de, deu | Untested |
| wwwireland.systemmonitor.eu.com | ireland, ie, irl | Untested |
| wwwpoland1.systemmonitor.eu.com | poland, pl,pol | Untested |
| www.systemmonitor.co.uk | united kingdom, uk, gb, gbr | **Verified** |
| www.systemmonitor.us | united states, us, usa | Untested |

### Using the package

Once you've downloaded and extracted the package, you can start using it. (This will be better when it's properly uploaded, sorry)

#### Create a new .py file in the root directory and import the NAble package
```
from NAbleAPI import NAble
```

#### Authenticate with your API key
```
na = NAble('[YOUR REGION]','[YOUR API KEY]')
```

Example

```
na = NAble('uk','f821213a8d3q43843dj39824')
```

(Not a real API key, don't try to use it)


#### Make your first request
Gee it sure would be helpful is there was documentation for the available commands.  Unfortunately, there isn't right now.

Get all your clients

```
myNAbleClients = na.clients()
```


#### Storing your key
Its probably best not to store your API key in your script. Instead, you can create a .env file and use that.

1. Create a new file called `.env` in the root directory
2. Put your API key in it (do not put it in quotes, type exactly as shown below)
```
NABLE_KEY = f821213a8d3q43843dj39824
```
3. Get the key from file
``` 
from NAbleAPI import NAble # Import the NAble package
import os # Import OS package (built into Python, I'm like 99% sure)

NABLE_KEY = os.getenv("NABLE_KEY")

na = NAble('uk',NABLE_KEY)
```

## API Endpoints
The endpoints are grouped by category on NAble's website, so I have done the same below.
I found the names on NAbles site to be a bit long, so I have shortened them a bit. The `Function Name` is what you will use in Python.
I'm doing my best to get them all added!



### Clients, SItes, and Devices 
Official NAble documentation page [here](https://documentation.n-able.com/remote-management/userguide/Content/devices.htm)
| Service | Status | Function Name | Description |
| --- | --- | --- | --- |
| list_clients | Working | clients() | List all clients |
| list_sites | Working | sites() | List sites for a client |
| list_servers | Working | servers() | list servers at a site |
| list_workstations | Working | workstations() | list workstations at a site |
| list_agentless_assets | Working | agentlessAssets() | List agentless assets at a site |
| list_devices_at_client | Working | clientDevices() | List all workstations or servers for a client |
| list_device_monitoring_details | Working | deviceDetails | Get details for a single device | 
| add_client | Planned | addClient | Add a client |
| add_site | Planned | addSite | Add a site | 
| get_site_installation_package | Partially Working | siteInstallPackage | Create/Get a site installation package (returns rawbytes right now) |

### Checks and results
Official NAble documentation page [here](https://documentation.n-able.com/remote-management/userguide/Content/checks_and_results.htm)
| Service | Status | Function Name | Description |
| --- | --- | --- | --- |
| list_failing_checks | Untested | failingChecks() | List all failing checks |
| list_checks | Untested | checks() |  List all checks for a device |
| list_check_config | Untested | checkConfig() | Get a single checks configuration |

### Anti-Virus Update Check Information
Official NAble documentation page [here](https://documentation.n-able.com/remote-management/userguide/Content/api_av_info.htm)


### List Backup Check History
Official NAble documentation page [here](https://documentation.n-able.com/remote-management/userguide/Content/list_backup_history.htmm)


### Asset Tracking Information
Official NAble documentation page [here](https://documentation.n-able.com/remote-management/userguide/Content/asset_tracking_information.htm)


### Settings
Official NAble documentation page [here](https://documentation.n-able.com/remote-management/userguide/Content/settings.htm)


### Patch Management
Official NAble documentation page [here](https://documentation.n-able.com/remote-management/userguide/Content/patch_management.htm)


### Managed Anti-Virus
Official NAble documentation page [here](https://documentation.n-able.com/remote-management/userguide/Content/managed_antivirus2.htm)


### Backup & Recovery
Official NAble documentation page [here](https://documentation.n-able.com/remote-management/userguide/Content/api_mob_over.htm)


### Run Task Now
Official NAble documentation page [here](https://documentation.n-able.com/remote-management/userguide/Content/run_task_now.htm)


### List Active Directory Users
Official NAble documentation page [here](https://documentation.n-able.com/remote-management/userguide/Content/list_active_directory_users.htm)




### Literally everything else
Planned!
