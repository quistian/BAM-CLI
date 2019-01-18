#!/usr/local/bin/python3 -tt

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


'''

RESTful Python API for BAM

REST WADL: https://proteus.utoronto.ca/Services/REST/application.wadl

From JumpStart to BAM
User Group Webinar - Making APIs Work for You - Episode 1

- Web Layer and API Layer

- Connect -> Login -> API Calls -> Logout

- SOAP one session, and then at end closes

- REST single shot sessions as request and responses

- URLs contain action verbs: Service, Create, Read, Update, Delete

- API account is the same as a normal user account (hybrid as well)

- Logs -> /var/log/Server.log

- API calls are small unit operations
  each with custom input and output

- To send NULL values use e.g. var = ""

- BAM v8.1.0 and present support REST

- Sequence of steps for the REST API to e.g. add a host record to bozo.utoronto.ca

    a. Get the REST onetime Token, add it to the https Header
    b. Get the Parent Configuration object by name
    c. Get the Parent View object by name
    d. Get the Parent Zone object by name, using the fqdn (i.e. utoronto.ca)


'''

import sys
import json
import requests

from pprint import pprint

uname = 'api-test-user'
pw = 't1e2s3t4'
creds_ro = {'username': uname, 'password': pw}

uname = 'api-test-user2'
pw = 't5e6s7t8'
creds_rw = {'username': uname, 'password': pw}

'''

Global Variables:
    * start with UpperCase
    * have no _ character
    * may have mid UpperCase words

'''

Debug = False
Debug = True

Creds = creds_rw

BaseURL = "https://proteus.utoronto.ca/Services/REST/v1/"
RootId = 0
ConfigId = 0
ViewId = 0

ConfigName = 'Test'
ViewName = 'Public'

AuthHeader = {}

ObjectTypes = [
        'Entity',
        'Configuration',
        'View',
        'Zone',
        'InternalRootZone',
        'HostRecord',
        'AliasRecord',
        'MXRecord',
        'TXTRecord',
        'SRVRecord',
        'GenericRecord',
        'HINFORecord',
        'NAPTRRecord',
        'StartOfAuthority'
]

IPv4Objects = [
        'IP4Block',
        'IP4Network',
        'IP4Adress',
        'IP4DHCPRange',
        'IP4NetworkTemplate',
]

Categories = {
    'all': 'ALL',
    'admin': 'ADMIN',
    'Configuration': 'CONFIGURATION',
    'deploymentOptions': 'DEPLOYMENT_OPTIONS',
    'deploymentRoles': 'DEPLOYMENT_ROLES',
    'deploymentSchedulers': 'DEPLOYMENT_SCHEDULERS',
    'dhcpClassObjects': 'DHCPCLASSES_OBJECTS',
    'dhcpNACPolicies': 'DHCPNACPOLICY_OBJECTS',
    'IP4Objects': 'IP4_OBJECTS',
    'IP6Objects': 'IP6_OBJECTS',
    'MACPoolObjects': 'MACPOOL_OBJECTS',
    'resourceRecords': 'RESOURCE_RECORD',
    'servers': 'SERVERS',
    'tags': 'TAGS',
    'tasks': 'TASKS',
    'TFTPObjects': 'TFTP_OBJECTS',
    'vendorProfiles ': 'VENDOR_PROFILES',
    'viewZones ': 'VIEWS_ZONES',
    'TSIGKeys ': 'TSIG_KEYS',
    'GSS': 'GSS',
    'DHCPZones': 'DHCP_ZONES',
    'ServerGroup': 'SERVERGROUP',
}

TopLevelDomains = ['ca', 'edu', 'org', 'net', 'com', 'int' ]

'''

Generic API Methods

* use the UPDATE, DELETE and GET methods
* are used in many Address Manager API scripts


Getting Objects:

Generic methods for getting entity values.
*  Get entities by name
*  Get entities by ID
*  Get Entities
*  Get Parent

See the BAM API Guide, Chapter 4

'''


'''
Get Entity by Name

Returns objects from the database referenced by their name field.

Output / Response: Returns the requested object from the database.

APIEntity getEntityByName( long parentId, String name, String type )

Parameter Description
 parentId The ID of the target object’s parent object.
 name The name of the target object.
 type The type of object returned by the method.
 This string must be one of the constants listed in ObjectTypes

'''


