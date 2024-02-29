#!/usr/bin/env python3

import os
import sys
import json
import csv
import requests

from pprint import pprint
from dotenv import load_dotenv


'''
Library to use the BAM v2 API, which commenced with BAM v9.5
See:

    https://proteus-dev.its.utoronto.ca/api/docs/?context=AddressManager
    
    The BlueCat Address Manager 9.5 RESTful v2 API is a new RESTful
    API for Address Manager that presents Address Manager objects
    as resources. Each resource has a unique endpoint, and related
    resources are grouped in collections. To fetch an individual
    resource, a GET request is sent to the resource's endpoint. To
    fetch all resources in a collection, a GET request is sent to
    the collection's endpoint.
    
    The RESTful v2 API is hypermedia driven and uses the HAL format
    for representing links. When navigating through the API, you
    can use those links to navigate to related resources or child
    resources of the requested endpoint. The API supports the
    following media types for most endpoints: application/hal+json,
    application/json, and text/csv. For authentication, the API
    supports both Basic and Bearer HTTP authentication schemes.

    To get started, create a session and receive credentials for Basic authentication by sending a POST request to the /sessions endpoint, with a message body containing the user's credentials:

    {"username":"apiuser", "password":"apipass"}

    The response will contain an apiToken field that can be entered
    with the username in the Swagger UI Authorize dialog. The response
    will also contain a basicAuthenticationCredentials field containing
    a base64 encoding of the requester's username and API token delimited
    by a colon. This string can be injected directly into request
    Authorization headers in the following format:

    Authorization: Basic YXBpOlQ0OExOT3VIRGhDcnVBNEo1bGFES3JuS3hTZC9QK3pjczZXTzBJMDY=

'''

load_dotenv("/home/russ/.bamrc")
Ca_bundle = '/etc/ssl/Sectigo-AAA-chain.pem'

Debug = False
Debug = True

Dot = '.'

Conf = 'Test'
View = 'Azure'
CIDRBlock = '10.0.0.0/8'
ConfID = 0
ViewID = 0
ExHostZoneID = 0
BlockID = 0

TTL = 3600

URL = os.environ.get('BAM_APIv2_URL')
uname = os.environ.get('BAM_DEV_USER')
pw = os.environ.get('BAM_DEV_PW')
Header = {
        'Content-Type': 'application/json',
}

# Retrieve the configurations. Request the data as per BAM's default content type.

'''
Response:

{
'_links': {'collection': {'href': '/api/v2/sessions'}, 'self': {'href': '/api/v2/sessions/548'}},
'apiToken': '7ghHx/YgLcWwP+mhU5hZ2oLeRc205zrqW6wouXQf',
'apiTokenExpirationDateTime': '2024-02-21T09:38:47Z',
'authenticator': {
   '_links': {'self': {'href': '/api/v2/authenticators/2'}},
   'id': 2,
   'name': 'proteusAuthenticator',
   'type': 'AddressManagerAuthenticator'
   },
'basicAuthenticationCredentials': 'c3V0aGVybDQ6N2doSHgvWWdMY1d3UCttaFU1aFoyb0xlUmMyMDV6cnFXNndvdVhRZg==',
'id': 548,
'loginDateTime': '2024-02-21T09:18:47Z',
'logoutDateTime': None,
'readOnly': False,
'remoteAddress': '128.100.103.17',
'response': None,
'state': 'LOGGED_IN',
'type': 'UserSession',
'user': {
    '_links': {'self': {'href': '/api/v2/users/108726'}},
    'id': 108726,
    'name': 'sutherl4',
    'type': 'User'
    }
}

'''

def basic_auth(nm, pw):
    global ConfID, ViewID, ExHostZoneID, Header, Auth_header, BlockID

    payload = {
        'username': nm,
        'password': pw,
    }
    resp = req('POST', url='/sessions', json=payload)
    data = resp.json()
    if Debug:
        pprint(data)
    tok = data['basicAuthenticationCredentials']

    Header['Authorization'] = f'Basic {tok}'
    Auth_header = Header
    ConfID = get_conf_id(Conf)
    ViewID = get_view_id(View, ConfID)
    ExHostZoneID = get_external_hosts_zone_id(ViewID)
    data = get_ipv4_blocks(ConfID)
    if len(data):
        BlockID = data[0]['id']
    else:
        BlockID = create_block(ConfID, CIDRBlock)

    if Debug:
        print(BlockID)

    return tok

'''
Get a list of all Configurations
To get a subset of fields: params = {'fields': 'id,name,type'}

Return from GET: /configurations

{'count': 2,
 'data': 
    [
        {'_links': {'accessControlLists': {'href': '/api/v2/configurations/100905/accessControlLists'},
                      'accessRights': {'href': '/api/v2/configurations/100905/accessRights'},
                      'blocks': {'href': '/api/v2/configurations/100905/blocks'},
                      'clientClasses': {'href': '/api/v2/configurations/100905/clientClasses'},
                      'clientIdentifiers': {'href': '/api/v2/configurations/100905/clientIdentifiers'},
                      'collection': {'href': '/api/v2/configurations'},
                      'deploymentOptionDefinitions': {'href': '/api/v2/configurations/100905/deploymentOptionDefinitions'},
                      'deploymentOptions': {'href': '/api/v2/configurations/100905/deploymentOptions'},
                      'devices': {'href': '/api/v2/configurations/100905/devices'},
                      'macAddresses': {'href': '/api/v2/configurations/100905/macAddresses'},
                      'macPools': {'href': '/api/v2/configurations/100905/macPools'},
                      'merges': {'href': '/api/v2/configurations/100905/merges'},
                      'realms': {'href': '/api/v2/configurations/100905/realms'},
                      'reconciliationPolicies': {'href': '/api/v2/configurations/100905/reconciliationPolicies'},
                      'responsePolicies': {'href': '/api/v2/configurations/100905/responsePolicies'},
                      'self': {'href': '/api/v2/configurations/100905'},
                      'serverGroups': {'href': '/api/v2/configurations/100905/serverGroups'},
                      'servers': {'href': '/api/v2/configurations/100905/servers'},
                      'signingKeys': {'href': '/api/v2/configurations/100905/signingKeys'},
                      'splits': {'href': '/api/v2/configurations/100905/splits'},
                      'tags': {'href': '/api/v2/configurations/100905/tags'},
                      'templates': {'href': '/api/v2/configurations/100905/templates'},
                      'tftpGroups': {'href': '/api/v2/configurations/100905/tftpGroups'},
                      'transactions': {'href': '/api/v2/configurations/100905/transactions'},
                      'up': {'href': '/api/v2/1'},
                      'views': {'href': '/api/v2/configurations/100905/views'},
                      'workflowRequests': {'href': '/api/v2/configurations/100905/workflowRequests'},
                      'zoneGroups': {'href': '/api/v2/configurations/100905/zoneGroups'}},
           'blockUsageCalculation': 'ADDRESS_ALLOCATION',
           'checkIntegrityValidation': 'FULL',
           'checkMxCnameValidation': 'WARN',
           'checkMxValidation': 'WARN',
           'checkNamesValidation': 'WARN',
           'checkNsValidation': 'WARN',
           'checkSrvCnameValidation': 'WARN',
           'checkWildcardValidation': 'WARN',
           'configurationGroup': None,
           'description': None,
           'dhcpConfigurationValidationEnabled': False,
           'dnsConfigurationValidationEnabled': False,
           'dnsFeedEnabled': False,
           'dnsFeedLicense': None,
           'dnsOptionInheritanceEnabled': True,
           'dnsZoneValidationEnabled': False,
           'id': 100905,
           'keyAutoRegenerationEnabled': False,
           'name': 'Production',
           'serverMonitoringEnabled': False,
           'sharedNetworkTagGroup': None,
           'snmp': None,
           'type': 'Configuration',
           'userDefinedFields': None},
          {'_links': {'accessControlLists': {'href': '/api/v2/configurations/163787/accessControlLists'},
                      'accessRights': {'href': '/api/v2/configurations/163787/accessRights'},
                      'blocks': {'href': '/api/v2/configurations/163787/blocks'},
                      ....
                      }
          }
      ]
}

As is returns a list of configurations
'''

