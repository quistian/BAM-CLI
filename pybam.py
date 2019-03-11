#!/usr/local/bin/python3 -tt

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


'''

RESTful Python API for BAM
REST WADL: https://proteus.utoronto.ca/Services/REST/application.wadl

From JumpStart to BAM
User Group Webinar - Making APIs Work for You - Episode 1

- Web Layer and API Layer

	Connect -> Login -> API Calls -> Logout

	SOAP one session, and then at end closes

	REST single shot sessions as request and responses

	URLs contain action verbs: Service, Create, Read, Update, Delete

	API account is the same as a normal user account (hybrid as well)

- Logs -> /var/log/Server.log

- API calls are small unit operations each with custom input and output

- To send NULL values use e.g. var = ''

- BAM v8.1.0 and present support REST

- Sequence of steps for the REST API to e.g. add a host record to bozo.utoronto.ca

    a. Get the REST onetime Token, add it to the https Header
    b. Get the Parent Configuration object by name
    c. Get the Parent View object by name
    d. Get the Parent Zone object by name, using the fqdn (i.e. utoronto.ca)


'''

import os
import sys
import json
import requests
import getpass

from pprint import pprint

uname = 'api-test-user'
pw = 't1e2s3t4'
creds_ro = {'username': uname, 'password': pw}

uname = 'api-test-user2'
pw = 't5e6s7t8'
creds_rw = {'username': uname, 'password': pw}


'''

Global Variables convention:
    * start with UpperCase
    * have no _ character
    * may have mid UpperCase words

'''

Debug = False
Debug = True

Creds = creds_rw

BaseURL = 'https://proteus.utoronto.ca/Services/REST/v1/'

RootId = 0
ConfigId = 0
ViewId = 0

ConfigName = 'Production'
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
        'StartOfAuthority',
        'ExternalHostRecord'
]

RRObjectTypes = ObjectTypes[3:]

RRTypeMap = {
        'MX': {'obj_type': 'MXRecord', 'prop_key': 'linkedRecordName'},
        'A': {'obj_type': 'HostRecord', 'prop_key': 'addresses'},
        'a': {'obj_type': 'GenericRecord', 'prop_key': 'rdata'},
        'PTR': {'obj_type': 'GenericRecord', 'prop_key': 'rdata'},
        'CNAME': {'obj_type': 'AliasRecord', 'prop_key': 'linkedRecordName'},
        'TXT': {'obj_type': 'TXTRecord', 'prop_key': 'txt'},
}

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

TopLevelDomains = ['ca', 'edu', 'org', 'net', 'com', 'int', 'us' ]

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
    params = {'parentId': id, 'name': name, 'type': type}
    req = requests.get(URL, headers=AuthHeader, params=params)
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


def get_entity_by_id(entityid):
    URL = BaseURL + 'getEntityById'
    params = {'id': str(entityid)}
    req = requests.get(URL, headers=AuthHeader, params=params)
    return req.json()


'''

Get Entities

Returns an array of requested child objects for a given parentId value.
Some objects returned in the array may not have their properties field set.
For those objects, you will need to call them individually using
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
            defaults to 10

Returns a list of branch items given the root one level up

'''

def get_entities(parentid, type, start=0, count=10):
    URL = BaseURL + 'getEntities'
    params = {'parentId': parentid, 'type': type, 'start': start, 'count': count}
    req = requests.get(URL, headers=AuthHeader, params=params)
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
    'id': 217650,
    'name': 'utoronto',
    'type': 'Zone',
    'properties': 'deployable=true|absoluteName=utoronto.ca|'
}

'''


def get_parent(childid):
    URL = BaseURL + 'getParent'
    params = {'entityId': str(childid)}
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

def custom_search(filters, type, start=0, count=10):
    URL = BaseURL + 'customSearch'
    params = {
            'filters': filters,
            'type': type,
            'options': '',
            'start': start,
            'count': count,
    }
    req = requests.get(URL, headers=AuthHeader, params=params)
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

def search_by_category(key, category, start=0, count=10):
    URL = BaseURL + 'searchByCategory'

    params = {
        'keyword': key,
        'category': category,
        'start': start,
        'count': count
    }

    req = requests.get(URL, headers=AuthHeader, params=params)
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


def search_by_object_types(key, types, start=0, count=10):
    URL = BaseURL + 'searchByObjectTypes'
    params = {
        'keyword': key,
        'types': types,
        'start': start,
        'count': count
    }
    req = requests.get(URL, headers=AuthHeader, params=params)
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


def get_entities_by_name(parentid, name, type, start=0, count=10):
    URL = BaseURL + 'getEntitiesByName'
    params = {
        'parentId': parentid,
        'name': name,
        'type': type,
        'start': start,
        'count': count,
    }
    req = requests.get(URL, headers=AuthHeader, params=params)
    return req.json()

'''