def get_entity_by_name(id, name, type):
    URL = BaseURL + 'getEntityByName'
    param_list = {'parentId': id, 'name': name, 'type': type}
    req = requests.get(URL, headers=AuthHeader, params=param_list)
    return req.json()
    

'''

Get Entity by ID
Returns objects from the database referenced by their database ID
and with its properties fields populated.

Output / Response
Returns the requested object from the database with its properties fields populated.
For more information about the available options, refer to IPv4Objects
on page 248 in the Property Options Reference section.

Returns E.g.

{
    'id': 2217650,
    'name': 'utoronto',
    'properties': 'deployable=true|absoluteName=utoronto.ca|',
    'type': 'Zone'
}

'''


def get_entity_by_id(id):
    URL = BaseURL + 'getEntityById'
    params = {'id': str(id)}
    req = requests.get(URL, headers=AuthHeader, params=params)
    return req.json()


'''

Get Entities

Returns an array of requested child objects for a given parentId value.
Some objects returned in the array may not have their properties field set.
`For those objects, you will need to call them individually using
the getEntityById() method to populate the properties field.

* Using getEntities() to search users will return all users existing in Address Manager.
  Use getLinkedEntities() or linkEntities() to search users under a specific user group.

* Using getEntities() to query server objects in configurations containing XHA pairs might
result in a connection timeout if any of the servers in an XHA pair are not reachable.

Output / Response
Returns an array of the requested objects from the database without their
properties fields populated, or returns an empty array.

API call:
    getEntities( long parentId, String type, int start, int count )

Parameter Description:
    parentId: The object ID of the target object’s parent object.
    type: The type of object returned.
          This must be one of the constants listed in Object Types
    start:  Indicates where in the list of objects to start returning objects.
            The list begins at an index of 0.
    count:  Indicates the maximum number of child objects to return.

Returns a list of branch items given the root one level up

'''

def get_entities(id, type, start, count):
    URL = BaseURL + 'getEntities'
    params = {'parentId': id, 'type': type, 'start': start, 'count': count}
    req = requests.get(URL, headers=AuthHeader, params=params)
    return req.json()


'''

Get Parent

Returns the parent entity of a given entity.

Output / Response
Returns the APIEntity for the parent entity with its properties fields populated. For more information about
the available options, refer to IPv4Objects on page 248 in the Property Options Reference section.

API call:
    APIEntity getParent ( long entityId )

Parameter Description:
    entityId:   The Entity Id


'''


def get_parent(child_id):
    URL = BaseURL + 'getParent'
    params = {'entityId': str(child_id)}
    req = requests.get(URL, headers=AuthHeader, params=params)
    return req.json()


'''

Generic methods for searching and retrieving entities.

    * Custom Search
    * Search by Category
    * Search by Object Types
    * Get Entities by Name
    * Get Entities by Name Using Options
    * Get MAC Address

Supported wildcards in the search string:
You can use the following wildcards when invoking a search method. These wildcards are supported only
in the String parameter:

    * ^ matches the beginning of a string. For example, ^ex matches example but not text.
    * $ matches the end of string. For example: ple$ matches example but not please.
    * * matches zero or more characters within a string. For example: ex*t matches exit and excellent.

Note: You cannot use the following characters in the search string:

    * , (comma)
    * ‘ (single quotation mark)
    * ( ) (parentheses)
    * [ ] (square brackets)
    * { } (braces)
    * % (percent)
    * ? (question mark)
    * + (addition/plus sign)

'''

