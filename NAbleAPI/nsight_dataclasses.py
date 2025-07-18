# BUILT-IN
from typing import Optional, Literal, TypeVar
import datetime as dt
from ipaddress import IPv4Address

# EXTERNAL
from pydantic import BaseModel, Field, PositiveInt, PositiveFloat, field_validator, TypeAdapter, AliasChoices, ConfigDict

Endpoints = Literal['list_clients', 'list_sites', 'list_device_monitoring_details']



# Clients
class Client(BaseModel):
    name: str
    clientid: int
    view_dashboard: bool
    view_wkstsn_assets: bool
    dashboard_username: Optional['str'] = None
    creation_date: dt.date
    server_count: int
    workstation_count: int
    mobile_device_count: int
    device_count: int

Clients = TypeAdapter(list[Client])

# Sites
class Site(BaseModel):
    name: str
    siteid: int
    connection_ok: bool
    creation_date: Optional[dt.date] = None
    primary_router: Optional[str] = None
    secondary_router: Optional[str] = None
    
Sites = TypeAdapter(list[Site])

# Workstations
class Workstation(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str
    deviceid: int = Field(validation_alias=AliasChoices('workstationid')) # I like device ID better
    guid: str
    description: str
    install_date: dt.date
    last_boot_time: int # TODO is this a unix timestamp
    dsc_active: bool
    atz_dst_date: str # TODO this is when daylight savings is set, and does not include a year.  Maybe I can add a year?
    utc_apt: dt.datetime #TODO set timezone!
    utc_offset: int # UTC offset in seconds
    user: str
    domain: Optional[str] = None
    manufacturer: str
    model: str
    ip: IPv4Address
    external_ip: IPv4Address
    mac1: Optional[str] = None
    mac2: Optional[str] = None
    mac3: Optional[str] = None
    os: str
    os_details: str
    agent_version: str 
    agent_mode: int #TODO figure out what these are
    online: bool
    active_247: bool
    check_interval_247: int # Assuming minutes
    status_247: int #TODO figure out what these are
    local_date_247: dt.date
    local_time_247: dt.time
    utc_time_247: dt.datetime # TODO set timezone to UTC
    dsc_hour: int
    dsc_status: int # Assuming whether or not it is currently daylight savings
    dsc_local_date: dt.date
    dsc_local_time: dt.time
    dsc_utc_time: dt.datetime # Set to UTC
    tz_bias: int
    tz_dst_bias: int
    tz_std_bias: int
    tz_mode: int
    tz_dst_date: str
    tz_std_date: str
    assetid: int
    wins_name: str
    role: int
    chassis_type: int
    device_serial: str
    processor_count: int
    total_memory: int # Bytes
    service_pack: Optional[int] = None
    os_serial_number: Optional[str] = None
    os_product_key: Optional[str] = None
    os_type:Optional[int] = None
    last_scan_time: dt.datetime
    
    @field_validator('agent_version') # Convert version from 9_10_11 to 9.10.11
    def agent_ver(cls, value):
        return value.replace('_', '.')
    
Workstations = TypeAdapter(list[Workstation])

# Device Details
class ClientDeviceWorkstation(BaseModel):
    deviceid: int = Field(validation_alias=AliasChoices('id'))
    name: str
    user: str = Field(validation_alias=AliasChoices('username')) #TODO should this be user or username? Make it the same for Workstation and this
    description: str
    status: str
    checkcount: list[dict[str, int]] # TODO make this show correctly
    takecontrol: bool
    patch: bool
    mav: bool
    mob: bool
    systray: bool
    mavbreck: bool
    webprotection: bool
    riskintelligence: bool
    guid: Optional[str] = None
    os: Optional[str] = None
    agent_version: Optional[str] = Field(default=None, validation_alias=AliasChoices('agent')) #TODO this is returned as "Agent v10.13.8", I think it should be made to match workstation
    lastresponse: Optional[dt.datetime] = None
    lastresponse_utc: Optional[dt.datetime] = None
    lastboot: Optional[dt.datetime] = None
    checks: Optional[dict] = None # TODO make this show correctly
    outages: Optional[dict] = None # TODO make this show correctly
    notes: Optional[dict] = None # TODO make this show correctly
    
    @field_validator('checks')
    def check_converter(cls, value):
        if value:
            if int(value['@count']) == 0:
                return {
                    'count':0,
                    'checks': tuple()
                }
                
            else:
                return {
                    'count': int(value['@count']),
                    'checks': tuple(DeviceDetailChecks.validate_python(value['check']))
                }
        else:
            return None
    
    @field_validator('lastresponse', 'lastresponse_utc', 'lastboot', mode='before')
    def datetime_fix(cls, value):
        if value: # Sometimes its none, idk?
            try:
                return dt.datetime.strptime(value, "%Y-%m-%d %H:%m:%s").date()
            except ValueError: # Invalid year
                return None
        else:
            return None


class ClientDeviceSite(BaseModel):
    siteid: int = Field(validation_alias=AliasChoices('id'))
    name: str
    devices: list[ClientDeviceWorkstation] = Field(validation_alias=AliasChoices('workstation', 'server'))
    
    @field_validator('devices', mode='before')
    def workstation_fix(cls, value): #Workstations are sometimes returned in dict format
        if isinstance(value, dict):
            return [value]
        
        else:
            return value
    
class ClientDevice(BaseModel):
    clientid: int = Field(validation_alias=AliasChoices('id'))
    name: str
    sites: list[ClientDeviceSite] = Field(validation_alias=AliasChoices('site'))
    
    @field_validator('sites', mode='before')
    def site_fix(cls, value): # Sites are sometimes returned in dict format
        if isinstance(value, dict):
            return [value]
        else:
            return value
    
    

ClientDevices = TypeAdapter(list[ClientDevice])

# Device Details
class DeviceDetailCheck(BaseModel):
    checkid: int
    item_type: str = Field(validation_alias=AliasChoices('dsc_247'))
    description: str
    status: str = Field(validation_alias=AliasChoices('checkstatus'))
    extra: Optional[str] = None
    datetime: Optional[dt.datetime] = Field(validation_alias=AliasChoices('datetime'))
    consecutive_fails: int
    emailalerts: bool
    emailrecoveryalerts: bool
    smsalerts: bool
    smsrecoveryalerts: bool
    servertime: dt.datetime
    
    @field_validator('datetime', mode='before')
    def datetime_fix(cls, value):
        if value: # Sometimes its none, idk?
            try:
                return dt.datetime.strptime(value, "%Y-%m-%d %H:%m:%s").date()
            except ValueError: # Invalid year
                return None
        else:
            return None
    
    @field_validator('item_type', mode='before')
    def convert_item(cls, value):
        types = {
            1: '247',
            2: 'dsc',
            3: 'scheduled_task',
            4: 'mav_check',
            6: 'mob_check'
        }
        return types[int(value)] # change status to something usable
    
DeviceDetailChecks = TypeAdapter(list[DeviceDetailCheck])

    
class DeviceDetail(BaseModel):
    deviceid: int = Field(validation_alias=AliasChoices('id'))
    name: str
    description: str
    user: str = Field(validation_alias=AliasChoices('username')) #TODO should this be user or username? Make it the same for Workstation and this
    guid: Optional[str] = None
    os: str
    agent_version: str = Field(validation_alias=AliasChoices('agent')) #TODO this is returned as "Agent v10.13.8", I think it should be made to match workstation
    lastresponse: Optional[dt.datetime] = None
    lastresponse_utc: dt.datetime
    lastboot: dt.datetime
    checks: Optional[dict] = None # TODO make this show correctly
    outages: Optional[dict] = None # TODO make this show correctly
    notes: Optional[dict] = None # TODO make this show correctly
    takecontrol: bool
    patch: bool
    mav: bool
    mob: bool
    systray: bool
    mavbreck: bool

    
    @field_validator('agent_version') # Convert version from 9_10_11 to 9.10.11
    def agent_ver(cls, value):
        return value.replace('Agent v', '')
    
    @field_validator('checks')
    def check_converter(cls, value):
        if value:
            if int(value['@count']) == 0:
                return {
                    'count':0,
                    'checks': tuple()
                }
                
            else:
                if isinstance(value['check'], dict):
                    value['check'] = [value['check']] # Evil people
                return {
                    'count': int(value['@count']),
                    'checks': tuple(DeviceDetailChecks.validate_python(value['check']))
                }
        else:
            return None
    
DeviceDetails = TypeAdapter(list[DeviceDetail])



# Check


class Check(BaseModel):
    checkid: int
    uid: int
    sync_status: str
    description: str
    status: str = Field(validation_alias=AliasChoices('statusid'))
    date: Optional[dt.date] = None # Im pretty sure this is the last time the check ran
    time: Optional[dt.time] = None
    utc_run: Optional[dt.datetime] = None
    output: Optional[str] = None
    emailalerts: bool = Field(validation_alias=AliasChoices('email'))
    emailrecoveryalerts: bool = Field(validation_alias=AliasChoices('emailrecovery'))
    smsalerts: bool = Field(validation_alias=AliasChoices('sms'))
    smsrecoveryalerts: bool = Field(validation_alias=AliasChoices('smsrecovery'))
    check_type: int # TODO convert to actual info
    item_type: str = Field(validation_alias=AliasChoices('dsc_247'))
    consecutive_fails: int
    
    @field_validator('date', mode='before')
    def date_fix(cls, value):
        try:
            return dt.datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError: # Invalid year
            return None
        
    @field_validator('time', mode='before')
    def time_fix(cls, value):
        try:
            return dt.datetime.strptime(value, "%H:%m:%s").time()
        except ValueError: # Invalid year
            return None
        
    @field_validator('utc_run', mode='before')
    def datetime_fix(cls, value):
        if value: # Sometimes its none, idk?
            try:
                return dt.datetime.strptime(value, "%Y-%m-%d %H:%m:%s").date()
            except ValueError: # Invalid year
                return None
        else:
            return None
    
    @field_validator('sync_status', mode='before')
    def convert_sync(cls, value):
        sync = { # 71 = awaiting sync I think
            0: 'synced'
        }
        try: 
            return sync[int(value)]
        except KeyError: #TODO add the rest
            pass
        return value
    
    @field_validator('status', mode='before')
    def convert_status(cls, value):
        statuses = {
            0: 'not_run',
            1: 'failed',
            4: 'failed_parked',
            5: 'passed'
        }
        return statuses[int(value)] # change status to something usable
    
    @field_validator('item_type', mode='before')
    def convert_item(cls, value):
        types = {
            1: '247',
            2: 'dsc',
            3: 'scheduled_task',
            4: 'mav_check',
            6: 'mob_check'
        }
        return types[int(value)] # change status to something usable
    
Checks = TypeAdapter(list[Check])