Get Entities by Name Using Options

Returns an array of entities that match the specified name and object type. Searching behavior can be
changed by using the options.

Output / Response
Returns an array of entities. The array is empty if there are no matching entities.

API call:
APIEntity[] getEntitiesByNameUsingOptions ( long parentId, String name, String type, int
start, int count, String options )

Parameters:

    Parameters:

    parentId: The object ID of the parent object of the entities to be returned.
    name:   The name of the entity.
    types:  The type of object to be returned. This value must be one of the object types listed
            in Object Types
    start:  Indicates where in the list of returned objects to start returning objects. The list
            begins at an index of 0. This value cannot be null or empty.
    count:  The maximum number of objects to return. The default value is 10. This value
            cannot be null or empty.
    options: A string containing options. Currently the only available option is
            ObjectProperties.ignoreCase. By default, the value is set to false. Setting this
            option to true will ignore the case-sensitivity used while searching entities by name.

            ObjectProperties.ignoreCase = [true | false]

'''

def get_entities_by_name_using_options(parentid, name, typ, options='false', start=0, count=10):
    URL = BaseURL + 'getEntitiesByNameUsingOptions'
    params = {
        'parentId': parentid,
        'name': name,
        'type': type,
        'start': start,
        'count': count,
        'options': options,
    }
    req = requests.get(URL, headers=AuthHeader, params=params)
    return req.json()

'''

Get MAC Address

Returns an APIEntity for a MAC address.

Output / Response
Returns an APIEntity for the MAC address. Returns an empty APIEntity if the MAC address does not exist.
The property string of the returned entity should include the MAC address:
    address=nn-nn-nn-nn-nn-nn|
If the MAC address is in a MAC pool, the property string includes the MAC pool information:
    macPool=macPoolName|

API call:
APIEntity getMACAddress ( long configurationId, String macAddress )

Parameter Description
    configurationId: The object ID of the configuration in which the MAC address is located.
    macAddress: The MAC address in the format nnnnnnnnnnnn, nn-nn-nn-nn-nn-nn or
                nn:nn:nn:nn:nn:nn, where nn is a hexadecimal value.

'''

def get_MAC_Address(confid, macaddr):
    URL = BaseURL + 'getMACAddress'
    params = {
        'configurationId': confid,
        'macAddress': macaddr,
    }
    req = requests.get(URL, headers=AuthHeader, params=params)
    return req.json()



'''

Updating Objects

Generic methods for updating an object.

Updating an object involves two steps:
    1. Building the object or parameter string used to update the object.
    2. Performing the update.

'''

'''
Update

Updates entity objects.

API call: All entity update statements follow this format:

void update ( APIEntity entity )

Parameter Description
entity: The actual API entity passed as an entire object that has its mutable
        values updated

'''

def update_object(entity):
    URL = BaseURL + 'update'
    req = requests.put(URL, headers=AuthHeader, json=entity)

'''

Update with Options

Updates objects requiring a certain behavior that is not covered by the regular update() method. This
method is currently used for CName, MX and SRV records, and the option is only applicable to these
types.

Output / Response: None

API call:
void updateWithOptions ( APIEntity entity, String options )

Parameter Description

    entity: The actual API entity to be updated.

    options: A string containing the update options. Currently, only one option is
             supported:

                linkToExternalHost=boolean

            If true, update will search for the external host record specified in
            linkedRecordName even if a host record with the same exists under the same DNS View.
            If the external host record is not present, it will throw an exception.
            
            If false, update will search for the host record specified in linkedRecordName

'''

def update_with_options(ent, opts):
    URL = BaseURL + 'updateWithOptions'
    req = requests.put(URL, headers=AuthHeader, json=ent)
    return req.json()


'''

Deleting Objects

Generic methods for deleting an object.
There are two generic methods for getting entity values:
    * Delete
    * Delete with Options

Delete:
    Deletes an object using the generic delete() method.
    
Output / Response:
    None.
    
API call:
    Pass the entity ID from the database identifying the object to be deleted.
    void delete ( long ObjectId )

Parameter Description:
    ObjectId The ID for the object to be deleted.

Output / Response
    None

'''

def delete(obj_id):
    URL = BaseURL + 'delete'
    param = {'objectId': obj_id}
    req = requests.delete(URL, headers=AuthHeader, params=param)
    
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
    params = {
        'objectId': obj_id,
        'options': options
    }
    req = requests.delete(URL, headers=AuthHeader, params=params)


'''

Linked Entities

Generic methods for getting, link or unlink entities.

    * Get Linked Entities
    * Link Entities
    * Unlink Entities

'''

'''

Get Linked Entities