'''

Custom Search
    Search for an array of entities by specifying object properties.

Output / Response
    Returns an array of APIEntities matching the specified object properties or returns an empty array.
    The APIEntity will at least contain Object Type, Object ID, Object Name, and Object Properties.

API call:
    APIEntity[]
    customSearch ( String[] filters, String type, String[] options, int start, int count)

    filters: List of properties on which the search is based.  Valid format is: name=value, name2=value2
             E.g. filters=filter1=abc&filters=filter2=def

    type: The object type that you wish to search. The type cannot be null or empty string ""
          This must be one for the following object types:

            * IP4Block
            * IP4Network
            * IP4Addr
            * GenericRecord
            * HostRecord
            * Any other objects with user-defined fields

    options: A list of strings of search options specifying the search behavior.
             Reserved for future use.
             E.g. options=option1=val1&options=option2=val2

    start: Indicates where in the list of returned objects to start returning objects.
           The value must be a non-negative value and cannot be null or empty

    count: The maximum number of objects to return.
           The value must be a positive value between 1 and 1000.
           This value cannot be null or empty.

    Supported fields/filters for each type:

        Type: GenericRecord
        Fields:
            * comments=Text
            * ttl=Long
            * recordType=Text
            * rdata=Text

        Type: HostsRecord
        Fields:
            * comments=Text
            * ttl=Long
        
        Type: IP4Block
        Fields:
            * inheritDNSRestrictions=Boolean
            * pingBeforeAssign=Boolean
            * reverseZoneSigned=Boolean
            * allowDupHost=Boolean
            * inheritDefaultDomains=Boolean
            * highwatermark=Integer
            * lowwatermark=Integer

        Type: IP4Network
        Fields:
            * inheritDNSRestrictions=Boolean
            * pingBeforeAssign=Boolean
            * reverseZoneSigned=Boolean
            * allowDupHost=Boolean
            * inheritDefaultDomains=Boolean
            * portInfo=Text
            * highwatermark=Integer
            * lowwatermark=Integer

        Type: IP4Addr
        Fields:
            * routerPortInfo=Text
            * portInfo=Text
            * vlanInfo=Text

API Example:
    http://<AddressManager_ip>/Services/REST/customSearch?
    filters=filter1=abc&filters=filter2=def&type=IP4Block&options=&start=0&count=10

The filters and options should be sent using the follows Requests data structure:

    'filters': ['comments=This is important', 'recordType=MX', 'ttl=86400', 'rdata=128.100.103.*']

The return is a list as follows

[
    {'id': 2429335, 'name': '',
      'properties': 'ttl=86400|absoluteName=theta.utoronto.ca|linkedRecordName=alt2.aspmx.l.google.com|priority=5|',
      'type': 'MXRecord'},
    {'id': 2429340, 'name': '',
      'properties': 'ttl=86400|absoluteName=lcd.utoronto.ca|linkedRecordName=aspmx3.googlemail.com|priority=10|',
      'type': 'MXRecord'},
    {'id': 2429341, 'name': '',
      'properties': 'ttl=86400|absoluteName=lcd.utoronto.ca|linkedRecordName=aspmx2.googlemail.com|priority=10|',
      'type': 'MXRecord'}
]


'''

def custom_search(fltrs, typ, strt, cnt):
    URL = BaseURL + 'customSearch'
    opts = ''
    param_list = {
            'filters': fltrs,
            'type': typ,
            'options': opts,
            'start': strt,
            'count': cnt,
    }
    req = requests.get(URL, headers=AuthHeader, params=param_list)
    return req.json()


'''

Search by Category:

    Returns an array of entities by searching for keywords associated with objects
    of a specified object category.

Output / Response:
    Returns an array of entities matching the keyword text and the category type,
    or returns an empty array.

API call:
    APIEntity[] searchByCategory ( String keyword, String category, int start, int count )

Parameter Description:
    keyword: The search keyword string. This value cannot be null or empty.
    
    category: The entity category to be searched. This must be one of the entity categories
              listed in Categories dictionary
              
    start: Indicates where in the list of returned objects to start returning objects.
           The list begins at an index of 0. This value cannot be null or empty.
           
    count: The maximum number of objects to return. The default value is 10.
           This value cannot be null or empty.


'''

def search_by_category(key, cat, strt, stp):
    URL = BaseURL + 'searchByCategory'

    param_list = {
        'keyword': key,
        'category': cat,
        'start': strt,
        'count': stp
    }

    req = requests.get(URL, headers=AuthHeader, params=param_list)
    return req.json()


'''

Search by Object Types

Returns an array of entities by searching for keywords associated with objects of a specified object type.
You can search for multiple object types with a single method call.

Output / Response
Returns an array of entities matching the keyword text and the category type, or returns an empty array.

Arguments in the parameter list:

keyword: The search string. Can not be NULL or Empty
        ^ matches the beginning of a string
        $ matches the end of a string
        * matches one or more characters within a string

types: The object types for which to search in the format type1,type2,[type3 ...]
       See ObjectTypes list E.g.
        'Entity','Configuration','View','Zone','HostRecord','MXRecord',

start: List index (starting with 0) to mark the beginning of the return

count: Maximum values to return. Default is 10


'''