# params = {'fields': 'id,name,type'}

def get_confs(params={}):
    resp = req('GET', '/configurations')
    data = resp.json()
    return data['data']

'''
Data dictionary returned for an individual Configuration:

{'_links': {'accessControlLists': {'href': '/api/v2/configurations/163787/accessControlLists'},
            'accessRights': {'href': '/api/v2/configurations/163787/accessRights'},
            'blocks': {'href': '/api/v2/configurations/163787/blocks'},
            'clientClasses': {'href': '/api/v2/configurations/163787/clientClasses'},
            'clientIdentifiers': {'href': '/api/v2/configurations/163787/clientIdentifiers'},
            'collection': {'href': '/api/v2/configurations'},
            'deploymentOptionDefinitions': {'href': '/api/v2/configurations/163787/deploymentOptionDefinitions'},
            'deploymentOptions': {'href': '/api/v2/configurations/163787/deploymentOptions'},
            'devices': {'href': '/api/v2/configurations/163787/devices'},
            'macAddresses': {'href': '/api/v2/configurations/163787/macAddresses'},
            'macPools': {'href': '/api/v2/configurations/163787/macPools'},
            'merges': {'href': '/api/v2/configurations/163787/merges'},
            'realms': {'href': '/api/v2/configurations/163787/realms'},
            'reconciliationPolicies': {'href': '/api/v2/configurations/163787/reconciliationPolicies'},
            'responsePolicies': {'href': '/api/v2/configurations/163787/responsePolicies'},
            'self': {'href': '/api/v2/configurations/163787'},
            'serverGroups': {'href': '/api/v2/configurations/163787/serverGroups'},
            'servers': {'href': '/api/v2/configurations/163787/servers'},
            'signingKeys': {'href': '/api/v2/configurations/163787/signingKeys'},
            'splits': {'href': '/api/v2/configurations/163787/splits'},
            'tags': {'href': '/api/v2/configurations/163787/tags'},
            'templates': {'href': '/api/v2/configurations/163787/templates'},
            'tftpGroups': {'href': '/api/v2/configurations/163787/tftpGroups'},
            'transactions': {'href': '/api/v2/configurations/163787/transactions'},
            'up': {'href': '/api/v2/1'},
            'views': {'href': '/api/v2/configurations/163787/views'},
            'workflowRequests': {'href': '/api/v2/configurations/163787/workflowRequests'},
            'zoneGroups': {'href': '/api/v2/configurations/163787/zoneGroups'}},
 'blockUsageCalculation': 'ADDRESS_ALLOCATION',
 'checkIntegrityValidation': 'FULL',
 'checkMxCnameValidation': 'WARN',
 'checkMxValidation': 'WARN',
 'checkNamesValidation': 'WARN',
 'checkNsValidation': 'WARN',
 'checkSrvCnameValidation': 'WARN',
 'checkWildcardValidation': 'WARN',
 'configurationGroup': 'Testing',
 'description': 'For Testing as our Production instance has',
 'dhcpConfigurationValidationEnabled': False,
 'dnsConfigurationValidationEnabled': False,
 'dnsFeedEnabled': False,
 'dnsFeedLicense': None,
 'dnsOptionInheritanceEnabled': True,
 'dnsZoneValidationEnabled': False,
 'id': 163787,
 'keyAutoRegenerationEnabled': False,
 'name': 'Test',
 'serverMonitoringEnabled': False,
 'sharedNetworkTagGroup': None,
 'snmp': None,
 'type': 'Configuration',
 'userDefinedFields': None}

 '''

def get_conf(cid, params={}):
    resp = req('GET', f'/configurations/{cid}', params=params)
    data = resp.json()
    return data

'''
get_conf_views: Retrieves all Views related to a given configuration
Returns a dictionary as follows:
Conf ID: 100905 Views
data is the list of Views

{'count': 2,
 'data': [
     {'_links': {'accessRights': {'href': '/api/v2/views/100917/accessRights'},
                      'collection': {'href': '/api/v2/configurations/100905/views'},
                      'deploymentOptions': {'href': '/api/v2/views/100917/deploymentOptions'},
                      'deploymentRoles': {'href': '/api/v2/views/100917/deploymentRoles'},
                      'namingPolicies': {'href': '/api/v2/views/100917/namingPolicies'},
                      'restrictedRanges': {'href': '/api/v2/views/100917/restrictedRanges'},
                      'self': {'href': '/api/v2/views/100917'},
                      'tags': {'href': '/api/v2/views/100917/tags'},
                      'templates': {'href': '/api/v2/views/100917/templates'},
                      'transactions': {'href': '/api/v2/views/100917/transactions'},
                      'up': {'href': '/api/v2/configurations/100905'},
                      'userDefinedLinks': {'href': '/api/v2/views/100917/userDefinedLinks'},
                      'zones': {'href': '/api/v2/views/100917/zones'}},
           'configuration': {'_links': {'self': {'href': '/api/v2/configurations/100905'}},
                             'id': 100905,
                             'name': 'Production',
                             'type': 'Configuration'},
           'deviceRegistrationEnabled': False,
           'deviceRegistrationPortalAddress': None,
           'id': 100917,
           'name': 'Public',
           'type': 'View',
           'userDefinedFields': None},
          {'_links': {'accessRights': {'href': '/api/v2/views/163784/accessRights'},
                      'collection': {'href': '/api/v2/configurations/100905/views'},
                      'deploymentOptions': {'href': '/api/v2/views/163784/deploymentOptions'},
                      'deploymentRoles': {'href': '/api/v2/views/163784/deploymentRoles'},
                      'namingPolicies': {'href': '/api/v2/views/163784/namingPolicies'},
                      'restrictedRanges': {'href': '/api/v2/views/163784/restrictedRanges'},
                      'self': {'href': '/api/v2/views/163784'},
                      'tags': {'href': '/api/v2/views/163784/tags'},
                      'templates': {'href': '/api/v2/views/163784/templates'},
                      'transactions': {'href': '/api/v2/views/163784/transactions'},
                      'up': {'href': '/api/v2/configurations/100905'},
                      'userDefinedLinks': {'href': '/api/v2/views/163784/userDefinedLinks'},
                      'zones': {'href': '/api/v2/views/163784/zones'}},
           'configuration': {'_links': {'self': {'href': '/api/v2/configurations/100905'}},
                             'id': 100905,
                             'name': 'Production',
                             'type': 'Configuration'},
           'deviceRegistrationEnabled': False,
           'deviceRegistrationPortalAddress': None,
           'id': 163784,
           'name': 'Azure',
           'type': 'View',
           'userDefinedFields': None}
           ]
}

'''

