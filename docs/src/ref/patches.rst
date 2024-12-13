
.. currentmodule:: NAbleAPI
.. toctree::
    :maxdepth: 2
    :hidden:
    :caption: Patch Management (Windows only)


Patch Management
==================
These functions allow you to interact with your clients and sites.

Official documentation can be found `here <https://documentation.n-able.com/remote-management/userguide/Content/patch_management.htm>`_.

.. autosummary::
   :nosignatures:

    NAble.listPatches
    NAble.approvePatches
    NAble.doNothingPatches
    NAble.ignorePatches
    NAble.reprocessPatches
    NAble.retryPatches

List Patches
-------

.. automethod:: NAble.listPatches

Approve Patches
-------

.. automethod:: NAble.approvePatches


Do Nothing with Patches
-------

.. automethod:: NAble.doNothingPatches


Ignore Patches
-------

.. automethod:: NAble.ignorePatches


Reprocess Patches
-------

.. automethod:: NAble.reprocessPatches


Retry Patches (appears to be the same as Reprocess)
-------

.. automethod:: NAble.retryPatches