def search_by_object_types(key, typs, strt, cnt):
    URL = BaseURL + 'searchByObjectTypes'
    param_list = {
        'keyword': key,
        'types': typs,
        'start': strt,
        'count': cnt
    }
    req = requests.get(URL, headers=AuthHeader, params=param_list)
    return req.json()


'''
Get Entities by Name

Returns an array of entities that match the specified parent, name, and object type.

Output / Response:  Returns an array of entities.
                    The array is empty if there are no matching entities.
API call:

APIEntity getEntitiesByName (long parentId, String name, String type, int start, int count )

Parameter Description
    parentId: The object ID of the parent object of the entities to be returned.
    name: The name of the entity.
    types:  The type of object to be returned. This value must be one of the object types
            listed in Object Types on page 209.
    start:  Indicates where in the list of returned objects to start returning objects.
            The list begins at an index of 0. This value cannot be null or empty.
    count: The maximum number of objects to return. The default value is 10.
           This value cannot be null or empty.

'''


def get_entities_by_name(id, name, type, start, count):
    URL = BaseURL + 'getEntitiesByName'
    param_list = {
        'parentId': id,
        'name': name,
        'type': type,
        'start': start,
        'count': count,
    }
    req = requests.get(URL, headers=AuthHeader, params=param_list)
    return req.json()


'''

Get Parent
Returns the parent entity of a given entity (referenced by Id).

Output / Response
Returns the APIEntity for the parent entity with its properties fields populated.
For more information about the available options, refer to IPv4Objects
on page 248 in the Property Options Reference section.

E.g. parent object:

{
    'id': 2217650,
    'name': 'utoronto',
    'type': 'Zone',
    'properties': 'deployable=true|absoluteName=utoronto.ca|'
}


'''

def bam_error(err_str):
    print(err_str)
    sys.exit()


def get_token():
    URL = BaseURL + 'login'
    req = requests.get(URL, params=Creds)
    result = req.json().split()
    return result[3]


def bam_init():
    global AuthHeader

    tok = get_token()

    AuthHeader = {
      'Authorization': 'BAMAuthToken: ' + tok,
      'Content-Type': 'application/json'
    }

    set_config_id()
    set_view_id()

    if Debug:
        print()
        print('Authorization Header:', AuthHeader)
        print('ConfigId for Configuration:', ConfigName, 'is:',  ConfigId)
        print('ViewId for View:', ViewName, 'is:', ViewId)
        print()

def bam_logout():
    URL = BaseURL + 'logout'
    req = requests.get(URL, headers=AuthHeader)
    return req.json()


def bam_error(err_str):
    print(err_str)
    sys.exit()


def get_system_info():
    URL = BaseURL + 'getSystemInfo'
    req = requests.get(URL, headers=AuthHeader)
    return req.json()


def get_configuration_setting(id, name):
    URL = BaseURL + 'getConfigurationSetting'
    params = {'configurationId': id, 'settingName': name}
    req = requests.get(URL, headers=AuthHeader, params=params)
    return req.json()









def get_ip4_address(ip, tok):
    URL = BaseURL + 'getIP4Address'


'''

addEntity Description


addEntity() is a generic method for adding:
    Configurations,
    DNS zones, and
    DNS resource records.

When using addEntity() to add a zone, you must specify
a single zone name without any . (dot) characters.
The parent object must be either a DNS view or another DNS zone.

Output / Response
Returns the object ID for the new DNS zone.

API call: long addEntity( long parentId, APIEntity entity )

Parameter Description
parentId: The object ID of the parent DNS view or
          DNS zone to which the zone is added.
          
entity:   The zone name, without any . (dot) characters, to be added.

The entity has the following JSON structure:

 {'id': 2516291, 'name': 'org', 'type': 'Zone', 'properties': None}
 
 or when filled in:
 
 
'''

def add_entity(parent_id, entity):
    URL = BaseURL + 'addEntity'
    params = {'parentId': parent_id}

    req = requests.post(URL, headers=AuthHeader, params=params, json=entity)
    return req.json()
    