def get_conf_views(cid, params={}):
    resp = req('GET', f'/configurations/{cid}/views', params=params)
    data = resp.json()
    return data['data']

'''

{'count': 3,
 'data': [{'_links': {'accessRights': {'href': '/api/v2/views/100917/accessRights'},
                      'collection': {'href': '/api/v2/configurations/100905/views'},
                      'deploymentOptions': {'href': '/api/v2/views/100917/deploymentOptions'},
                      'deploymentRoles': {'href': '/api/v2/views/100917/deploymentRoles'},
                      'namingPolicies': {'href': '/api/v2/views/100917/namingPolicies'},
                      'restrictedRanges': {'href': '/api/v2/views/100917/restrictedRanges'},
                      'self': {'href': '/api/v2/views/100917'},
                      'tags': {'href': '/api/v2/views/100917/tags'},
                      'templates': {'href': '/api/v2/views/100917/templates'},
                      'transactions': {'href': '/api/v2/views/100917/transactions'},
                      'up': {'href': '/api/v2/configurations/100905'},
                      'userDefinedLinks': {'href': '/api/v2/views/100917/userDefinedLinks'},
                      'zones': {'href': '/api/v2/views/100917/zones'}},
           'configuration': {'_links': {'self': {'href': '/api/v2/configurations/100905'}},
                             'id': 100905,
                             'name': 'Production',
                             'type': 'Configuration'},
           'deviceRegistrationEnabled': False,
           'deviceRegistrationPortalAddress': None,
           'id': 100917,
           'name': 'Public',
           'type': 'View',
           'userDefinedFields': None},
          {'_links': {'accessRights': {'href': '/api/v2/views/163784/accessRights'},
                      'collection': {'href': '/api/v2/configurations/100905/views'},
                      'deploymentOptions': {'href': '/api/v2/views/163784/deploymentOptions'},
                      'deploymentRoles': {'href': '/api/v2/views/163784/deploymentRoles'},
                      'namingPolicies': {'href': '/api/v2/views/163784/namingPolicies'},
                      'restrictedRanges': {'href': '/api/v2/views/163784/restrictedRanges'},
                      'self': {'href': '/api/v2/views/163784'},
                      'tags': {'href': '/api/v2/views/163784/tags'},
                      'templates': {'href': '/api/v2/views/163784/templates'},
                      'transactions': {'href': '/api/v2/views/163784/transactions'},
                      'up': {'href': '/api/v2/configurations/100905'},
                      'userDefinedLinks': {'href': '/api/v2/views/163784/userDefinedLinks'},
                      'zones': {'href': '/api/v2/views/163784/zones'}},
           'configuration': {'_links': {'self': {'href': '/api/v2/configurations/100905'}},
                             'id': 100905,
                             'name': 'Production',
                             'type': 'Configuration'},
           'deviceRegistrationEnabled': False,
           'deviceRegistrationPortalAddress': None,
           'id': 163784,
           'name': 'Azure',
           'type': 'View',
           'userDefinedFields': None},
          {'_links': {'accessRights': {'href': '/api/v2/views/163799/accessRights'},
                      'collection': {'href': '/api/v2/configurations/163787/views'},
                      'deploymentOptions': {'href': '/api/v2/views/163799/deploymentOptions'},
                      'deploymentRoles': {'href': '/api/v2/views/163799/deploymentRoles'},
                      'namingPolicies': {'href': '/api/v2/views/163799/namingPolicies'},
                      'restrictedRanges': {'href': '/api/v2/views/163799/restrictedRanges'},
                      'self': {'href': '/api/v2/views/163799'},
                      'tags': {'href': '/api/v2/views/163799/tags'},
                      'templates': {'href': '/api/v2/views/163799/templates'},
                      'transactions': {'href': '/api/v2/views/163799/transactions'},
                      'up': {'href': '/api/v2/configurations/163787'},
                      'userDefinedLinks': {'href': '/api/v2/views/163799/userDefinedLinks'},
                      'zones': {'href': '/api/v2/views/163799/zones'}},
           'configuration': {'_links': {'self': {'href': '/api/v2/configurations/163787'}},
                             'id': 163787,
                             'name': 'Test',
                             'type': 'Configuration'},
           'deviceRegistrationEnabled': False,
           'deviceRegistrationPortalAddress': None,
           'id': 163799,
           'name': 'Azure',
           'type': 'View',
           'userDefinedFields': None}]}

With params: fields -> 'configuration,id,name,type'

{
'count': 3,
 'data': [{'configuration': {'_links': {'self': {'href': '/api/v2/configurations/100905'}},
                             'id': 100905,
                             'name': 'Production',
                             'type': 'Configuration'},
           'id': 100917,
           'name': 'Public',
           'type': 'View'},
          {'configuration': {'_links': {'self': {'href': '/api/v2/configurations/100905'}},
                             'id': 100905,
                             'name': 'Production',
                             'type': 'Configuration'},
           'id': 163784,
           'name': 'Azure',
           'type': 'View'},
          {'configuration': {'_links': {'self': {'href': '/api/v2/configurations/163787'}},
                             'id': 163787,
                             'name': 'Test',
                             'type': 'Configuration'},
           'id': 163799,
           'name': 'Azure',
           'type': 'View'}]
}

'''

#    params = {'fields': 'id,configuration,name,type'}

def get_views(params={}):
    resp = req('GET', '/views', params=params)
    data = resp.json()
    return data['data']


'''
get_view output

Retrieve a Single View

Returns a dictionary of an individual View:

E.g. View: 100917
{
'id': 100917,
'type': 'View',
'name': 'Public',
'configuration': {
    'id': 100905,
    'type': 'Configuration',
    'name': 'Production',
    '_links': {'self': {'href': '/api/v2/configurations/100905'}}
    },
'deviceRegistrationEnabled': False,
'deviceRegistrationPortalAddress': None,
'userDefinedFields': None,
'_links': {
    'self': {'href': '/api/v2/views/100917'},
    'collection': {'href': '/api/v2/configurations/100905/views'},
    'up': {'href': '/api/v2/configurations/100905'},
    'deploymentOptions': {'href': '/api/v2/views/100917/deploymentOptions'},
    'deploymentRoles': {'href': '/api/v2/views/100917/deploymentRoles'},
    'restrictedRanges': {'href': '/api/v2/views/100917/restrictedRanges'}, 
    'namingPolicies': {'href': '/api/v2/views/100917/namingPolicies'},
    'templates': {'href': '/api/v2/views/100917/templates'},
    'zones': {'href': '/api/v2/views/100917/zones'},
    'tags': {'href': '/api/v2/views/100917/tags'},
    'accessRights': {'href': '/api/v2/views/100917/accessRights'},
    'transactions': {'href': '/api/v2/views/100917/transactions'},
    'userDefinedLinks': {'href': '/api/v2/views/100917/userDefinedLinks'}
    }
}

'''

def get_view(vid, params={}):
    resp = req('GET', f'/views/{vid}', params=params)
    data = resp.json()
    return data