Returns an array of entities containing the entities linked to a specified entity.
The array is empty if there are no linked entities.

Output / Response
Returns an array of entities. The array is empty if there are no linked entities.

API call:
APIEntity[] getLinkedEntities ( long entityId, String type, int start, int count)

Parameter Description
    entityId: The object ID of the entity for which to return linked entities.

    type:   The type of linked entities which need to be returned.
            This value must be one of the types listed in Object Types on page 209.

! Attention:
    * While specifying a resource record as the entityId, if you want to find
    all the records (CNAME, MX, or SRV records) having links to this
    record, you can use RecordWithLink for the type parameter.

    * When specifying a MAC address as the entityId, this method
    returns the IPv4 address associated with the MAC address. When
    appropriate, leaseTimeand expiryTimeinformation also appears in
    the returned properties string.

    start: Indicates where in the list of returned objects to start returning objects.
           The list begins at an index of 0. This value cannot be null or empty.

    count: The maximum number of objects to return.

'''

def get_linked_entities(entityid, obj_type, start=0, count=10):
    URL = BaseURL + 'getLinkedEntities'

    params = {
            'entityId': entityid,
            'type': obj_type,
            'start': start,
            'count': count,
    }

    req = requests.get(URL, headers=AuthHeader, params=params)
    return req.json()
    
'''

Link Entities
    Establishes a link between two specified Address Manager entities.
Output / Response
    None.

API call:
void linkEntities ( long entity1Id, long entity2Id, String properties )

Parameter Description:

entity1Id: The object ID of the first entity in the pair of linked entities.
entity2Id: The object ID of the second entity in the pair of linked entities.
properties: Adds object properties, including user-defined fields.


'''

def link_entities(entity1id, entitity2id, properties):
    URL = BaseURL + 'linkEntities'
    
    params = {
        'entity1Id': entity1id,
        'entity2Id': entity2id,
        'properties': properties
    }
    
    req = requests.put(URL, headers=AuthHeader, params=params)
    return req.json()

'''
Unlink Entities
    Removes the link between two specified Address Manager entities.
    
Output / Response
    None.

This method works on the following types of objects and links:
    Type of entity1Id   Type of entity2Id   Result
    Any entity          Tag                 Removes the tag linked to the entity.
    MACPool             MACAddress          Removes MAC address from MAC pool.
    MACAddress          MACPool             Removes Mac Pool from MAC address.
    User                UserGroup           Removes Group from User
    UserGroup           User                Removes User from Group
    etc...


'''


def unlink_entities(entity1id, entitity2id, properties):
    URL = BaseURL + 'unlinkEntities'
    
    params = {
        'entity1Id': entity1id,
        'entity2Id': entity2id,
        'properties': properties
    }
    
    req = requests.put(URL, headers=AuthHeader, params=params)
    return req.json()

'''

IPAM Functions

Add IPv4 Block by CIDR
    Adds a new IPv4 Block using CIDR notation.

Output / Response
    Returns the object ID for the new IPv4 block.

API call:
    long addIP4BlockByCIDR ( long parentId, String CIDR, String properties )
    
Parameter Description:
    parentId: The object ID of the target object’s parent object.
    CIDR: The CIDR notation defining the block (for example, 10.10/16).
    properties: A string containing options. For more information about the available
                options, refer to IPv4Objects on page 248 in the
                Property Options Reference section.


'''

'''

Assign IPv4 Address
    Assigns a MAC address and other properties to an IPv4 address.

Output / Response
    Returns the object ID for the newly assigned IPv4 address.

API call:
    long assignIP4Address (
        long configurationId, 
        String ip4Address, 
        String macAddress,
        String hostInfo,
        String action,
        String properties
    )

Parameter: Description

configurationId:
    The object ID of the configuration in which the IPv4 address is located.

ipv4Address:
    The IPv4 address.

macAddress:
    The MAC address to assign to the IPv4 address. The MAC address
    can be specified in the format:
        nnnnnnnnnnnn, nn-nn-nn-nn-nn-nn or nn:nn:nn:nn:nn:nn,
        where nn is a hexadecimal value.

hostInfo:
    A string containing host information for the address in the following format:
        hostname,viewId,reverseFlag,sameAsZoneFlag,
        hostname,viewId,reverseFlag,sameAsZoneFlag,
        hostname,viewId,reverseFlag,sameAsZoneFlag
    Where:
        hostname - FQDN for host record to be added
        viewId - object ID of the view under which this host should be created
        reverseFlag - flag indicating if a reverse should be created (true|false)
        sameAsZoneFlag - The flag indicating if record should be created as same
            as zone record. The possible values are true and false
    The comma-separated parameters may be repeated in the order shown above.
    The string must not end with a comma.