'''

Add Zone: Adds DNS zones.

When using addZone(), you can use . (dot) characters to create the top level domain
and subzones.

Output / Response

Returns the object ID for the new DNS zone.

API Call:
long addZone( long parentId, String absoluteName, String properties )


Parameter Description:


parentId: The object ID for the parent object to which the zone is being added.
          For top-level domains, the parent object is a DNS view.
          For sub zones, the parent object is a top-level domain or DNS zone.
          
absoluteName: The complete FQDN for the zone with no trailing dot
              (for example, frodo.org).
              
properties: Adds object properties, including a flag for deployment,
            an optional network template association, and
            user-defined fields in the format:
                deployable=<true|false>|template=<template id>|
                <userField>=<userFieldValue>
                
The deployable flag is false by default and is optional. To make the zone
deployable, set the deployable flag to true.

'''


def add_zone(fqdn):
    URL = BaseURL + 'addZone'

#    if is_zone(fqdn):
#        print fqdn, 'is already a zone and can not be added'
#        return -1

    if fqdn in TopLevelDomains:
        parent_id = ViewId
    else:
        parent_id = get_object_id(parent_name(fqdn))
        info = get_entity_by_id(parent_id)
        if info['type'] != 'Zone':
            bam_error('The parent of', fqdn, 'is not a zone')
    
    param_list = {
            'parentId': parent_id,
            'absoluteName': fqdn,
            'properties': 'deployable=true',
    }

    req = requests.post(URL, headers=AuthHeader, params=param_list)
    return req.json()
    

'''

Add Zone Template
    Adds a DNS zone template.

Output / Response:
    Returns the object ID of the new DNS zone template.

API Call:
long addZoneTemplate( long parentId, String name, String properties )

Parameter Description:
    parentId: The object ID of the parent DNS view when adding a view-level zone
              template. The object ID of the configuration when adding
              a configurationlevel zone template.
    name: The name of the DNS zone template. This value can be an empty string ("").
    
    properties: Adds object properties, including user-defined fields.


'''


def add_zone_template(parent_id, name, properties):
    URL = BaseURL + 'addZoneTemplate'
    
    param_list = {
        'parentId': parent_id,
        'name': name,
        'properties': properties,
    }
    
    req = requests.post(URL, headers=AuthHeader, params=param_list)
    return req.json()


'''

Adding Resource Records  Description

viewId: Object ID for the parent view

absoluteName: Fully Qualified Domain Name

type: One of
    AliasRecord
    HINFORecord
    HOSTRecord (see add_host_record)
    MXRecord
    TXTRecord

rdata: Data for the RR in the BIND format

'''

def add_resource_record(fqdn, typ, rrdata, ttl, props):
    URL = BaseURL + 'addResourceRecord'
    param_list = {
        'viewId': ViewId,
        'absoluteName': fqdn,
        'type': typ,
        'rdata': rrdata,
        'ttl': str(ttl),
        'properties': props
    }
    req = requests.post(URL, headers=AuthHeader, params=param_list)
    return req.json()

#
# Add a host record, either and A or an A and a PTR
#

def add_host_record(fqdn, ips, ttl, properties):
    URL = BaseURL + 'addHostRecord'

# adding to the top level of the zone requires a leading dot
    if is_zone(fqdn):
        fqdn = '.' + fqdn

    param_list = {
      'viewId': ViewId,
      'absoluteName': fqdn,
      'addresses': ips,
      'ttl': ttl,
      'properties': properties
    }

    if Debug:
        pprint(param_list)

    req = requests.post(URL, headers=AuthHeader, params=param_list)
    if Debug:
        print(req.url)
        print(req.text)
    return req.json()

'''

Deleting Objects

Generic methods for deleting an object.
There are two generic methods for getting entity values:
• Delete
• Delete with Options


Delete:
    Deletes an object using the generic delete() method.
    
Output / Response:
    None.
    
API call:
    Pass the entity ID from the database identifying the object to be deleted.
    void delete ( long ObjectId )

Parameter Description:
    ObjectId The ID for the object to be deleted.

'''

def delete_object(obj_id):
    URL = BaseURL + 'delete'
    param_list = {'objectId': obj_id}
    req = requests.delete(URL, headers=AuthHeader, params=param_list)
    if Debug:
        print('delete request info:')
        print('request URL: ', req.url)
        print('server response ', req.text)
    return req.text
    