'''
get all the Network Blocks for a given Collection/Configuration

long data form:

[
{'_inheritedFields': [],
  '_links': {'accessRights': {'href': '/api/v2/blocks/163788/accessRights'},
             'blocks': {'href': '/api/v2/blocks/163788/blocks'},
             'collection': {'href': '/api/v2/configurations/163787/blocks'},
             'deploymentOptions': {'href': '/api/v2/blocks/163788/deploymentOptions'},
             'deploymentRoles': {'href': '/api/v2/blocks/163788/deploymentRoles'},
             'leases': {'href': '/api/v2/blocks/163788/leases'},
             'moves': {'href': '/api/v2/blocks/163788/moves'},
             'networks': {'href': '/api/v2/blocks/163788/networks'},
             'reconciliationPolicies': {'href': '/api/v2/blocks/163788/reconciliationPolicies'},
             'self': {'href': '/api/v2/blocks/163788'},
             'tags': {'href': '/api/v2/blocks/163788/tags'},
             'transactions': {'href': '/api/v2/blocks/163788/transactions'},
             'up': {'href': '/api/v2/configurations/163787'},
             'userDefinedLinks': {'href': '/api/v2/blocks/163788/userDefinedLinks'}},
  'configuration': {'_links': {'self': {'href': '/api/v2/configurations/163787'}},
                    'id': 163787,
                    'name': 'Test',
                    'type': 'Configuration'},
  'id': 163788,
  'location': None,
  'name': 'Global Unicast Address Space',
  'range': '2000::/3',
  'type': 'IPv6Block',
  'userDefinedFields': None},

 {'_inheritedFields': [],
  '_links': {'accessRights': {'href': '/api/v2/blocks/163789/accessRights'},
             'blocks': {'href': '/api/v2/blocks/163789/blocks'},
             'collection': {'href': '/api/v2/configurations/163787/blocks'},
             'deploymentOptions': {'href': '/api/v2/blocks/163789/deploymentOptions'},
             'deploymentRoles': {'href': '/api/v2/blocks/163789/deploymentRoles'},
             'leases': {'href': '/api/v2/blocks/163789/leases'},
             'moves': {'href': '/api/v2/blocks/163789/moves'},
             'networks': {'href': '/api/v2/blocks/163789/networks'},
             'reconciliationPolicies': {'href': '/api/v2/blocks/163789/reconciliationPolicies'},
             'self': {'href': '/api/v2/blocks/163789'},
             'tags': {'href': '/api/v2/blocks/163789/tags'},
             'transactions': {'href': '/api/v2/blocks/163789/transactions'},
             'up': {'href': '/api/v2/configurations/163787'},
             'userDefinedLinks': {'href': '/api/v2/blocks/163789/userDefinedLinks'}},
  'configuration': {'_links': {'self': {'href': '/api/v2/configurations/163787'}},
                    'id': 163787,
                    'name': 'Test',
                    'type': 'Configuration'},
  'id': 163789,
  'location': None,
  'name': 'Unique Local Address Space',
  'range': 'fc00::/6',
  'type': 'IPv6Block',
  'userDefinedFields': None},

 {'_inheritedFields': ['lowWaterMark', 'highWaterMark'],
  '_links': {'accessRights': {'href': '/api/v2/blocks/163879/accessRights'},
             'blocks': {'href': '/api/v2/blocks/163879/blocks'},
             'collection': {'href': '/api/v2/configurations/163787/blocks'},
             'defaultZones': {'href': '/api/v2/blocks/163879/defaultZones'},
             'deploymentOptions': {'href': '/api/v2/blocks/163879/deploymentOptions'},
             'deploymentRoles': {'href': '/api/v2/blocks/163879/deploymentRoles'},
             'leases': {'href': '/api/v2/blocks/163879/leases'},
             'merges': {'href': '/api/v2/blocks/163879/merges'},
             'moves': {'href': '/api/v2/blocks/163879/moves'},
             'networks': {'href': '/api/v2/blocks/163879/networks'},
             'reconciliationPolicies': {'href': '/api/v2/blocks/163879/reconciliationPolicies'},
             'restrictedZones': {'href': '/api/v2/blocks/163879/restrictedZones'},
             'self': {'href': '/api/v2/blocks/163879'},
             'signingKeys': {'href': '/api/v2/blocks/163879/signingKeys'},
             'splits': {'href': '/api/v2/blocks/163879/splits'},
             'tags': {'href': '/api/v2/blocks/163879/tags'},
             'transactions': {'href': '/api/v2/blocks/163879/transactions'},
             'up': {'href': '/api/v2/configurations/163787'},
             'userDefinedLinks': {'href': '/api/v2/blocks/163879/userDefinedLinks'}},
  'configuration': {'_links': {'self': {'href': '/api/v2/configurations/163787'}},
                    'id': 163787,
                    'name': 'Test',
                    'type': 'Configuration'},
  'defaultView': {'_links': {'self': {'href': '/api/v2/views/163799'}},
                  'id': 163799,
                  'name': 'Azure',
                  'type': 'View'},
  'defaultZonesInherited': True,
  'duplicateHostnamesAllowed': True,
  'highWaterMark': 100,
  'id': 163879,
  'location': None,
  'lowWaterMark': 0,
  'name': 'Private_10',
  'pingBeforeAssignEnabled': False,
  'range': '10.0.0.0/8',
  'restrictedZonesInherited': True,
  'reverseZoneSigned': False,
  'reverseZoneSigningPolicy': None,
  'template': None,
  'type': 'IPv4Block',
  'usagePercentage': {'assigned': 0, 'unassigned': 100},
  'userDefinedFields': None}]

'''

def get_collection_blocks(cid, params={}):
    resp = req('GET', f'/configurations/{cid}/blocks', params=params)
    data = resp.json()
    return data['data']

'''
Create a CIDR Block for a given Configuration and return its ID
full data:
{
    'id': 163886,
    'type': 'IPv4Block',
    'name': None,
    'configuration': {'id': 163787, 'type': 'Configuration', 'name': 'Test', '_links': {'self': {'href': '/api/v2/configurations/163787'}}},
    'range': '10.0.0.0/8',
    'template': None,
    'location': None,
    'duplicateHostnamesAllowed': True,
    'pingBeforeAssignEnabled': False,
    'defaultView': None,
    'defaultZonesInherited': True,
    'restrictedZonesInherited': True,
    'lowWaterMark': 0, 
    'highWaterMark': 100,
    'usagePercentage': {'assigned': 0, 'unassigned': 100},
    'reverseZoneSigned': False,
    'reverseZoneSigningPolicy': None,
    'userDefinedFields': None, 
    '_inheritedFields': ['lowWaterMark', 'highWaterMark'],
    '_links': {
        'self': {'href': '/api/v2/blocks/163886'},
        'collection': {
        'href': '/api/v2/configurations/163787/blocks'},
        'up': {'href': '/api/v2/configurations/163787'},
        'blocks': {'href': '/api/v2/blocks/163886/blocks'},
        'networks': {'href': '/api/v2/blocks/163886/networks'},
        'deploymentOptions': {'href': '/api/v2/blocks/163886/deploymentOptions'},
        'deploymentRoles': {'href': '/api/v2/blocks/163886/deploymentRoles'},
        'leases': {'href': '/api/v2/blocks/163886/leases'},
        'reconciliationPolicies': {'href': '/api/v2/blocks/163886/reconciliationPolicies'},
        'restrictedZones': {'href': '/api/v2/blocks/163886/restrictedZones'},
        'signingKeys': {'href': '/api/v2/blocks/163886/signingKeys'},
        'defaultZones': {'href': '/api/v2/blocks/163886/defaultZones'},
        'merges': {'href': '/api/v2/blocks/163886/merges'},
        'moves': {'href': '/api/v2/blocks/163886/moves'},
        'splits': {'href': '/api/v2/blocks/163886/splits'},
        'tags': {'href': '/api/v2/blocks/163886/tags'},
        'accessRights': {'href': '/api/v2/blocks/163886/accessRights'},
        'transactions': {'href': '/api/v2/blocks/163886/transactions'},
        'userDefinedLinks': {'href': '/api/v2/blocks/163886/userDefinedLinks'}
        }
}
'''

