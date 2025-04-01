.. _index:
.. Python-NAbleAPI documentation master file, created by
   sphinx-quickstart on Fri Dec  6 13:38:16 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Python-NAbleAPI documentation
=============================

**Python-NAbleAPI** is a Python library/wrapper for the `N-Able Data Extraction API <https://documentation.n-able.com/remote-management/userguide/Content/data_extraction_api.htm>`_.
I have never written in "ReStructuredText" before, so I spent a lot of time reading the documentation and looking at the `Spotipy index.rst <https://github.com/spotipy-dev/spotipy/blob/master/docs/index.rst?plain=1>`_ to try and understand better. Thank you spotipy devs!

Features
========

*Python-NAbleAPI* currently supports most of the official `N-Able Data Extraction API <https://documentation.n-able.com/remote-management/userguide/Content/data_extraction_api.htm>`_ with the eventual goal being to support them all!

Installing and updating
=======================

Install Python-NAbleAPI with::

    pip install NAbleAPI

OR::

    python -m pip install NAbleAPI

Update using::

    pip install NAbleAPI --upgrade

OR::

    python -m pip install NAbleAPI --upgrade

Getting Started
===============

You will need to authorize/login using an API key to use this module.  You will also need to know which region your N-Able instance is on.

To get your API key, follow the `official N-Able documentation <https://documentation.n-able.com/remote-management/userguide/Content/api_key.htm>`_.

To find your region, check `this page <https://documentation.n-able.com/remote-management/userguide/Content/determine_url.htm>`_ or use the table below

================================ =========================== ============
Dashboard URL                    Region                      Status
================================ =========================== ============
www.am.remote.management         americas, ams               Untested
wwwasia.system-monitor.com       asia                        Untested
www.system-monitor.com           australia, au, aus          Untested
wwweurope1.systemmonitor.eu.com  europe, eu                  Untested
wwwfrance.systemmonitor.eu.com   france, fr                  Untested
wwwfrance1.systemmonitor.eu.com  france1, fr1                Untested
wwwgermany1.systemmonitor.eu.com germany, de, deu            Untested
wwwireland.systemmonitor.eu.com  ireland, ie, irl            Untested
wwwpoland1.systemmonitor.eu.com  poland, pl,pol              Untested
www.systemmonitor.co.uk          united kingdom, uk, gb, gbr **Verified**
www.systemmonitor.us             united states, us, usa      Untested
================================ =========================== ============

Notes

* Not all regions have been tested. If your region is marked 'untested' on the table, please let me know whether it works.
* If your dashboard URL starts with `www2`, assume it is just `www` for the region.
* If there is another abbreviation or country code you would like added, let me know!

Authorizing and making a request
--------------------------------

Once you have your key and region, you can authorize and make your first request::
    from NAbleAPI import NAble #Import the NAble module

    na = NAble(region=[your region],key=[Your key]) # Authorize
    myClients = na.clients() # Get all your clients


Storing your API key
--------------------

It's probably best not to store your API key in your script. Instead, you can create a .env file and use that.

1. Create a new file called `.env` in your root directory
2. Put your API key in it (do not put it in quotes, type exactly as shown below)::

    NABLE_KEY = f821213a8d3q43843dj39824

3. Get the key from file::

    from NAbleAPI import NAble # Import the NAble package
    import os # Import OS package (built into Python, I'm like 99% sure)

    NABLE_KEY = os.getenv("NABLE_KEY")

.. toctree::
    :maxdepth: 1
    :caption: General Usage
    index.rst
    

.. toctree::
   :maxdepth: 2
   :caption: Reference

   ref/clientSiteDevices.rst
   ref/patches.rst
   ref/reference