'''

Delete with Options
    Deletes objects that have options associated with their removal.
    This method currently works only with the deletion of dynamic records
    from the Address Manager database. When deleted, dynamic records present
    the option of not dynamically deploying to DNS/DHCP Server.
Output / Response
    None.

'''
    

def delete_with_options(obj_id, options):
    URL = BaseURL + 'deleteWithOptions'
    param_list = {
        'objectId': obj_id,
        'options': options
    }
    req = requests.delete(URL, headers=AuthHeader, params=param_list)
    return req.text


# Deletes all data and RRs in the Zone tree including other Zones

def delete_zone(fqdn):
    zone_id = get_zone_id(fqdn)
    if zone_id:
        val = delete_object(zone_id)
        return val

def get_host_records_by_hint(start, count, options):
    URL = BaseURL + 'getHostRecordsByHint'
    params = {
      'start': start,
      'count': count,
      'options': options
    }
    req = requests.get(URL, headers=AuthHeader, params=params)
    return req.json()


def get_zones_by_hint(id, start, count, opts):
        URL = BaseURL + 'getZonesByHint'
        params = {
            'containerId': id,
            'start': start,
            'count': count,
            'options': opts
        }
        req = requests.get(URL, headers=AuthHeader, params=params)
        return req.json()


def assign_ip4Address(config_id, ip_addr, mac_addr, host_info, action, props):
    URL = BaseURL + 'assignIP4Address'
    params = {
        'configurationId': config_id,
        'ip4Address': ip_addr,
        'macAddress': mac_addr,
        'hostInfo': host_info,
        'action': action,
        'properties': props
    }
    req = requests.post(URL, headers=AuthHeader, params=params)
    return req.json()

'''

Low level functions to manipulate the IP address space

'''

def add_IP4_Network(bid, cidr, props):
    URL = BaseURL + 'addIP4Network'

    param_list = {
        'blockId': bid,
        'CIDR': cidr,
        'properties': props
    }

    req = resquests.post(URL, headers=AuthHeader, params=param_list)
    return req.json()

def add_IP4_Block_By_CIDR(pid, cidr, props):
    URL = BaseURL + 'addIP4BlockByCIDR'
    
    param_list = {
            'parentId': pid,
            'CIDR': cidr,
            'properties': props
    }

    req = resquests.post(URL, headers=AuthHeader, params=param_list)
    return req.json()


#
# assumes the two global variable have been set: ConfigName, ViewName
#


def set_config_id():
    global ConfigId

    config_info = get_entity_by_name(RootId, ConfigName, 'Configuration')
    ConfigId = config_info['id']

def set_view_id():
    global ViewId

    if ConfigId > 0:
        view_info = get_entity_by_name(ConfigId, ViewName, 'View')
        ViewId = view_info['id']
    else:
        print('Error: The parent (Configuration) Id must be set before setting the View Id')
        sys.exit()
        
#
# given andy.bozo.cathy.dan.ca it returns bozo.cathy.dan.ca
#

def parent_name(fqdn):
    return fqdn.split('.',1)[1]

#
# Get the Object info (Id and parentId) given a FQDN or a CIDR block
#

  
def get_object_info(fqdn):
    id = ViewId
    names = fqdn.split('.')
    lg = len(names)
    for name in names[::-1]:
        info = get_entity_by_name(id, name, 'Entity')
        id = info['id']
        if Debug:
            print(id, info)
    return info


def get_object_id(fqdn):
    info = get_object_info(fqdn)
    return info['id']
    

#
# return the parent ID of an Object based on its name
#


def get_parent_id(fqdn):
    parent_zone = parent_name(fqdn)
    parent_id = get_object_id(parent_zone)
    return parent_id


def get_host_info(vid, fqdn):
    names = fqdn.split('.')
    lg = len(names)
    igd = vid
    for name in names[::-1]:
        info = get_entity_by_name(id, name, 'Entity')
        if info['type'] == 'Zone':
            id = info['id']
            print(names[:l])
            lg -= 1
        else:
            break
    name = '.'.join(names[:l])
    info = get_entity_by_name(id, name, 'GenericRecord')
    return info
    
#
# retrieves the Id of a Zone or Subzone
#

def get_zone_id(fqdn):
    info = get_object_info(fqdn)
    if info['type'] == 'Zone':
        return info['id']
    else:
        print(fqdn, 'is not a zone')