def create_block(cid, cidr):
    payload = {
            'type': 'IPv4Block',
            'range': cidr,
    }
    resp = req(
            'POST',
            f'/configurations/{cid}/blocks',
            json=payload,
            )
    data = resp.json()
    return data['id']

'''
Get the main Block IDs associated with a Configuration

'''

def get_ipv4_blocks(cid):
    params = { 'filter': "type:eq('IPv4Block')" }
    return get_collection_blocks(cid, params=params)

def get_ipv4_block_id(cid):
    params = {
            'fields': 'id',
            'filter': "type:eq('IPv4Block')",
            }
    data = get_collection_blocks(cid, params=params)
    if len(data):
        return data[0]['id']
    else:
        return False

'''
delete Network Block by its ID
'''

def delete_block(blkid):
    resp = req('DELETE', f'/blocks/{blkid}')
    data = resp.json()
    return data

def get_collection_networks(cid, params={}):
    resp = req('GET', f'/blocks/{cid}/networks', params=params)
    data = resp.json()
    return data['data']

'''

returns a list of dictionaries of networks
[
    {'id': 163888, 'range': '10.141.0.0/24'},
    {'id': 163890, 'range': '10.141.1.0/24'}
]

'''
def get_ipv4_networks(blkid):
    params = {
        'fields': 'range,id',
        'filter': "type:eq('IPv4Network')"
    }
    return get_collection_networks(blkid, params=params)

'''

Create a new Network and return its ID

'''

def create_ipv4_network(blkid, cidr):
    payload = {
            'type': 'IPv4Network',
            'range': cidr,
            'defaultView': {
                'id': ViewID,
                'type': 'View',
                'name': 'default'
            }
    }
    resp = req(
            'POST',
            f'/blocks/{blkid}/networks',
            json=payload,
            )
    data = resp.json()
    return data['id']

def delete_network_by_id(netid):
    if Debug:
        print(f'deleting network {netid}')
    resp = req(
            'DELETE',
            f'/networks/{netid}',
    )

'''
deletes a network by its CIDR block gracefully.
does nothing if it does not exist
'''

def delete_network(cidr):
    if netid := is_ipv4_network(cidr):
        delete_network_by_id(netid)

'''
Adds a network gracefully. If it's already there nothing happens
'''

def add_ipv4_network(cidr):
    if not is_ipv4_network(cidr):
        return create_ipv4_network(BlockID, cidr)
    else:
        return False

def is_ipv4_network(cidr):
    nets = get_ipv4_networks(BlockID)
    for net in nets:
        if net['range'] == cidr:
            return net['id']
    return False

'''
get_zones: Retrieve information about _all_ zones from all Configurations and Views

{'_links': {'accessRights': {'href': '/api/v2/zones/100918/accessRights'},
            'collection': {'href': '/api/v2/views/100917/zones'},
            'resourceRecords': {'href': '/api/v2/zones/100918/resourceRecords'},
            'self': {'href': '/api/v2/zones/100918'},
            'tags': {'href': '/api/v2/zones/100918/tags'},
            'transactions': {'href': '/api/v2/zones/100918/transactions'},
            'up': {'href': '/api/v2/views/100917'}},
 'configuration': {'_links': {'self': {'href': '/api/v2/configurations/100905'}},
                   'id': 100905,
                   'name': 'Production',
                   'type': 'Configuration'},
 'id': 100918,
 'name': 'Public',
 'type': 'ExternalHostsZone',
 'view': {'_links': {'self': {'href': '/api/v2/views/100917'}},
          'id': 100917,
          'name': 'Public',
          'type': 'View'}}

Zone from Zone list
{'_links': {'accessRights': {'href': '/api/v2/zones/100919/accessRights'},
            'collection': {'href': '/api/v2/views/100917/zones'},
            'deploymentOptions': {'href': '/api/v2/zones/100919/deploymentOptions'},
            'deploymentRoles': {'href': '/api/v2/zones/100919/deploymentRoles'},
            'deployments': {'href': '/api/v2/zones/100919/deployments'},
            'moves': {'href': '/api/v2/zones/100919/moves'},
            'namingPolicies': {'href': '/api/v2/zones/100919/namingPolicies'},
            'resourceRecords': {'href': '/api/v2/zones/100919/resourceRecords'},
            'restrictedRanges': {'href': '/api/v2/zones/100919/restrictedRanges'},
            'self': {'href': '/api/v2/zones/100919'},
            'signingKeys': {'href': '/api/v2/zones/100919/signingKeys'},
            'tags': {'href': '/api/v2/zones/100919/tags'},
            'templateApplications': {'href': '/api/v2/zones/100919/templateApplications'},
            'transactions': {'href': '/api/v2/zones/100919/transactions'},
            'up': {'href': '/api/v2/views/100917'},
            'userDefinedLinks': {'href': '/api/v2/zones/100919/userDefinedLinks'},
            'workflowRequests': {'href': '/api/v2/zones/100919/workflowRequests'},
            'zones': {'href': '/api/v2/zones/100919/zones'}},
 'absoluteName': 'ca',
 'configuration': {'_links': {'self': {'href': '/api/v2/configurations/100905'}},
                   'id': 100905,
                   'name': 'Production',
                   'type': 'Configuration'},
 'deploymentEnabled': False,
 'dynamicUpdateEnabled': False,
 'id': 100919,
 'name': 'ca',
 'signed': False,
 'signingPolicy': None,
 'template': None,
 'type': 'Zone',
 'userDefinedFields': None,
 'view': {'_links': {'self': {'href': '/api/v2/views/100917'}},
          'id': 100917,
          'name': 'Public',
          'type': 'View'}}

Zone from Zone list
{'_links': {'accessRights': {'href': '/api/v2/zones/100920/accessRights'},
            'collection': {'href': '/api/v2/zones/100919/zones'},
            'deploymentOptions': {'href': '/api/v2/zones/100920/deploymentOptions'},
            'deploymentRoles': {'href': '/api/v2/zones/100920/deploymentRoles'},
            'deployments': {'href': '/api/v2/zones/100920/deployments'},
            'moves': {'href': '/api/v2/zones/100920/moves'},
            ....

'''

def get_zones(params={}):
    resp = req('GET', '/zones', params=params)
    data = resp.json()
    return data['data']

'''
def get_zone_zones:  Retrieve all Zones under a given zone
'''

def get_zone_info(zid, params={}):
    resp = req('GET', f'/zones/{zid}', params=params)
    data = resp.json()
    return data