action:
    This parameter must be set to the constants in IP Assignment Action Values:
        MAKE_STATIC, MAKE_RESERVED or MAKE_DHCP_RESERVED

properties:
    A string containing the following property, including user-defined fields:

        ptrs:
            a string containing the list of unmanaged external host records to
            be associated with the IPv4 address in the following format:
                viewId,exHostFQDN[, viewId,exHostFQDN,...]

            EntityProperties props = new EntityProperties();
            props.addProperty(
                ObjectProperties.ptrs,
                123,exHostFQDN.com,456,exHostFQDN.net"
            )
            long addressId =
                service.assignIP4Address(
                    configurationId,
             IPv4Address, macAddressStr, hostInfo,
         IPAssignmentActionValues.MAKE_STATIC, props.getPropertiesString() );

 name -- name of the IPv4 address.

    locationCode - the hierarchical location code consists of a set of 1 to 3
    alpha-numeric strings separated by a space. The first two characters
    indicate a country, followed by next three characters which indicate
    a city in UN/ LOCODE. New custom locations created under a UN/LOCODE
    city are appended to the end of the hierarchy. For example, CA TOR
    OF1 indicates: CA= Canada TOR=Toronto OF1=Office 1.

    The code is case-sensitive. It must be all UPPER CASE letters.
    The country code and child location code should be alphanumeric strings.


'''

def assign_IP4_Address(configid, ipaddr, macaddr, hostinfo, action, props):
    URL = BaseURL + 'assignIP4Address'

    params = {
        'configurationId': configid,
        'ip4Address': ipaddr,
        'macAdress': macaddr,
        'hostInfo': hostinfo,
        'action': action,
        'properties': props
    }

    req = requests.post(URL, headers=AuthHeader, params=params)
    return req.json()


def add_IP4_block_by_CIDR(parentid, cidr, properties):
    URL = BaseURL + 'addIP4BlockByCIDR'
    
    params = {
        'parentId': parentid,
        'CIDR': cidr,
        'properties': properties
    }
    
    req = requests.post(URL, headers=AuthHeader, params=params)
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

    params = {
        'blockId': bid,
        'CIDR': cidr,
        'properties': props
    }

    req = resquests.post(URL, headers=AuthHeader, params=params)
    return req.json()

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
    Returns the object ID for the new Entity.

API call: long addEntity( long parentId, APIEntity entity )

Parameter Description
    parentId: The object ID of the parent DNS view or
              DNS zone to which the zone is added.
          
entity:  The zone name, without any . (dot) characters, to be added.

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
        parent_id = get_id_by_name(parent_name(fqdn))
        info = get_entity_by_id(parent_id)
        if info['type'] != 'Zone':
            bam_error('The parent of', fqdn, 'is not a zone')
    
    params = {
            'parentId': parent_id,
            'absoluteName': fqdn,
            'properties': 'deployable=true',
    }

    req = requests.post(URL, headers=AuthHeader, params=params)
    return req.json()


'''

Get Zones by Hint
    Returns an array of accessible zones of child objects for a given containerId value.

Output / Response
    Returns an array of zones based on the input argument without their properties fields populated, or returns
    an empty array if containerId is invalid. If no access right option is specified, the View access level will be
    used by default.

API Call:
    APIEntity[] getZonesByHint( long containerId, int start, int count, String options )

Parameters:
    containerId: The object ID for the container object. It can be the object ID of any object in
                 the parent object hierarchy. The highest parent object can be the configuration level.
    start:  Indicates where in the list of objects to start returning objects.
            The list begins at an index of 0.

    count:  Indicates the maximum number of child objects that this method will return.
            The maximum number of child objects cannot exceed more than 10.

    options:
    A string containing options. The Option names available in the ObjectProperties are:
        ObjectProperties.hint, ObjectProperties.accessRight, and ObjectProperties.overrideType.
        Multiple options can be separated by a | (pipe) character. For example:
            hint=ab|overrideType=HostRecord|accessRight=ADD
        The values for ObjectProperties.hint option can be the prefix of a zone name.  For example:
            String options = ObjectProperties.hint + "=abc|"
        The values for the ObjectProperties.accessRight and ObjectProperties.overrideType
        options must be one of the constants listed in Access Right Values on page 189
        and Object Types on page 209. For example:
            String options = ObjectProperties.accessRight + "=" + AccessRightValues.AddAccess +
                "|"+ ObjectProperties.overrideType + "=" + ObjectTypes.HostRecord;