def test_get_entity_by_name():
    id = RootId

    lst = ['Test', 'Public', 'ca', 'utoronto', 'frodo', 'ring', 'goofy']
    for nm in lst:
        type = get_entity_by_name(id, nm, 'Entity')['type']
        info = get_entity_by_name(id, nm, type)
        type = info['type']
        props = info['properties']
        id = info['id']
        print('name', nm, 'id', id, 'type', type, 'properties', props)


def test_get_entity_by_id():
    for id in [2200891, 2203565, 2217649, 2217650, 2512206, 2512207, 2516972]:
        vals = get_entity_by_id(id)
        pprint(vals)

def test_get_entities():
    print('\nGetEntities')
    vals = get_entities(2512207, 'GenericRecord', 0, 20)
    pprint(vals)
    print('\nGet Entities by Name')
    info = get_entities_by_name(2512207, "", 'GenericRecord', 0, 10)
    pprint(info)
    print('\nGet Entity by Name')
    info = get_entity_by_name(2512207, "", 'GenericRecord')
    pprint(info)

def test_get_parent():
    for objid in [2510060, 2512206, 2217649]:
        vals = get_parent(objid)
        print('child id', objid)
        print('parent object',vals)
    
    print()
    for nm in ['goofy.zulu.org', 'frodo.utoronto.ca']:
        pid = get_parent_id(nm)
        print(nm, 'has a parent id of', pid)
    
    print()
    for nm in ['goofy.zulu.org', 'frodo.utoronto.ca']:
        id = get_object_id(nm)
        pinfo = get_parent(id)
        parent = parent_name(nm)
        print('Parent info for', parent, pinfo)


# Tests for Searching for and Retrieving Entities

def test_custom_search():
    filters = ['ttl=86400']
    vars = custom_search(filters, 'MXRecord', 0, 25)
    pprint(vars)

    filters = ['recordType=A', 'rdata=128.100.103*']
    vars = custom_search(filters, 'GenericRecord', 0, 15)
    pprint(vars)

#
# is_zone takes a name/fqdn as input and returns: False
# if it is not a zone, otherwise the object_Id of the zone
#

def is_zone(fqdn):

    vals = search_by_object_types(fqdn, 'Zone', 0, 3)
    return vals

#
# Add a zone using the generic add_generic call rather than
# the specific add_zone()one
#

    
def add_zone_generic(fqdn):
    dot = '.'
    n = fqdn.split(dot)
    nm = n[0]
    subzone = dot.join(n[1:])
    par_id = get_object_id(subzone)
    props = 'deployable=true|'
    props += 'absoluteName=' + fqdn + '|'
    ent = {
        'name': nm,
        'type': 'Zone',
        'properties': props
    }
    val = add_entity(par_id, ent)
    return val


def test_rr_functions():

    ip = '128.100.103.123'
    props = 'reverseRecord=false|'
    ttl = '3600'
    zone = 'bozo.math.utoronto.ca'
    fqdn = 'hamster' + '.' + zone

    if Debug:
        print(fqdn,ip,ttl,props)

    vals = add_host_record(fqdn, '128.100.103.123', 3600, props)
    pprint(vals)

def test_zone_functions():
    dot = '.'
    
    for z in ['zulu.org', 'watusi.zulu.org']:
        val = is_zone(z)
        print(val)
        val = delete_zone(z)
        val = add_zone_generic(z)
        print(val)

    print('Generic zone add')
    for z in ['yes.uoft.ca', 'no.uoft.ca']:
        ent = add_zone_generic(z)
        print(ent)
        val = get_object_info(z)
        print(val)
    
#    print('Adding a Zone Template')
#    val = add_zone_template(ViewId, 'default', 'deployable=true')
#    print(val)
        
#    val = delete_zone(zone)
    
'''

# zones = get_zones_by_hint(view_id,1,10, op)
# host_info = get_host_info(view_id, 'bozo.math.utoronto.ca')
# if Debug:
#     pprint(host_info)

#   vals = delete_zone('bozo.utoronto.ca')
#   vals = add_zone('ring.frodo.utoronto.ca')
#   print 'Zone return value: ', vals
#   pprint(vals)

#   fqdn = '.bozo.utoronto.ca'
#   ip = '128.100.103.254'
    ttl = 3600
    props = 'reverseRecord=false|'

'''