'''
get_conf_zones:  Retrieve all Zones under a give Configuration
Returns a list of Zones, one level below the View i.e. TLDS

[{'_links': {'accessRights': {'href': '/api/v2/zones/163800/accessRights'},
             'collection': {'href': '/api/v2/views/163799/zones'},
             'resourceRecords': {'href': '/api/v2/zones/163800/resourceRecords'},
             'self': {'href': '/api/v2/zones/163800'},
             'tags': {'href': '/api/v2/zones/163800/tags'},
             'transactions': {'href': '/api/v2/zones/163800/transactions'},
             'up': {'href': '/api/v2/views/163799'}},
  'configuration': {'_links': {'self': {'href': '/api/v2/configurations/163787'}},
                    'id': 163787,
                    'name': 'Test',
                    'type': 'Configuration'},
  'id': 163800,
  'name': 'Azure',
  'type': 'ExternalHostsZone',
  'view': {'_links': {'self': {'href': '/api/v2/views/163799'}},
           'id': 163799,
           'name': 'Azure',
           'type': 'View'}},
 {'_links': {'accessRights': {'href': '/api/v2/zones/163805/accessRights'},
             'collection': {'href': '/api/v2/views/163799/zones'},
             'deploymentOptions': {'href': '/api/v2/zones/163805/deploymentOptions'},
             'deploymentRoles': {'href': '/api/v2/zones/163805/deploymentRoles'},
             'deployments': {'href': '/api/v2/zones/163805/deployments'},
             'moves': {'href': '/api/v2/zones/163805/moves'},
             'namingPolicies': {'href': '/api/v2/zones/163805/namingPolicies'},
             'resourceRecords': {'href': '/api/v2/zones/163805/resourceRecords'},
             'restrictedRanges': {'href': '/api/v2/zones/163805/restrictedRanges'},
             'self': {'href': '/api/v2/zones/163805'},
             'signingKeys': {'href': '/api/v2/zones/163805/signingKeys'},
             'tags': {'href': '/api/v2/zones/163805/tags'},
             'templateApplications': {'href': '/api/v2/zones/163805/templateApplications'},
             'transactions': {'href': '/api/v2/zones/163805/transactions'},
             'up': {'href': '/api/v2/views/163799'},
             'userDefinedLinks': {'href': '/api/v2/zones/163805/userDefinedLinks'},
             'workflowRequests': {'href': '/api/v2/zones/163805/workflowRequests'},
             'zones': {'href': '/api/v2/zones/163805/zones'}},
  'absoluteName': 'com',
  'configuration': {'_links': {'self': {'href': '/api/v2/configurations/163787'}},
                    'id': 163787,
                    'name': 'Test',
                    'type': 'Configuration'},
  'deploymentEnabled': False,
  'dynamicUpdateEnabled': False,
  'id': 163805,
  'name': 'com',
  'signed': False,
  'signingPolicy': None,
  'template': None,
  'type': 'Zone',
  'userDefinedFields': None,
  'view': {'_links': {'self': {'href': '/api/v2/views/163799'}},
           'id': 163799,
           'name': 'Azure',
           'type': 'View'}},
 {'_links': {'accessRights': {'href': '/api/v2/zones/163806/accessRights'},
             'collection': {'href': '/api/v2/views/163799/zones'},
             'deploymentOptions': {'href': '/api/v2/zones/163806/deploymentOptions'},
             'deploymentRoles': {'href': '/api/v2/zones/163806/deploymentRoles'},

'''

def get_collection_zones(cid, params={}):
    collection = 'zones'
    if cid == ViewID:
        collection = 'views'
    resp = req('GET', f'/{collection}/{cid}/zones', params=params)
    data = resp.json()
    return data['data']

'''
Creates a Zone using recursion
'''

def create_zone(zone):
    zid = is_zone(zone)
    if zid:
        return zid
    else:
        (zname, subzone, subzid) = decouple(zone)
        pzid = create_zone(subzone)
        payload = {
            'type': 'Zone',
            'name': zname,
        }
        resp = req('POST', f'/zones/{pzid}/zones', json=payload)
        if resp.ok:
            print(f'new zone: {zone} has been created')
        else:
            data = resp.json()
            if Debug:
                pprint(data)
            return data['id']

'''

Deletes a Zone if it exists

'''

def delete_zone(zone):
    zid = is_zone(zone)
    if zid:
        resp = req('DELETE', f'/zones/{zid}')
        if resp.ok:
            print(f'Zone: {zone} has been deleted')
            return True
        else:
            data = resp.json()
            print(f'There was a problem deleting Zone: {zone}')
            pprint(data)
            return False
    else:
        print(f'Zone: {zone} does not exist')
        return False

'''
get_rrs: Retrieve all RRs
Returns a list of ALL RRs under all Configurations

[{'_links': {'accessRights': {'href': '/api/v2/resourceRecords/100922/accessRights'},
             'collection': {'href': '/api/v2/zones/100921/resourceRecords'},
             'moves': {'href': '/api/v2/resourceRecords/100922/moves'},
             'self': {'href': '/api/v2/resourceRecords/100922'},
             'tags': {'href': '/api/v2/resourceRecords/100922/tags'},
             'transactions': {'href': '/api/v2/resourceRecords/100922/transactions'},
             'up': {'href': '/api/v2/zones/100921'},
             'workflowRequests': {'href': '/api/v2/resourceRecords/100922/workflowRequests'}},
  'absoluteName': 'fands-bcit-ups.obm.utoronto.ca',
  'comment': None,
  'configuration': {'_links': {'self': {'href': '/api/v2/configurations/100905'}},
                    'id': 100905,
                    'name': 'Production',
                    'type': 'Configuration'},
  'dynamic': False,
  'id': 100922,
  'name': 'fands-bcit-ups',
  'text': 'APC,Smart-UPS,1000',
  'ttl': 10800,
  'type': 'TXTRecord',
  'userDefinedFields': None},
 {'_links': {'accessRights': {'href': '/api/v2/resourceRecords/100923/accessRights'},

'''

def get_rrs(cid=ConfID, params={}):
    params['filter'] = f'configuration.id:eq({cid})'
    resp = req('GET', f'/resourceRecords', params=params)
    data = resp.json()
    return data

def get_zone_rrs(zid, params={}):
    resp = req('GET', f'/zones/{zid}/resourceRecords', params=params)
    data = resp.json()
    return data['data']

def get_zone_rrs_by_type(zid, rr_type=None):
    params = {
        'filter': f"type:eq('{rr_type}')",
    }
    return get_zone_rrs(zid, params)

def get_zone_generic_rrs(zid):
    return get_zone_rrs_by_type(zid, 'GenericRecord')

def get_zone_cname_rrs(zid):
    return get_zone_rrs_by_type(zid, 'AliasRecord')

def get_zone_A_rrs(zid):
    params = {
            'filter': "type:eq('GenericRecord') and recordType:eq('A')",
    }
    return get_zone_rrs(zid, params=params)

def get_collection_rrs(cid, params={}):
    resp = req('GET', f'/deployments/{cid}/addedRecords', params=params)
    data = resp.json()
    return data

# Non API Functions below this line

def get_conf_rrs(cid, params={}):
    rrs = []
    allrrs = get_rrs(params)
    for rr in allrrs:
        rr_conf_id = rr['configuration']['id']
        print(rr_conf_id)
    return rrs

'''

External Host are needed to create Alias/CNAME records

'''

def create_ex_host(fqdn):
    exid = is_ex_host(fqdn)
    if exid:
        return exid
    else:
        payload = {
            'name': fqdn,
            'type': 'ExternalHostRecord',
        }
        resp = req('POST', f'/zones/{ExHostZoneID}/resourceRecords', json=payload)
        data = resp.json()
        return data['id']

'''

returns a dictionary of externalhosts and their IDs

'''

def get_ex_hosts():
    exhosts = dict()
    rrs = get_zone_rrs(ExHostZoneID)
    for rr in rrs:
        exhosts[rr['name']] = rr['id']
    return exhosts

'''
Check to see if an External Host already exists
If it does return its ID

'''

