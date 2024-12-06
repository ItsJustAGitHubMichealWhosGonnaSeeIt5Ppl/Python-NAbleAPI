
.. currentmodule:: NAbleAPI
.. toctree::
    :maxdepth: 2
    :hidden:
    :caption: Clients, Sites, and Devices

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
     'view_dashboard': '0', # Whether client can view dashboard?
     'view_wkstsn_assets': '0', # Whether client can view workstation assets?
     'dashboard_username': 'none', # Username to access dashboard (if applicable)
     'timezone': None, # Timezone (None if not set)
     'creation_date': '2022-01-09', # Date created
     'server_count': '0', # server devices count
     'workstation_count': '1', # workstation devices count
     'mobile_device_count': '0', # mobile devices count
     'device_count': '1' # Total devices
     }

Add Client
----------
NOT YET IMPLEMENTED

.. automethod:: NAble.addClient


List Sites
-----

.. automethod:: NAble.sites

Add Site
----------
NOT YET IMPLEMENTED

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

Get Client Devices
--------------

.. automethod:: NAble.clientDevices

Device Details
--------------

.. automethod:: NAble.deviceDetails