def test_generic_methods():
    test_get_entity_by_name()
    test_get_entity_by_id()
    test_get_entities()
    print()
    print('test getParent')
    test_get_parent()
    print()
    print('get object id')
    id = get_object_id('goofy.ring.frodo.utoronto.ca')
    print(id)


def test_category_search():
    entities = search_by_category('utoronto', Categories['resourceRecords'], 0, 20)
    pprint(entities)
    entities = search_by_category('math', Categories['resourceRecords'], 0, 20)
    pprint(entities)
    entities = search_by_category('128', Categories['IP4Objects'], 0, 20)
    pprint(entities)
    entities = search_by_category('cs.utoronto.ca', Categories['all'], 0, 20)
    pprint(entities)

def test_object_type_search():
    types = 'View,Zone,HostRecord,GenericRecord'
    vars = search_by_object_types('*ab*', types, 0, 100)
    pprint(vars)

def test_search_functions():
    print('Custom Search')
    test_custom_search()
    print('\nSearch by Category')
    test_category_search()
    print('\nSearch by Object Type')
    test_object_type_search()
    
def qwe():
    types = 'View,Zone,HostRecord,GenericRecord'
    types = 'Configuration,View'
    vars = search_by_object_types('test', types, 0, 100)
    pprint(vars)
    for var in vars:
        for k in var:
            if k == 'properties':
                if var[k] is not None:
                    vals = var[k].split('|')
                    for val in vals:
                        print(val)
            else:
                print(k, var[k])
        print()

def main():

    bam_init()

    sysinfo = get_system_info()
    if Debug:
        print('System Information:')
        for item in sysinfo.split('|'):
            print(item)

    test_search_functions()
    sys.exit()
    test_zone_functions()
    test_generic_methods()
    
#    test_rr_functions()

    zone = 'bozo.utoronto.ca'
    id = Fqdn2Id(zone)
    print('Parent of', zone, 'is', id)

    zone = 'utoronto.ca'
    id = Fqdn2Id(zone)
    print('Parent of', zone, 'is', id)

    zone = 'ca'
    id = Fqdn2Id(zone)
    print('Parent of', zone, 'is', id)


    hostname = 'bozo.cs.utoronto.ca'
    ipaddr = '128.100.1.2'
    macaddr = 'aa:bb:cc:dd:ee:ff'
    reverseFlag = 'false'
    sameAsZoneFlag = 'false'
    vals = [hostname, macaddr, reverseFlag, sameAsZoneFlag]
    hostinfo = ','.join(vals)
    if Debug:
        print(hostinfo)
    action = 'MAKE_DHCP_rESERVED'
    properties = 'name=frodo|locationCode=CA TOR UOFT'
    res = assign_ip4Address(
            conf_id, ipaddr, macaddr, hostinfo, action, properties
            )
    if Debug:
        pprint(res)

    fqdn = 'utoronto.ca'
    obj_id = get_object_id(fqdn)
    par_id = get_parent_id(obj_id)
    print(par_id)

    parent_id = Fqdn2Id(fqdn)
    print(parent_id)

    pid = Fqdn2Id('utoronto.ca')
    vars = get_entities(pid, 'HostRecord', 0, 10)
    pprint(vars)


    host_info = add_resource_record(fqdn, 'HostRecord', ip, ttl, props)
    if Debug:
        print('\nAdd Host Response:')
        pprint(host_info)

    host_info = add_host_record(fqdn, ip, ttl, props)
    if Debug:
        print('\nAdd Host Response:')
        pprint(host_info)

    obj_id = get_object_id('ca')
    print(obj_id)
    print()

    obj_id = get_object_id('utoronto.ca')
    print(obj_id)
    print()

    obj_id = get_object_id('bozo.math.utoronto.ca')
    print(obj_id)

    host_info = get_host_info(view_id, 'mail.utoronto.ca')
    if Debug:
        pprint(host_info)

    zone_info = get_entity_by_name(zone_info['id'], 'utoronto', 'Zone')
    pprint(zone_info)

    host_info = get_entity_by_name(zone_info['id'], 'bozo', 'HostRecord')
    if Debug:
        print('\nHost info for ' + fqdn + ':')
        pprint(host_info)

    response = delete_object(host_id)
    pprint(response)

    response = bam_logout()
    if Debug:
        pprint(response)


if __name__ == "__main__":
    main()