'''

def get_zones_by_hint(containerid, options, start=0, count=1):
        URL = BaseURL + 'getZonesByHint'
        if count > 10:
            count = 10
        params = {
            'containerId': containerid,
            'start': start,
            'count': count,
            'options': options
        }
        req = requests.get(URL, headers=AuthHeader, params=params)
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
    
    params = {
        'parentId': parent_id,
        'name': name,
        'properties': properties,
    }
    
    req = requests.post(URL, headers=AuthHeader, params=params)
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

def add_resource_record(fqdn, typ, rrdata, ttl=86400, props='comments=EmTee|'):
    URL = BaseURL + 'addResourceRecord'
    params = {
        'viewId': ViewId,
        'absoluteName': fqdn,
        'type': typ,
        'rdata': rrdata,
        'ttl': str(ttl),
        'properties': props
    }
    if Debug:
        print(params)
    req = requests.post(URL, headers=AuthHeader, params=params)
    return req.json()


'''

Host Records
A host record, or A record, designates an IP address for a device.
A new host requires a name and an IP address. Multiple addresses may exist
for the same device. Set the time-to-live for this record to an override value
here so that the record has a longer or shorter ttl. A comment field is also included.


Add Host Record
Adds host records for IPv4 or IPv6 addresses. All addresses must be valid addresses.
This method will add the record under a zone. In order to add records under templates,
you must use Add Entity for Resource Records on page 124.
When adding a host record, the reverseRecord property, if not explicitly set
in the properties string, is set to true and Address Manager creates
a reverse record automatically. IPv4 addresses can be added in both
workflow and non-workflow mode. IPv6 addresses can be added in non-workflow mode only.
For more information on workflow mode, see Workflow Change Requests on page 182.

Output / Response
Returns the object ID for the new host resource record.
API call:
long addHostRecord(long viewId, String absoluteName, String addresses,
                    long ttl, String properties)