def is_ex_host(fqdn):
    hosts = get_ex_hosts()
    if fqdn in hosts:
        return hosts[fqdn]
    else:
        return False

'''

Creates RRs of all sorts
based on their respective schemas

'''

def create_rr(fqdn, RR_type, value):
    (name, zone, zid) = decouple(fqdn)
    if not zid:
        zid = create_zone(zone)  # this will create the zone if not already there
    payload = {
        'name': name,
        'type': RR_type,
        'ttl': TTL,
    }
    if RR_type == 'GenericRecord':
        (rr_type, rdata) = value.split('~')
        payload['recordType'] = rr_type
        payload['rdata'] = rdata
    elif RR_type == 'AliasRecord':
        ex_host_id = create_ex_host(value)
        payload['linkedRecord'] = {
            'id': ex_host_id,
            'type': 'ExternalHostRecord',
        }
    elif RR_type == 'HostRecord':
        toks = value.split(Dot)
        toks[3] = '0'
        network = Dot.join(toks)
        cidr = f'{network}/24'
        add_ipv4_network(cidr)
        payload['reverseRecord'] = False
        payload['addresses'] = [
            {
                'type': 'IPv4Address',
                'address': value
            }
        ]
    resp = req('POST', f'/zones/{zid}/resourceRecords', json=payload)
    if resp.ok:
        data = resp.json()
        print(f'A {RR_type} of value {value} for {fqdn} was created')
        if Debug:
            pprint(data)
        return data['id']
    else:
        print(f'There was an error creating RR for {fqdn} of type: {RR_type}')
        pprint(resp.text)
        return False

'''

A HostRecord of value 10.141.5.5 for hrec2.c.b.a.com was created

{
    '_links': {'accessRights': {'href': '/api/v2/resourceRecords/163903/accessRights'},
                'addresses': {'href': '/api/v2/resourceRecords/163903/addresses'},
                'collection': {'href': '/api/v2/zones/163859/resourceRecords'},
                'dependentRecords': {'href': '/api/v2/resourceRecords/163903/dependentRecords'},
                'moves': {'href': '/api/v2/resourceRecords/163903/moves'},
                'self': {'href': '/api/v2/resourceRecords/163903'},
                'tags': {'href': '/api/v2/resourceRecords/163903/tags'},
                'transactions': {'href': '/api/v2/resourceRecords/163903/transactions'},
                'up': {'href': '/api/v2/zones/163859'},
                'workflowRequests': {'href': '/api/v2/resourceRecords/163903/workflowRequests'}},
     'absoluteName': 'hrec2.c.b.a.com',
     'comment': None,
     'configuration': {'_links': {'self': {'href': '/api/v2/configurations/163787'}},
                       'id': 163787,
                       'name': 'Test',
                       'type': 'Configuration'},
     'dynamic': False,
     'id': 163903,
     'name': 'hrec2',
     'reverseRecord': False,
     'ttl': 3600,
     'type': 'HostRecord',
     'userDefinedFields': None
 }

'''

def create_hostrecord(fqdn, ipaddr):
    return create_rr(fqdn, 'HostRecord', ipaddr)

def create_generic_rr(fqdn, rr_type, value):
    return create_rr(fqdn, 'GenericRecord', f'{rr_type}~{value}')

def create_alias_rr(fqdn, exhost):
    return create_rr(fqdn, 'AliasRecord', exhost)

def add_CNAME_rr(fqdn, exhost):
    if not is_CNAME_rr(fqdn):
        return create_alias_rr(fqdn, exhost)

def add_A_rr(fqdn, value):
    if not is_A_rr(fqdn, value):
        return create_generic_rr(fqdn, 'A', value)
    else:
        return False

def add_Host_rr(fqdn, value):
    return

def is_generic_rr(fqdn, RR_type, value):
    (name, zone, zid) = decouple(fqdn)
    rrs = get_generic_rrs(zid)
    pprint(rrs)
    for rr in rrs:
        if rr['name'] == name and  rr['recordType'] == RR_type == value:
            if Debug:
                print(f'Found a matching RR for {fqdn} of type: {RR_type}')
            return rr['id']
    return False
    print(f'Subzone: {zone} does not exist')
    return False

def is_CNAME_rr(fqdn):
    (nm, zone, zid) = decouple(fqdn)
    rrs = get_zone_cname_rrs(zid)
    for rr in rrs:
        if rr['name'] == nm:
            return rr['linkedRecord']['absoluteName']
    if Debug:
        print(f'No corresponding CNAME record for {fqdn}')
    return False

def is_A_rr(fqdn, value):
    (nm, zone, zid) = decouple(fqdn)
    rrs = get_zone_A_rrs(zid)
    for rr in rrs:
        if rr['name'] == nm and rr['rdata'] == value:
            return rr['id']
    return False

def delete_generic_rr(fqdn, RR_type, value):
    rr_id = is_generic_rr(fqdn, RR_type, value)
    if rr_id:
        delete_rr_by_id(rr_id)
        if Debug:
            print(f'Generic record for {fqdn} of type {RR_type} and value {value} is deleted')
    else:
        print(f'There is no Generic Record corresponding to {fqdn}')

def delete_rr_by_id(rr_id):
    resp = req('DELETE', f'/resourceRecords/{rr_id}')
    if not resp.ok:
        print(f'Error in deleting: {fqdn}')

def delete_A_rr(fqdn, value):
    rr_id = is_A_rr(fqdn, value)
    if rr_id:
        delete__rr_by_id(rr_id)
    else:
        return False

'''

Updates a Generic RR if it exists and returns the new RR
Calls get_generic first. There may be more than one match

'''

def update_generic_rr(fqdn, RR_type, new_value):
    rrs = get_generic_rrs(fqdn, RR_type)
    if isinstance(rrs, list):
        rr = rrs[0]
        old_rdata = rr['rdata']
        if new_value == old_rdata:
            print(f'The Generic RR {fqdn} of type {RR_type} does not need updating as it already has the value {new_value}')
            return False
        if len(rrs) > 1:
            print(f'There are more than one RR with name {fqdn} and type {RR_type}')
            print(f'The one with value {old_rdata} will be updated to the new value {new_value}')
        rr['rdata'] = new_value
        url = f'{URL}/resourceRecords/{rr["id"]}'
        resp = requests.put(
            url,
            headers = Auth_header,
            json = rr,
            verify = Ca_bundle,
        )
        data = resp.json()
        if resp.ok:
            if Debug:
                print(f'{fqdn} has been updated to value {new_value}')
                pprint(data)
            return data
        else:
            print(f'{fqdn} could not be updated')
            return False
    else:
        print(f'There is no RR of type {RR_type} to update')
        return False

def update_A_rr(fqdn, new_value):
    return update_generic_rr(fqdn, 'A', new_value)

'''

Get all Generic Records matching a fqdn and RR type

'''

def get_generic_rrs(fqdn, RR_type):
    (name, zone, zid) = decouple(fqdn)
    if zid := is_zone(zone):
        matched = list()
        rrs = get_zone_rrs(zid)
        for rr in rrs:
            if rr['name'] == name and rr['type'] == 'GenericRecord' and rr['recordType'] == RR_type:
                matched.append(rr)
        if len(matched):
            return matched
        else:
            print(f'There are no RRs with name {fqdn} and type {RR_type} in zone {zone}')
            return False
    else:
        print(f'No RR with name {fqdn} as zone {zone} does not exist')
        return False

