# BUILT-IN
from typing import Optional, Literal, TypeVar
from datetime import datetime, date, time
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
    creation_date: date
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
    creation_date: Optional[date] = None
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
    install_date: date
    last_boot_time: int # TODO is this a unix timestamp
    dsc_active: bool
    atz_dst_date: str # TODO this is when daylight savings is set, and does not include a year.  Maybe I can add a year?
    utc_apt: datetime #TODO set timezone!
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
    local_date_247: date
    local_time_247: time
    utc_time_247: datetime # TODO set timezone to UTC
    dsc_hour: int
    dsc_status: int # Assuming whether or not it is currently daylight savings
    dsc_local_date: date
    dsc_local_time: time
    dsc_utc_time: datetime # Set to UTC
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
    last_scan_time: datetime
    
    @field_validator('agent_version') # Convert version from 9_10_11 to 9.10.11
    def agent_ver(cls, value):
        return value.replace('_', '.')
    
Workstations = TypeAdapter(list[Workstation])

# Device Details
class DeviceDetail(BaseModel):
    deviceid: int = Field(validation_alias=AliasChoices('id'))
    name: str
    description: str
    user: str #TODO should this be user or username? Make it the same for Workstation and this
    guid: str
    os: str
    agent_version: str #TODO this is returned as "Agent v10.13.8", I think it should be made to match workstation
    lastresponse: datetime
    lastresponse_utc: datetime
    lastboot: datetime
    checks: dict[str, int] # TODO make this show correctly
    outages: dict
    notes: dict
    patch: bool
    mav: bool
    mob: bool
    systray: bool
    mavbreak: bool
    
DeviceDetails = TypeAdapter(list[DeviceDetail])