Parameters:

    viewId: The object ID for the parent view to which this record is being added.
    
    absoluteName: The FQDN for the host record. If you are adding a record in a zone
                  that is linked to a incremental Naming Policy,
                  a single hash (#) sign must be added at the appropriate location
                  in the FQDN. Depending on the policy order value,
                  the location of the single hash (#) sign varies.
    addresses: A list of comma-separated IP addresses
                (for example, 10.0.0.5,130.4.5.2).
    
    ttl: The time-to-live value for the record.
         To ignore the ttl, set this value to -1.
         
    properties:  Adds object properties, including comments and user-defined fields.

'''


def add_host_record(fqdn, ips, ttl=86400, properties='comments=EnTee|'):
    URL = BaseURL + 'addHostRecord'

# adding to the top level of the zone requires a leading dot
    if is_zone(fqdn):
        fqdn = '.' + fqdn

    params = {
      'viewId': ViewId,
      'absoluteName': fqdn,
      'addresses': ips,
      'ttl': ttl,
      'properties': properties
    }

    req = requests.post(URL, headers=AuthHeader, params=params)
    return req.json()


'''

Add Bulk Host Records

Adds host records using auto-increment from the specific starting address.
This method will add the record under a zone. In order to add records under templates,
you must use Add Entity for Resource Records on page 124.
This method adds host records to a zone linked to a DNS naming policy,
each with an IP address autoincremented starting from a specific address in a network.

Output / Response
Returns an array of host record APIEntity objects based on available addresses and number of IP
addresses required. If no addresses are available, an error will be shown.
API call:
APIEntity[] addBulkHostRecord ( long viewId, String absoluteName, long ttl, long
networkId, String startAddress, int numberOfAddresses, String properties)

Parameter Description
viewId The object ID for the parent view to which this record is being added.
absoluteName The FQDN for the host record. If you are adding a record in a zone that is linked
to a incremental Naming Policy, a single hash (#) sign must be added at the
appropriate location in the FQDN. Depending on the policy order value, the
location of the single hash (#) sign varies.
ttl The time-to-live value for the record. To ignore the ttl, set this value to -1.
networkId The network which to get the available IP addresses. Each address is used for
one host record.
startAddress The starting IPv4 address for getting the available addresses.
numberOfAddresses The number of addresses.
properties excludeDHCPRange=true/false, if true then IP addresses within a DHCP
range will be skipped. This argument can also contain user-defined fields.


'''

'''

Get Host Record by Hint
    Returns an array of objects with host record type.

Output / Response
    Returns an array of host record APIEntity objects.

API call:
    APIEntity[] getHostRecordsByHint ( int start, int count, String options)

Parameters:

    start:  Indicates where in the list of objects to start returning objects.
            The list begins at an index of 0.
    count:  Indicates the maximum of child objects that this method will return.
            The value must be less than or equal to 10.

    options: A string containing options. The supported options are hint and retrieveFields.
        Multiple options can be separated by a | (pipe) character. For example:
            hint=^abc|retrieveFields=false
        If the hint option is not specified in the string, searching criteria will be based on
        the same as zone host record. The following wildcards are supported in the hint option.

        * ^—matches the beginning of a string. For example: ^ex matches example but not text.
        * $—matches the end of a string. For example: ple$ matches example but not please.
        * ^ $—matches the exact characters between the two wildcards. For example:
            ^example$ only matches example.
        * ?—matches any one character. For example: ex?t matches exit.
        * *—matches one or more characters within a string.
            For example: ex*t matches exit and excellent.

        The default value for the retrieveFields option is set to false. If the option is set
        to true, user-defined field will be returned. If the options string does not contain
        retrieveFields, user-defined field will not be returned.

'''

def get_host_records_by_hint(options, start=0, count=10):
    URL = BaseURL + 'getHostRecordsByHint'
    params = {
      'options': options,
      'start': start,
      'count': count,
    }
    req = requests.get(URL, headers=AuthHeader, params=params)
    return req.json()

# Editing specific types of Resource Records

'''

Add Text Records

    This method will add the record under a zone.

Output / Response:
    Returns the object ID for the new TXT record.

API call:
long addTXTRecord ( long viewId, String absoluteName, String txt, long ttl, String properties )
Parameter Description
viewId:
    The object ID for the parent view to which the record is being added.
absoluteName:
    The FQDN of the text record. If you are adding a record in a zone
    that is linked to a incremental Naming Policy, a single hash (#)
    sign must be added at the appropriate location in the FQDN. Depending
    on the policy order value, the location of the single hash (#) sign
    varies.

txt:
    The text data for the record.
ttl:
    The time-to-live value for the record. To ignore the ttl, set this value to -1.
properties:
    Adds object properties, including comments and user-defined fields.

'''

def add_TXT_Record(absname, txt, ttl=86400, props='comments=EmTee|'):
    URL = BaseURL + 'addTXTRecord'
    params = {
        'viewId': ViewId,
        'absoluteName': absname,
        'txt': txt,
        'ttl': ttl,
        'properties': props
    }
    req = requests.post(URL, headers=AuthHeader, params=params)
    return req.json()

'''

Generic Records

Use the generic resource record methods to add and update the
following resource record types:
    A6, AAAA, AFSDB, APL, CAA, CERT, DNAME, DNSKEY, DS, ISDN, KEY,
    KX, LOC, MB, MG, MINFO, MR, NS, NSAP, PX, RP, RT, SINK, SSHFP,
    TLSA, WKS, and X25.
The fields available are:
    name, type (which defines the custom record type), and data
    (the rdata value for the custom type). The time-to-live for this
    record can be set to an override value, so the record has a longer
    or shorter ttl. A comment field is also included.

Output / Response
    Returns the object ID for the new generic resource record

'''

def add_Generic_Record(viewid, absname, rr_type, rr_data, ttl, props):
    URL = BaseURL + 'addGenericRecord'
    params = {
        'viewId': viewid,
        'absoluteName': absname,
        'type': rr_type,
        'rdata': rr_data,
        'ttl': ttl,
        'properties': props
    }
    req = requests.post(URL, headers=AuthHeader, params=params)
    return req.json()

def add_MX_Record(absname, priority, mx_host, ttl=86400, props='comments=EmTee|'):
    URL = BaseURL + 'addMXRecord'
    params = {
        'viewId': ViewId,
        'absoluteName': absname,
        'priority': priority,
        'linkedRecordName': mx_host,
        'ttl': ttl,
        'properties': props
    }
    req = requests.post(URL, headers=AuthHeader, params=params)
    return req.json()


def add_ExternalHost_Record(viewid, ex_host, props):
    URL = BaseURL + 'addExternalHostRecord'
    params = {
        'viewId': viewid,
        'name': ex_host,
        'properties': props
    }
    req = requests.post(URL, headers=AuthHeader, params=params)
    return req.json()


def add_Alias_Record(absname, link, ttl=86400, props='comments=EmTee|'):
    URL = BaseURL + 'addAliasRecord'
    params = {
        'viewId': ViewId,
        'absoluteName': absname,
        'linkedRecordName': link,
        'ttl': ttl,
        'properties': props
    }
    req = requests.post(URL, headers=AuthHeader, params=params)
    return req.json()


def get_system_info():
    URL = BaseURL + 'getSystemInfo'
    req = requests.get(URL, headers=AuthHeader)
    code = req.status_code
    if req.status_code == 200:
        return req.json()
    else:
        bam_error(req.text)

def get_configuration_setting(id, name):
    URL = BaseURL + 'getConfigurationSetting'
    params = {'configurationId': id, 'settingName': name}
    req = requests.get(URL, headers=AuthHeader, params=params)
    return req.json()


'''

Higher Level Functions

'''

# Takes a property list as a dictionary e.g.
# {'ttl': '86400', 'absoluteName': 'fwsm-tabu.bkup.utoronto.ca', 'addresses': '128.100.96.158', 'reverseRecord': 'true'}
# and returns it as a string equivalent:
#   ttl=86400|absoluteName=fwsm-tabu.bkup.utoronto.ca|addresses=128.100.96.158|reverseRecord=true|

def dict2props(d):
    props = []
    for k,v in d.items():
        props.append('='.join([k,v]))
    return '|'.join(props) + '|'


# Takes a property list as a string e.g.
#   ttl=86400|absoluteName=fwsm-tabu.bkup.utoronto.ca|addresses=128.100.96.158|reverseRecord=true|
# and returns it as a dictionary equivalent:
#   {'ttl': '86400', 'absoluteName': 'fwsm-tabu.bkup.utoronto.ca', 'addresses': '128.100.96.158', 'reverseRecord': 'true'}

def props2dict(str):
    dd = {}
    ll = str.split('|')
    for i in ll[0:-1]:
        kv = i.split('=')
        dd[kv[0]] = kv[1]
    return dd


def get_token():
    URL = BaseURL + 'login'

    if Debug:
        Creds = creds_rw
    else:
        uname = input('Username: ')
        pw = getpass.getpass()
        Creds = {'username': uname, 'password': pw}

    req = requests.get(URL, params=Creds)
    return req.json().split()[3]


def bam_init():
    global AuthHeader, ConfigId, ViewId

    tok = get_token()
    AuthHeader = {
      'Authorization': 'BAMAuthToken: ' + tok,
      'Content-Type': 'application/json'
    }
    if Debug:
        print('Authorization Header:', AuthHeader)
        print()

    val = get_system_info()
    if Debug:
        vals = val.split('|')
        for val in vals:
            print(val)
        print()

    ConfigId = get_config_id(ConfigName)
    ViewId = get_view_id(ViewName)


def bam_logout():
    URL = BaseURL + 'logout'
    req = requests.get(URL, headers=AuthHeader)
    sys.exit()


def bam_error(err_str):
    print('BAM error:', err_str)
    sys.exit()

def get_ip4_address(ip, tok):
    URL = BaseURL + 'getIP4Address'


# Deletes all data and RRs in the Zone tree including other Zones

def delete_zone(fqdn):
    zone_id = get_zone_id(fqdn)
    if zone_id:
        val = delete(zone_id)
        return val


#
# assumes the two global variable have been set: ConfigName, ViewName
#


def get_config_id(config_name):
    config_info = get_entity_by_name(RootId, config_name, 'Configuration')
    if Debug:
    	pprint(config_info)
    return config_info['id']


def get_view_id(view_name):
    if ConfigId > 0:
        view_info = get_entity_by_name(ConfigId, view_name, 'View')
        if Debug:
            pprint(view_info)
        return view_info['id']
    else:
        bam_error('Error: The parent (Configuration) Id must be set before setting the View Id')

        
#
# given andy.bozo.cathy.dan.ca it returns bozo.cathy.dan.ca
#

def parent_name(fqdn):
    return fqdn.split('.',1)[1]

#
# Get the information of an Entity (Id and parentId) given a FQDN or a CIDR block
#

def get_info_by_name(fqdn):
    id = ViewId
    names = fqdn.split('.')
    lg = len(names)
    for name in names[::-1]:
        ent = get_entity_by_name(id, name, 'Entity')
        pid = id
        id = ent['id']
    ent['pid'] = pid
    return ent


def get_id_by_name(fqdn):
    ent = get_info_by_name(fqdn)
    return ent['id']


def get_pid_by_name(fqdn):
    info = get_info_by_name(fqdn)
    return info['pid']


def get_pid_by_id(id):
    ent = get_parent(id)
    return ent['id']


def get_info_by_id(id):
    ent = get_entity_by_id(id)
    pid = get_pid_by_id(id)
    ent['pid'] = pid
    return ent


#
# return the parent ID of an Object based on its name
#


def get_pid_by_name(fqdn):
    info = get_info_by_name(fqdn)
    return info['pid']


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
    info = get_info_by_name(fqdn)
    if info['type'] == 'Zone':
        return info['id']
    else:
        print(fqdn, 'is not a zone')

#
# is_zone takes a name/fqdn as input and returns: False
# if it is not a zone, otherwise the object_Id of the zone
#

def is_zone(fqdn):
    ent = get_info_by_name(fqdn)
    if ent['type'] == 'Zone':
        return ent['id']
    else:
        return False

#
# Add a zone using the generic add_generic call rather than
# the specific add_zone()one
#
    
def add_zone_generic(fqdn):
    dot = '.'
    n = fqdn.split(dot)
    nm = n[0]
    subzone = dot.join(n[1:])
    par_id = get_id_by_name(subzone)
    props = 'deployable=true|'
    props += 'absoluteName=' + fqdn + '|'
    ent = {
        'name': nm,
        'type': 'Zone',
        'properties': props
    }
    val = add_entity(par_id, ent)
    return val


def add_PTR_rr(fqdn, ipaddr, ttl=86400):
    macaddr = ''
    hostinfo = ''
    action = 'MAKE_STATIC'
    props = 'ptrs=' + str(ViewId) + ',' + fqdn
    val = assign_IP4_Address(ConfigId, ipaddr, macaddr, hostinfo, action, props)
    return val

def get_external_hosts():
    exhosts = []
    ents = get_entities(ViewId, 'ExternalHostRecord', 0, 250)
    for ent in ents:
        exhosts.append(ent['name'])
    return exhosts

def add_external_host(exhost):
    exhosts = get_external_hosts()
    if exhost not in exhosts:
        val = add_ExternalHost_Record(ViewId, exhost, 'comments=Ext. Host|')
        print(val)

#
# fqdn is at the zone level or is a new RR below a zone
# add RR by using the lower level add_entity call
#

def add_entity_rr(data):
    if Debug:
        print()
        print('input data:', data)

    fqdn = data['fqdn']
    rr_type = data['rr_type']
    ttl = data['ttl']
    value = data['value']

#
# use BAM higher level functions rather than lower level add_entity
#

    if rr_type == 'A':
        ent_id = add_host_record(fqdn, value, ttl)
        if Debug:
            ent = get_entity_by_id(ent_id)
            print('add_host_record:', ent)
        return ent_id
    elif rr_type == 'TXT':
        ent_id = add_TXT_Record(fqdn, value, ttl)
        if Debug:
            ent = get_entity_by_id(ent_id)
            print('add_TXT_record:', ent)
        return ent_id
    elif rr_type == 'MX':
        (priority, mx_host) = value.split(' ')
        add_external_host(mx_host)
        ent_id = add_MX_Record(fqdn, priority, mx_host, ttl)
        if Debug:
            ent = get_entity_by_id(ent_id)
            print('add_MX_record:', ent)
        return ent_id
    elif rr_type == 'CNAME':
        ent = get_info_by_name(fqdn)
        ent_id = ent['id']
        if is_zone(fqdn):
            print('CNAME records are not allowed at the top of Zone')
            print('Existing Zone info:', ent)
            return ent['id']
        elif ent_id:
            cname_ent = get_entity_by_id(ent_id)
            print('Multiple CNAME records are forbidden')
            print('Existing CNAME record:', cname_ent)
            return cname_ent['id']
        else:
            add_external_host(value)
            ent_id = add_Alias_Record(fqdn, value, ttl)
            if Debug:
                ent = get_entity_by_id(ent_id)
                print('add_Alias_record:', ent)
            return ent_id

    ent_obj_type = RRTypeMap[rr_type]['obj_type']
    ent_key = RRTypeMap[rr_type]['prop_key']

    d = {
        'absoluteName': fqdn,
        'ttl': ttl,
        'comments': 'Nothing yet',
    }

    ent = get_info_by_name(fqdn)
    if Debug:
        print('initial get_info entity:', ent)
    obj_id = ent['id']
    obj_pid = ent['pid']
    obj_type = ent['type']
    obj_name = fqdn.split('.')[0]

    if rr_type == 'A':
        d['reverseRecord'] = 'true'
    elif rr_type == 'MX':
        (priority, value) = value.split(' ')
        add_external_host(value)
        d['priority'] = priority
    elif rr_type == 'CNAME':
        if obj_type == 'Zone':
            zone_ent = get_entity_by_id(ent['id'])
            print('CNAME records are not allowed at the top of Zone')
            print('Existing Zone info:', zone_ent)
            return
        if obj_id:
            cname_ent = get_entity_by_id(ent['id'])
            print('Multiple CNAME records are forbidden')
            print('Existing CNAME record:', cname_ent)
            return

    if obj_type == 'Zone':
        obj_pid = ent['id']
        obj_name = ''

    if ent_obj_type == 'GenericRecord':
        d['type'] = rr_type

    d[ent_key] = value

    temp_ent = {
        'name': obj_name,
        'type': ent_obj_type,
        'properties': dict2props(d),
    }

    if rr_type == 'PTR':
        obj_id = add_PTR_rr(fqdn, value)
        if Debug:
            print(obj_id, get_entity_by_id(obj_id))
    else:
        if Debug:
            print('ParentID', obj_pid, 'Temp Ent', temp_ent)
        new_obj_id = add_entity(obj_pid, temp_ent)
        if Debug:
            print('New ObjectID', new_obj_id)
