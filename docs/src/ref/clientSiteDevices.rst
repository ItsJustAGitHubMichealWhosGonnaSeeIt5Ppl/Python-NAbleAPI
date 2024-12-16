
.. currentmodule:: NAbleAPI
.. toctree::
    :maxdepth: 2
    :hidden:
    :caption: Clients, Sites, and Devices

Available "endpoints"

'Describe' available on most devices, this allows you to get a description of the endpoint, instead of the actual endpoint results.

Clients and Sites
==================
These functions allow you to interact with your clients and sites.

Official documentation (needs link)

List Clients
-------

.. automethod:: NAble.clients

Example Client Item::

     {'name': 'A Name', # Client Name
     'clientid': '12345', # Client ID
     'view_dashboard': '0', # Whether dashboard access is enabled for client (0 = no, 1 = yes)
     'view_wkstsn_assets': '0', # Whether client can view workstations and assets. If set to 0 (no) only servers are visible, view_dashboard must be 1.
     'dashboard_username': 'none', # Username to access dashboard (if applicable)
     'timezone': None, # Timezone (None if not set)
     'creation_date': '2022-01-09', # Date client was created
     'server_count': '0', # server devices count
     'workstation_count': '1', # workstation devices count
     'mobile_device_count': '0', # mobile devices count
     'device_count': '1' # Total devices
     }

Add Client
----------

.. automethod:: NAble.addClient


List Sites
-----

.. automethod:: NAble.sites

Example Site Item::

    [
    {'siteid': '12344', # Site ID
    'name': 'Name', # Site Name
    'connection_ok': '1', # In the event that one or more servers at that site have stopped sending data, have we been able to reach the site (0 = no, 1 = yes)
    'creation_date': None, # Date site was created
    'primary_router': None, # IP address or hostname of primary router at site (can be blank)
    'secondary_router': None # IP address or hostname of secondary router at site if dual routing used (can be blank)
    }]

Add Site
----------

.. automethod:: NAble.addSite



Devices
=======
These functions allow you to interact with your devices

List Servers
-------

.. automethod:: NAble.servers

List Workstations
------------

.. automethod:: NAble.workstations

Example Workstation (Windows) Item::

    [{'guid': '123rd23', # Device GUID (device uses this to authenticate)
    'name': 'DESKTOP-123', # Computer Name (set in Windows)
    'description': 'Steves Computer', # Description (Set in NAble)
    'install_date': '1997-01-01', # Date agent was initially installed (not updated)
    'last_boot_time': '1733834559', # Unix timestamp for last boot time OR "Not Available" if last boot time not available.  May add some filtering for this in the future.
    'dsc_active': '1', # Whether daily safety checks are active and running  (0 = no, 1 = yes)
    'atz_dst_date': '0000-03-05:00T01:00:00', # When Daylist Savings time begins for device.
    'utc_apt': '2024-12-10 12:18:52', # The Agent perceived UTC time (what?)
    'utc_offset': '0', UTC offset for device in seconds (if any)
    'user': 'DESKTOP-123\\steveC', # User logged in when last scan was run.
    'domain': 'stevedoors.local', # Domain (if applicable)
    'manufacturer': 'DELL', # Computer manufacturer
    'model': 'Real Computer1', # Computer Model
    'ip': '192.168.1.95', # Computer internal IP
    'external_ip': '123.45.67.890', # Computer external IP
    'mac1': '0:11:22:33:44:55', # Computer MAC address
    'mac2': '0:11:22:33:44:55', # Computer secondary MAC address (if available)
    'mac3': None, # Computer third MAC address (if available)
    'os': 'Microsoft Windows 10 Pro', # Operating System (Returns device.osversion if no as_device record?)
    'os_details': 'Microsoft Windows 10 Pro, 64-bit (build 19045)', # Operating System information/Version (if available)
    'workstationid': '293334', # Device ID (used to get more details)
    'agent_version': '10_13_8', # Agent version
    'agent_mode': '1', # Agent mode
    'online': '1', # Unsure (devices that are offline still show this as 1)
    'active_247': '1', # Whether any 24/7 checks are active
    'check_interval_247': '60', # How often 24/7 checks will run
    'status_247': '5', # How many active 24/7 checks are on the current device.
    'local_date_247': '2024-12-10', 
    'local_time_247': '12:18:52', 
    'utc_time_247': '2024-12-10 12:18:57', 
    'dsc_hour': '6', 
    'dsc_status': '1', 
    'dsc_local_date': '2024-12-10', 
    'dsc_local_time': '06:02:22', 
    'dsc_utc_time': '2024-12-10 06:02:22', 
    'tz_bias': '0', 
    'tz_dst_bias': '-60', 
    'tz_std_bias': '0', 
    'tz_mode': '1', 
    'tz_dst_date': '0000-03-05:00T01:00:00', 
    'tz_std_date': '0000-10-05:00T02:00:00', 
    'assetid': '293336', # Device Asset ID (NOT SERIAL NUMBER, NOT THE SAME AS WORKSTATIONID)
    'wins_name': 'DESKTOP-123', # Windows Device name (same as computer name above)
    'role': '1', # Unsure
    'chassis_type': '3', # Device chassis type. 3 = Desktop/any Mac. 10 = Laptop.
    'device_serial': 'SN2134', # Device serial number
    'processor_count': '1', # Physical Processor count (like the actual hardware, not cores)
    'total_memory': '8589934592', # Total RAM (bytes) 
    'service_pack': '0', # OS service pack (always shows 0 on Windows 10/11)
    'os_serial_number': '54321-12345-98765-GHKLS', # OS serial number (often not accurate in my experience)
    'os_product_key': '12345-56789-ABCDE', # OS Product key (often not accurate in my experience)
    'os_type': '18', # 
    'last_scan_time': '2024-12-25 10:41:00' # Last time device was checked (ISO format). May also return "0000-00-00 00:00:00" if last scan time cannot be gotten.
    '[ASSET CUSTOM FIELDS 1-6 IF AVAILABLE]': '[ASSET CUSTOM FIELD INFORMATION]' # Note, these will be scattered in the keys above, not at the bottom.
    }]

Get Client Devices
--------------

.. automethod:: NAble.clientDevices

Example Device Item::

    

Device Details
--------------

.. automethod:: NAble.deviceDetails

Experimental checks:

- EDR Present.  Will try to determine EDR status using Asset software check.