def get_conf_id(cfname):
    cid = 0
    params = {'fields': 'name,id,type'}
    confs = get_confs(params)
    for conf in confs:
        if conf['name'] == cfname:
            cid = conf['id']
            break
    return cid

def get_view_id(vname, cid):
    vid = 0
    params = {'fields': 'name,id,type'}
    views = get_conf_views(cid, params)
    for view in views:
        if view['name'] == vname:
            vid = view['id']
            break
    return vid

'''
returns a dictionary of {'name': id} for the Top Level Domains

'''

def get_tlds():
    dd = dict()
    parms = {
        'fields': 'name,id',
        'orderBy': 'asc(name)',
        'filter': "type:eq('Zone')",
    }
    ll = get_collection_zones(ViewID, params=parms)
    for l in ll:
        dd[l['name']] = l['id']
    return dd

'''

Get all Zones associated with a given View

'''

def get_view_zones(vid, params={}):
    data = get_collection_zones(vid, params=params)
    return data

def get_all_zones():
    dd = dict()
    params = {
        'limit': 5000,
        'fields': 'absoluteName,id',
        'filter': f"view.id:eq({ViewID}) and type:eq('Zone')",
    }
    zones = get_zones(params)
    for zone in zones:
        dd[zone['absoluteName']] = zone['id']
    return dd

'''
if zone exists return its Zone ID
else return False
Does not create a Zone rather returns False if not there

'''

def is_zone(zone):
    zones = get_all_zones()
    if zone in zones:
        return zones[zone]
    else:
        return False

def get_zone_id(zone):
    return is_zone(zone)

def get_subzones(zid):
    dd = dict()
    parms = {
        'fields': 'name,id',
        'orderBy': 'asc(name)',
        'filter': "type:eq('Zone')",
    }
    ll = get_collection_zones(zid, params=parms)
    for l in ll:
        dd[l['name']] = l['id']
    return dd

'''
[{'_links': {'accessRights': {'href': '/api/v2/zones/163800/accessRights'},
             'collection': {'href': '/api/v2/views/163799/zones'},
             'resourceRecords': {'href': '/api/v2/zones/163800/resourceRecords'},
             'self': {'href': '/api/v2/zones/163800'},
             'tags': {'href': '/api/v2/zones/163800/tags'},
             'transactions': {'href': '/api/v2/zones/163800/transactions'},
             'up': {'href': '/api/v2/views/163799'}},
  'configuration': {'_links': {'self': {'href': '/api/v2/configurations/163787'}},
                    'id': 163787,
                    'name': 'Test',
                    'type': 'Configuration'},
  'id': 163800,
  'name': 'Azure',
  'type': 'ExternalHostsZone',
  'view': {'_links': {'self': {'href': '/api/v2/views/163799'}},
           'id': 163799,
           'name': 'Azure',
           'type': 'View'}}]

'''

def get_external_hosts_zone_id(vid):
    params = {'filter': "type:eq('ExternalHostsZone')"}
    data = get_view_zones(ViewID, params=params)
    ex_id = data[0]['id']
    return ex_id

def req(method='GET', url='', params={}, json={}):

    try:
        resp = requests.request(
                method=method,
                url=f'{URL}{url}',
                headers=Header,
                params=params,
                json=json,
                verify=Ca_bundle,
                timeout=5.5,
                )
        resp.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print('\nHTTP Error')
        print(f'message: {errh.args[0]}\n')
    except requests.exceptions.ReadTimeout as errrt:
        print('Connection Time out')
    except requests.exceptions.ConnectionError as connerr:
        print('Connection error')

    if resp.ok:
        return resp
    else:
        print(f'return code: {resp.status_code}')
        print(f'url: {resp.url}')
        print(f'request method {resp.request.method}')
        print(f'request header {resp.request.headers}')
        print(f'request body {resp.request.body}')
        print(f'request response: {resp.text}')
        exit()

def test(nm,z):
    params = {}

    data = create_hostrecord(f'hrec3.{z}', '10.141.10.5')
    pprint(data)
    exit()
    delete_network('10.141.10.0/24')
    data = add_ipv4_network('10.141.1.0/24')
    pprint(data)
    data = add_ipv4_network('10.141.0.0/24')

    params = {'fields': 'name,id,range,type'}
    data = get_collection_networks(BlockID, params=params)
    pprint(data)
    exit()

    data = get_collection_blocks(ConfID)
    blkid = create_block(ConfID, CIDRBlock)
    print(blkid)
    blkid = get_ipv4_block_id(ConfID)
    if blkid:
        delete_block(blkid)
    pprint(data)
    data = get_ipv4_blocks(ConfID)

    data = is_CNAME_rr('who.c.b.a.com')
    zid = get_zone_id(z)
    data = get_zone_rrs(zid, 'AliasRecord')
    data = get_collection_blocks(ConfID, params=params)
    pprint(data)
    exit()

    data = add_A_rr(f'{nm}-test.{z}', '1.2.3.4')
    print(data)
    exit()

    data = create_alias_rr(f'who.{z}', 'www.quist.ca')
    pprint(data)
    get_confs()
    views = get_conf_views(params=params)
    views = get_views(params=params)
    pprint(views)
    data = get_conf(ConfID, params=params)
    data = get_view(ViewID, params=params)
    data = get_zones(params=params)
    data = get_zone_info(ExHostZoneID, params=params)
    data = get_collection_zones(ViewID, params=params)
    data = get_rrs(ConfID, params)
    data = create_ex_host('mary.woman.name.com')

'''

Does NOT create the zone component if it's not there

'''
def decouple(fqdn):
    toks = fqdn.split(Dot)
    name = toks.pop(0)
    zone = Dot.join(toks)
    zid = get_zone_id(zone)
    return(name, zone, zid)

def main():

    tok = basic_auth(uname, pw)

    zone = 'c.b.a.com'
    name = 'bozo'

    test(name,zone)

    create_ex_host('stan.kazy.person.org')

    fqdn1 = f'{name}1.{zone}'
    fqdn2 = f'{name}2.{zone}'
    fqdn3 = f'{name}3.{zone}'

    update_A_rr(fqdn1, '14.11.12.14')
    delete_A_rr(fqdn3, '33.11.11.11')

    zones = get_all_zones()
    pprint(zones)
    print(f'Zone: {zone} exists? {is_zone(zone)}')
    exit()

    data = get_tlds()
    for dname in data:
        dd = get_subzones(data[dname])
        print(f'Subzones of: {dname}')
        pprint(dd)

    exit()

    zones = get_view_zones(ViewID)
    pprint(zones)

    for zone in zones:
        zid = zone['id']
        rrs = get_zone_rrs(zid)
        pprint(rrs)
        print()
    exit()

    zones = get_zones()
    pprint(zones)
    exit()

    rrs = get_rrs(ConfID)
    pprint(rrs)

    confs = get_confs()
    for conf in confs:
        print()
        print(f'individual conf')
        cnf = get_conf(conf['id'])
        pprint(cnf)


    exit()
    confs = get_confs()
    for conf in confs:
        cid = conf['id']
        data = get_conf_views(cid)
        print(f'Conf ID: {cid} Views')
        pprint(data)

    views = get_views()
    for view in views:
        vid = view['id']
        print()
        print(f'View List Item')
        print(view)
        print()
        print(f'View: {vid}')
        data = get_view(vid)
        print(data)
    exit()


if __name__ == '__main__':
    main()
