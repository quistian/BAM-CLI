#!/usr/bin/env python

import getopt
import os
import sys

import re
from requests import Session, exceptions

from dotenv import load_dotenv
from pprint import pprint


"""
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

    Authorization: Basic Blah

"""

load_dotenv("/home/russ/.bamrc")

Debug = True
Debug = False
Header_Printed = False

Target = 'Dev'
Target = 'Prod'

if Target == 'Dev':
    Base = os.environ.get("BAM_DEV_ENDPT")
    Uname = os.environ.get("BAM_DEV_USER")
    Pw = os.environ.get("BAM_DEV_PW")
    Conf = os.environ.get("BAM_DEV_CONF")
    View = os.environ.get("BAM_DEV_VIEW")
elif Target == 'Prod':
    Base = os.environ.get("BAM_ENDPOINT")
    Uname = os.environ.get("BAM_USER")
    Pw = os.environ.get("BAM_PW")
    Conf = os.environ.get("BAM_CONF_AZ")
    View = os.environ.get("BAM_VIEW_AZ")
Ca_bundle = os.environ.get("BAM_CERT")


Dot = "."
CIDRBlock = "10.0.0.0/8"
ConfID = 0
ViewID = 0
ExHostZoneID = 0
BlockID = 0

Comment = "Modifications by v2API"

ViewZones = dict()

RR_Types = [
    "AliasRecord",
    "GenericRecord",
    "HINFORecord",
    "HostRecord",
    "ExternalHostRecord",
    "ExternalHostsZone",
    "NAPTRRecord",
    "SRVRecord",
    "TXTRecord",
]

Generic_RR_Types = [
    "A",
    "AAAA",
    "DNAME",
    "SFP",
    "PTR",
]

Network_Types = [
    "IPvvBlock",
    "IPv6Block",
    "IPv4Network",
    "IPv6Network",
    "IPv4Address",
    "IPv6Address",
]

TTL = 3600


Db = "bc_dns_delta.db"
Changed_zones = list()
Transaction_ids = list()


# Retrieve the configurations. Request the data as per BAM's default content type.

"""
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

"""


def basic_auth():
    global Sess, Header_Printed
    global ConfID, ViewID, ExHostZoneID, BlockID
    global Auth_header, Header, ViewZones

    if Debug:
        print(f"basic_auth: {Base} {Conf} {View}")

    mime_type = "application/json"
    Sess = Session()
    Sess.headers.update({"Content-Type": mime_type})
    resp = _request(
        "POST",
        "/sessions",
        payload={
            "username": Uname,
            "password": Pw,
        },
    )
    data = resp.json()
    if Debug:
        print("basic_auth: response:")
        pprint(data)
    token = data["basicAuthenticationCredentials"]
    Header_Printed = False

    Sess.headers.update({"Authorization": f"Basic {token}"})
    Sess.headers.update({"Accept": mime_type})
    Sess.headers.update({"User-Agent": "Generic BC Integrity API v2 Python Library"})
    Sess.headers.update({"x-bcn-change-control-comment": f"{Comment}"})
    Sess.verify = Ca_bundle

    ConfID = get_conf_id(Conf)
    ViewID = get_view_id(View, ConfID)
    ExHostZoneID = get_exhost_zone_id(ViewID)
    blocks = get_ipv4_blocks(ConfID)
    if len(blocks):
        BlockID = blocks[0]["id"]
    else:
        BlockID = create_block(ConfID, CIDRBlock)
    if Debug:
        print(f"basic_auth: ConfID: {ConfID}, ViewID: {ViewID} BlockID: {BlockID}")


"""
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
"""

# params = {'fields': 'id,name,type'}


def get_confs():
    resp = _request("GET", "/configurations", params={"fields": "name,id,type"})
    data = resp.json()
    return data["data"]


"""
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

 """


def get_conf(cid, params={}):
    resp = _request("GET", f"/configurations/{cid}", params)
    data = resp.json()
    return data


"""
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

"""


def get_conf_views(cid):
    resp = _request(
        "GET",
        path=f"/configurations/{cid}/views",
        params={"fields": "name,id,type"},
    )
    data = resp.json()
    if Debug:
        print("get_conf_views: data:")
    views = data["data"]
    return views


"""

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

"""

#    params = {'fields': 'id,configuration,name,type'}


def get_views(params={}):
    resp = _request("GET", "/views", params=params)
    data = resp.json()
    return data["data"]


"""
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

"""


def get_view(vid, params={}):
    resp = _request("GET", f"/views/{vid}", params=params)
    data = resp.json()
    return data


"""
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

"""


def get_collection_blocks(cid, params={}):
    resp = _request("GET", f"/configurations/{cid}/blocks", params=params)
    data = resp.json()
    return data["data"]


"""
Retrieve Transactions with a creationDateTime greater than '2022-01-10T14:14:45Z' and less than '2022-01-20T14:14:45Z'
GET http://{Address_Manager_IP}/api/v2/transactions?filter=creationDateTime:ge('2022-01-10T14:14:45Z') and creationDateTime:le('2022-01-20T14:14:45Z')

Returns:

{'_links': {'collection': {'href': '/api/v2/transactions'},
        'operations': {'href': '/api/v2/transactions/62986/operations'},
        'self': {'href': '/api/v2/transactions/62986'},
        'up': {'href': '/api/v2/1'}},
'comment': None,
'creationDateTime': '2024-11-18T15:18:10Z',
'description': 'Generic Record was added',
'id': 62986,
'operation': 'ADD_GENERIC_RECORD',
'revertingTransaction': None,
'transactionType': 'ADD',
'type': 'Transaction',
'user': {'_links': {'self': {'href': '/api/v2/users/108726'}},
         'id': 108726,
         'name': 'sutherl4',
         'type': 'User'}}
"""


def get_all_transactions(iso_start, iso_stop):
    resp = _request(
        "GET",
        "/transactions",
        params={
            "fields": "comment,creationDateTime,description,id,operation,transactionType,type,user",
            "filter": f"(creationDateTime:ge('{iso_start}') and creationDateTime:le('{iso_stop}'))",
        },
    )
    data = resp.json()
    actions = data["data"]
    return actions


#        'filter': f"((creationDateTime:ge('{iso_start}') and creationDateTime:le('{iso_stop}')) and operation:contains('GENERIC')",
#        'filter': f"creationDateTime:ge('{iso_start}') and creationDateTime:le('{iso_stop}') and operation:contains('GENERIC')",
#        'filter': f"creationDateTime:ge('{iso_start}') and creationDateTime:le('{iso_stop}') and (description:contains('Generic') or description:contains('Alias'))",


def get_rr_transactions(iso_start, iso_stop):
    """
    Transaction data structure:
        {
          'comment': None,
          'creationDateTime': '2024-11-19T19:09:47Z',
          'description': 'Generic Record was added',
          'id': 63263,
          'operation': 'ADD_GENERIC_RECORD',
          'transactionType': 'ADD',
          'type': 'Transaction',
          'user': {'_links': {'self': {'href': '/api/v2/users/108726'}},
                   'id': 108726,
                   'name': 'sutherl4',
                   'type': 'User'}
         }
     Note that operation is an enumeration, whereas description,
     So operation can not use the contains operation
    """

    actions = []
    limit = 1000
    offset = 0
    while True:
        resp = _request(
            "GET",
            "/transactions",
            # (description:contains('Generic') or description:contains('Alias'))",
            params = {
                "offset": offset,
                "limit": limit,
                "fields":
                "comment,creationDateTime,description,id,operation,transactionType,type,user",
                "filter": f"user.name:eq('{Uname}') and \
                creationDateTime:ge('{iso_start}') and \
                creationDateTime:le('{iso_stop}') and \
                operation:in('ADD_GENERIC_RECORD', 'DELETE_GENERIC_RECORD', 'UPDATE_GENERIC_RECORD', \
                'ADD_ALIAS_RECORD', 'DELETE_ALIAS_RECORD', 'UPDATE_ALIAS_RECORD')",
            },
        )
        data = resp.json()
        cnt = data["count"]
        if cnt > 0:
            actions.extend(data["data"])
        if cnt < limit:
            break
        else:
            offset += limit
    if Debug:
        print("get_rr_transactions: all RR transactions:")
        pprint(actions)
    return actions


"""

{'_links': {'collection': {'href': '/api/v2/transactions/62991/operations'},
            'self': {'href': '/api/v2/transactions/62991/operations/1'},
            'up': {'href': '/api/v2/transactions/62991'}},
 'fieldUpdates':
 [
     {'name': 'name', 'previousValue': None, 'value': 'n228_test'},
     {'name': 'comments', 'previousValue': None, 'value': None},
     {'name': 'recordType', 'previousValue': None, 'value': 'A'},
     {'name': 'rdata', 'previousValue': None, 'value': '10.140.164.98'},
     {'name': 'ttl', 'previousValue': None, 'value': 3600},
     {'name': 'absoluteName', 'previousValue': None, 'value': 'n228_test.privatelink_openai_azure_com.228'},
     {'name': 'dynamic', 'previousValue': None, 'value': 'No'}
 ],
 'id': 1,
 'operationType': 'ADD',
 'resourceId': 166806,
 'resourceType': 'GenericRecord',
 'type': 'Operation'}

"""


def get_transactions_operations(tid):
    resp = _request(
        "GET",
        f"/transactions/{tid}/operations",
        params={"fields": "fieldUpdates,operationType,resourceType,resourceId"},
    )
    data = resp.json()
    ops = data["data"]
    if Debug:
        print("get_trans_ops: Combined trans and ops")
        pprint(ops)
    return ops


"""
Create a CIDR Block for a given Configuration and return its ID
full data: {
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
"""


def create_block(cid, cidr):
    resp = _request(
        "POST",
        f"/configurations/{cid}/blocks",
        json={
            "type": "IPv4Block",
            "range": cidr,
            "comment": Comment,
        },
    )
    data = resp.json()
    return data["id"]


"""
Get the main Block IDs associated with a Configuration

"""


def get_ipv4_blocks(cid):
    resp = _request(
        "GET",
        path=f"/configurations/{cid}/blocks",
        params={"fields": "id", "filter": "type:eq('IPv4Block')"},
    )
    data = resp.json()
    blocks = data["data"]
    return blocks


def get_ipv4_block_id(cid):
    blocks = get_ipv4_blocks(cid)
    blk_id = blocks[0]["id"]
    return blk_id


"""
delete Network Block by its ID
"""


def delete_block(blkid):
    resp = _request(
        "DELETE",
        f"/blocks/{blkid}",
    )
    data = resp.json()
    return data


def get_collection_networks(cid, params={}):
    resp = _request(
        "GET",
        f"/blocks/{cid}/networks",
        params=params,
    )
    data = resp.json()
    return data["data"]


"""

returns a list of dictionaries of networks
[
    {'id': 163888, 'range': '10.141.0.0/24'},
    {'id': 163890, 'range': '10.141.1.0/24'}
]

"""


def get_ipv4_networks(blkid):
    params = {"fields": "range,id", "filter": "type:eq('IPv4Network')"}
    return get_collection_networks(blkid, params=params)


"""

Create a new Network and return its ID

"""


def create_ipv4_network(blkid, cidr):
    resp = _request(
        "POST",
        f"/blocks/{blkid}/networks",
        json={
            "type": "IPv4Network",
            "range": cidr,
            "defaultView": {"id": ViewID, "type": "View", "name": "default"},
            "comment": Comment,
        },
    )
    data = resp.json()
    return data["id"]


def delete_network_by_id(netid):
    if Debug:
        print(f"delete_network_by_id: deleted network id: {netid}")
    resp = _request(
        "DELETE",
        f"/networks/{netid}",
    )
    return resp.text


"""
deletes a network by its CIDR block gracefully.
does nothing if it does not exist
"""


def delete_network(cidr):
    if netid := is_ipv4_network(cidr):
        delete_network_by_id(netid)


"""
Adds a network gracefully. If it's already there nothing happens
"""


def add_ipv4_network(cidr):
    if not is_ipv4_network(cidr):
        return create_ipv4_network(BlockID, cidr)
    else:
        return False


def is_ipv4_network(cidr):
    nets = get_ipv4_networks(BlockID)
    for net in nets:
        if net["range"] == cidr:
            return net["id"]
    return False


"""
Get a list of IP addresses corresponding to a given Hostname RR
returns a list of them
"""


def get_addresses_by_hostname_id(hostid):
    addrs = list()
    resp = _request(
        "GET",
        f"/resourceRecords/{hostid}/addresses",
        params={"fields": "address"},
    )
    data = resp.json()
    for add_dict in data["data"]:
        addrs.append(add_dict["address"])
    return addrs


"""

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

"""


def get_zones(params={}):
    resp = _request("GET", "/zones", params=params)
    data = resp.json()
    if Debug:
        if "totalCount" in data:
            print(f'totalCount: {data["totalCount"]}')
    return data["data"]


"""
def get_zone_zones:  Retrieve all Zones under a given zone
"""


def get_zone_info(zid, params={}):
    resp = _request("GET", f"/zones/{zid}", params=params)
    data = resp.json()
    return data


"""
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

"""


def get_collection_zones(colid, params={}):
    if colid == ViewID:
        collection = "views"
    else:
        collection = "zones"
    resp = _request(
        "GET",
        f"/{collection}/{colid}/zones",
        params=params,
    )
    data = resp.json()
    if Debug:
        print("get_collection_zones: data:")
        pprint(data)
    return data["data"]


"""
Create a Zone from the root (View ID)
towards the leaf end point
"""


def create_zone(zone):
    pzid = ViewID
    community = "views"
    resp = _request(
        "POST",
        f"/{community}/{pzid}/zones",
        json={
            "type": "Zone",
            "absoluteName": zone,
            "comment": Comment,
        },
    )
    if resp.ok:
        data = resp.json()
        return data["id"]
    else:
        return False


"""
Creates a Zone using recursion
Checking first to see if it exists
Needs to change at the root to use views rather than zones as the collection
"""


def create_zone_recursively(zone):
    global ViewZones
    zid = is_zone(zone)
    if zid:
        return zid
    else:
        (zname, subzone, subzid) = decouple(zone)
        pzid = create_zone_recursively(subzone)
        community = "zones"
        resp = _request(
            "POST",
            f"/{community}/{pzid}/zones",
            json={
                "type": "Zone",
                "name": zname,
                "comment": Comment,
            },
        )
        if resp.ok:
            data = resp.json()
            zid = data["id"]
            if Debug:
                print(f"new zone: {zone} with ID {zid} has been created")
                pprint(data)
            ViewZones[zone] = zid
            return zid
        else:
            print(f"There was a problem creating subzone: {zone}")
            return False


"""

Deletes a Zone if it exists

"""


def delete_zone(zone):
    global ViewZones
    zid = is_zone(zone)
    if zid:
        resp = _request(
            "DELETE",
            f"/zones/{zid}",
        )
        if resp.status_code == 204:
            if Debug:
                print(f"delete_zone: Zone: {zone} has been deleted")
            del ViewZones[zone]
            return True
        else:
            data = resp.json()
            print(f"delete_zone: There was a problem deleting Zone: {zone}")
            pprint(data)
            return False
    else:
        print(f"delete_zone: Zone: {zone} does not exist")
        return False


"""
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

"""


def get_rrs(cid=ConfID):
    resp = _request(
        "GET",
        "/resourceRecords",
        params={
            "filter": f"configuration.id:eq({cid})",
        },
    )
    rrs = resp.json()
    return rrs


"""

Get _all_ Resource Records for a specific zone iD

"""


def get_zone_rrs(zid, params={}):
    resp = _request(
        "GET",
        f"/zones/{zid}/resourceRecords",
        params=params,
    )
    data = resp.json()
    return data["data"]


"""
Get RRs for specific zone ID and BlueCat RR type
"""


def get_zone_rrs_by_type(zid, rr_type, params={}):
    if Debug:
        print(f"get_zone_rrs_by_type: RRs for ZoneID {zid} of type {rr_type}")
    if rr_type in RR_Types:
        params["filter"] = f"type:eq('{rr_type}')"
    elif rr_type in Generic_RR_Types:
        params["filter"] = f"type:eq('GenericRecord') and recordType:eq('{rr_type}')"
    return get_zone_rrs(zid, params)


def get_zone_generic_rrs(zid):
    return get_zone_rrs_by_type(zid, "GenericRecord")


def get_zone_A_rrs(zid):
    params = {
        "fields": "absoluteName,rdata",
        "filter": "type:eq('GenericRecord') and recordType:eq('A')",
    }
    return get_zone_rrs(zid, params=params)


def get_zone_cname_rrs(zid):
    return get_zone_rrs_by_type(zid, "AliasRecord")


def get_zone_hostname_rrs(zid):
    hname_list = list()
    params = {
        "fields": "absoluteName,id",
        "filter": "type:eq('HostRecord')",
    }
    rrs = get_zone_rrs(zid, params=params)
    for rr in rrs:
        addrs = get_addresses_by_hostname_id(rr["id"])
        rr["ipaddr"] = addrs
        hname_list.append(rr)
    return hname_list


def get_all_A_rrs(zid):
    rr_dict = dict()
    for rr in get_zone_A_rrs(zid):
        rr_dict[rr["absoluteName"]] = rr["rdata"]
    for rr in get_zone_hostname_rrs(zid):
        rr_dict[rr["absoluteName"]] = rr["ipaddr"][0]
    return rr_dict


def get_hostname_addresses(fqdn):
    addrs = []
    (hname, zone, zid) = decouple(fqdn)
    if zid:
        rrs = get_zone_hostname_rrs(zid)
        for rr in rrs:
            if rr["name"] == hname:
                addrs = get_addresses_by_hostname_id(rr["id"])
    return addrs


def get_collection_rrs(cid, params={}):
    resp = _request(
        "GET",
        f"/deployments/{cid}/addedRecords",
        params=params,
    )
    rrs = resp.json()
    return rrs


# Non API Functions below this line


def get_conf_rrs(cid, params={}):
    rrs = list()
    allrrs = get_rrs(params)
    for rr in allrrs:
        rr_conf_id = rr["configuration"]["id"]
        print(rr_conf_id)
    return rrs


"""

External Host are needed to create Alias/CNAME records

"""


def create_ex_host(fqdn):
    exid = is_ex_host(fqdn)
    if exid:
        return exid
    else:
        resp = _request(
            "POST",
            f"/zones/{ExHostZoneID}/resourceRecords",
            json={
                "name": fqdn,
                "type": "ExternalHostRecord",
                "comment": Comment,
            },
        )
        data = resp.json()
        return data["id"]


"""

returns a dictionary of externalhosts and their IDs

"""


def get_ex_hosts():
    exhosts = dict()
    rrs = get_zone_rrs(ExHostZoneID)
    for rr in rrs:
        exhosts[rr["name"]] = rr["id"]
    return exhosts


"""
Check to see if an External Host already exists
If it does return its ID

"""


def is_ex_host(fqdn):
    hosts = get_ex_hosts()
    if fqdn in hosts:
        return hosts[fqdn]
    else:
        return False


"""

Creates RRs of all sorts
based on their respective schemas

"""


def create_rr(fqdn, RR_type, value):
    (name, zone, zid) = decouple(fqdn)
    if not zid:
        zid = create_zone(zone)  # this will create the zone if not already there

    payload = {
        "name": name,
        "type": RR_type,
        "ttl": TTL,
        "comment": Comment,
    }

    if RR_type == "GenericRecord":
        (rr_type, rdata) = value.split("~")
        payload["recordType"] = rr_type
        payload["rdata"] = rdata

    elif RR_type == "HINFORecord":
        (os, cpu) = value.split("~")
        payload["os"] = os
        payload["cpu"] = cpu

    elif RR_type == "HostRecord":
        toks = value.split(Dot)
        toks[3] = "0"
        network = Dot.join(toks)
        cidr = f"{network}/24"
        add_ipv4_network(cidr)
        payload["reverseRecord"] = False
        payload["addresses"] = [{"type": "IPv4Address", "address": value}]

    elif RR_type == "TXTRecord":
        payload["text"] = value

    # Indirection cases
    elif RR_type == "AliasRecord":
        ex_host_id = create_ex_host(value)
        payload["linkedRecord"] = {
            "id": ex_host_id,
            "type": "ExternalHostRecord",
        }

    elif RR_type == "MXRecord":
        mx_host_id = create_ex_host(value)
        if mx_host_id := is_Host_rr(value):
            payload["linkedRecord"] = {
                "id": mx_host_id,
                "type": "ExternalHostRecord",
            }

    # Create the RR via https
    resp = _request(
        "POST",
        f"/zones/{zid}/resourceRecords",
        json=payload,
    )

    if resp.ok:
        data = resp.json()
        print(f"A {RR_type} of value {value} for {fqdn} was created")
        if Debug:
            pprint(data)
        return data["id"]
    else:
        print(f"There was an error creating RR for {fqdn} of type: {RR_type}")
        pprint(resp.text)
        return False


"""

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

"""


# RRs with a level in Indirection
def create_alias_rr(fqdn, exhost):
    return create_rr(fqdn, "AliasRecord", exhost)


def create_mx_rr(fqdn, mxhost):
    return create_rr(fqdn, "MXRecord", mxhost)


# Regular RRs


def create_hostrecord(fqdn, ipaddr):
    return create_rr(fqdn, "HostRecord", ipaddr)


def create_generic_rr(fqdn, rr_type, value):
    return create_rr(fqdn, "GenericRecord", f"{rr_type}~{value}")


def create_txt_rr(fqdn, rr_type, value):
    return create_rr(fqdn, "TXTRecord", value)


"""

Graceful Representations of the above creation rr routines
add_ rather than create_

"""


def add_CNAME_rr(fqdn, exhost):
    if not is_CNAME_rr(fqdn):
        return create_alias_rr(fqdn, exhost)


"""
Add an Generic A record gracefully
Will create the subzone if it is not already there
"""


def add_A_rr(fqdn, value):
    if not is_A_rr(fqdn, value):
        return create_generic_rr(fqdn, "A", value)
    else:
        return False


def add_TXT_rr(fqdn, text):
    if not is_TXT_rr(fqdn, text):
        return create_rr(fqdn, "TXTRecord", text)
    else:
        return False


def add_Host_rr(fqdn, value):
    if not is_Host_rr(fqdn):
        create_hostrecord(fqdn, value)
    else:
        return False


def is_generic_rr(fqdn, RR_type, value):
    (hname, zone, zid) = decouple(fqdn)
    if zid:
        rrs = get_generic_rrs(zid)
        for rr in rrs:
            if (
                rr["hname"] == hname
                and rr["recordType"] == RR_type
                and rr["rdata"] == value
            ):
                if Debug:
                    print(
                        f"Found a matching RR for {fqdn} of type: {RR_type} with value {value}"
                    )
                return rr["id"]
        if Debug:
            print(f"No  matching RRs for {fqdn} of type {RR_type} and value {value}")
        return False
    else:
        if Debug:
            print(
                f"Subzone: {zone} does not exist for the Generic Record with hostname {fqdn}"
            )
        return False


def is_CNAME_rr(fqdn):
    (nm, zone, zid) = decouple(fqdn)
    rrs = get_zone_cname_rrs(zid)
    for rr in rrs:
        if rr["name"] == nm:
            return rr["linkedRecord"]["absoluteName"]
    if Debug:
        print(f"No corresponding CNAME record for {fqdn}")
    return False


def is_TXT_rr(fqdn, value):
    (hname, zone, zid) = decouple(fqdn)
    if zid:
        rrs = get_zone_rrs_by_type(zid, "TXTRecord")
        for rr in rrs:
            if rr["name"] == hname and rr["text"] == value:
                return rr["id"]
        if Debug:
            print(f"No TXT RRs were found corresponding to {fqdn} and {value}")
        return False
    else:
        if Debug:
            print(
                f"There is no zone {zone} corresponding to the TXT record for hostname {fqdn}"
            )
        return False


def is_A_rr(fqdn, value):
    (hname, zone, zid) = decouple(fqdn)
    if zid:
        rrs = get_zone_rrs_by_type("A")
        for rr in rrs:
            if rr["name"] == hname and rr["rdata"] == value:
                return rr["id"]
        if Debug:
            print(f"No A RRs were found corresponding to {fqdn} and {value}")
        return False
    else:
        if Debug:
            print(
                f"There is no zone {zone} corresponding to the A record for hostname {fqdn}"
            )
        return False


def is_Host_rr(fqdn, value="10.141.0.0"):
    (hname, zone, zid) = decouple(fqdn)
    if zid:
        rrs = get_zone_hostname_rrs(zid)
        for rr in rrs:
            if rr["name"] == hname:
                return rr["id"]
        if Debug:
            print(f"No Hostname A RRs were found corresponding to {fqdn}")
        return False
    else:
        if Debug:
            print(
                f"There is no zone {zone} corresponding to any Host records for the hostname {fqdn}"
            )
        return False


def delete_generic_rr(fqdn, RR_type, value):
    rr_id = is_generic_rr(fqdn, RR_type, value)
    if rr_id:
        delete_rr_by_id(rr_id)
        if Debug:
            print(
                f"Generic record for {fqdn} of type {RR_type} and value {value} is deleted"
            )
    else:
        print(f"There is no Generic Record corresponding to {fqdn}")


def delete_rr_by_id(rr_id):
    resp = _request(
        "DELETE",
        f"/resourceRecords/{rr_id}",
    )
    if not resp.ok:
        print(f"Error in deleting: rr with id: {rr_id}")


def delete_TXT_rr(fqdn, txt):
    (hname, zone, zid) = decouple(fqdn)
    if rr_id := is_TXT_rr(fqdn, txt):
        delete_rr_by_id(rr_id)
        if Debug:
            print(f"TXT RR {fqdn} with value {txt} deleted")
        return True
    else:
        if Debug:
            print(f"No TXT RR {fqdn} with value {txt} to delete")
        return False


def delete_A_rr(fqdn, value):
    (hname, zone, zid) = decouple(fqdn)
    if zid:
        if rr_id := is_A_rr(zid, fqdn, value):
            delete_rr_by_id(rr_id)
        else:
            if Debug:
                print(
                    f"There was no A record with value {value} corresponding to {fqdn}"
                )
            return rr_id
    else:
        if Debug:
            print(f"{fqdn} was not deleted as {zone} does not yet exist")
        return False


"""

Updates a Generic RR if it exists and returns the new RR
Calls get_generic first. There may be more than one match

"""


def update_generic_rr(fqdn, RR_type, new_value):
    rrs = get_generic_rrs(fqdn, RR_type)
    if isinstance(rrs, list):
        rr = rrs[0]
        old_rdata = rr["rdata"]
        if new_value == old_rdata:
            print(
                f"The Generic RR {fqdn} of type {RR_type} does not need updating as it already has the value {new_value}"
            )
            return False
        if len(rrs) > 1:
            print(f"There are more than one RR with name {fqdn} and type {RR_type}")
            print(
                f"The one with value {old_rdata} will be updated to the new value {new_value}"
            )
        rr["rdata"] = new_value
        if "comment" not in rr:
            rr["comment"] = Comment
        resp = _request(
            "PUT",
            f'/resourceRecords/{rr["id"]}',
            json=rr,
        )
        data = resp.json()
        if resp.ok:
            if Debug:
                print(f"{fqdn} has been updated to value {new_value}")
                pprint(data)
            return data
        else:
            print(f"{fqdn} could not be updated")
            return False
    else:
        print(f"There is no RR of type {RR_type} to update")
        return False


def update_A_rr(fqdn, new_value):
    return update_generic_rr(fqdn, "A", new_value)


"""

Get all Generic Records matching a fqdn and RR type

"""


def get_generic_rrs(fqdn, RR_type):
    (name, zone, zid) = decouple(fqdn)
    if zid := is_zone(zone):
        matched = list()
        rrs = get_zone_rrs(zid)
        for rr in rrs:
            if (
                rr["name"] == name
                and rr["type"] == "GenericRecord"
                and rr["recordType"] == RR_type
            ):
                matched.append(rr)
        if len(matched):
            return matched
        else:
            print(
                f"There are no RRs with name {fqdn} and type {RR_type} in zone {zone}"
            )
            return False
    else:
        print(f"No RR with name {fqdn} as zone {zone} does not exist")
        return False


def get_conf_id(cf_name):
    confs = get_confs()
    for conf in confs:
        if conf["name"] == cf_name:
            conf_id = conf["id"]
            break
    if Debug:
        print(f"get_conf_id: Conf ID: {conf_id}")
    return conf_id


def get_view_id(vname, cid):
    vid = 0
    views = get_conf_views(cid)
    for view in views:
        if view["name"] == vname and view["type"] == "View":
            vid = view["id"]
            break
    if Debug:
        print(f"get_view_id: view_id: {vid}")
    return vid


"""
returns a dictionary of {'name': id} for the Top Level Domains

"""


def get_tlds():
    dd = dict()
    parms = {
        "fields": "name,id",
        "orderBy": "asc(name)",
        "filter": "type:eq('Zone')",
    }
    zones = get_collection_zones(ViewID, params=parms)
    for zone in zones:
        dd[zone["name"]] = zone["id"]
    return dd


"""

Get all Zones associated with a given View

"""


def get_view_zones(vid, params={}):
    data = get_collection_zones(vid, params=params)
    return data


"""
Get all the zones in the given View and Config

"""


def get_all_zones(cid, vid):
    dd = dict()
    params = {
        "limit": 5000,
        "fields": "absoluteName,id",
        "filter": f"configuration.id:eq({cid}) and view.id:eq({vid}) and type:eq('Zone')",
    }
    zones = get_zones(params)
    for zone in zones:
        dd[zone["absoluteName"]] = zone["id"]
    return dd


def get_all_leaf_zones():
    zlist = list()
    for zone in ViewZones:
        toks = zone.split(Dot)
        leaf = toks.pop(0)
        if re.match("[1-9][0-9][0-9]", leaf):
            zlist.append(zone)
    return zlist


"""
if zone exists return its Zone ID
else return False
Does not create a Zone rather returns False if not there

"""


def is_zone(zone):
    if zone in ViewZones:
        return ViewZones[zone]
    else:
        return False


def get_zone_id(zone):
    return is_zone(zone)


def get_subzones(zid):
    dd = dict()
    params = {
        "fields": "name,id",
        "orderBy": "asc(name)",
        "filter": "type:eq('Zone')",
    }
    coll_zones = get_collection_zones(zid, params=params)
    for zone in coll_zones:
        dd[zone["name"]] = zone["id"]
    return dd


"""
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

"""


def get_exhost_zone_id(vid):
    #    data = get_view_zones(ViewID, params=params)
    resp = _request(
        "GET",
        path=f"/views/{vid}/zones",
        params={"filter": "type:eq('ExternalHostsZone')"},
    )
    data = resp.json()
    zones = data["data"]
    ex_id = zones[0]["id"]
    if Debug:
        print("get_exhost_zone_id: Zone ID: {ex_id}")
    return ex_id


"""
Output:
    'count': 1,
     'data': [{'activeSessions': 6,
               'address': '10.192.103.151',
               'hostname': 'proteus-dev',
               'id': 1,
               'interfaceRedundancyEnabled': False,
               'type': 'SystemSettings',
               'version': '9.5.3-1036.GA.bcn'}]}
"""


def get_system_info():
    resp = _request(
        "GET",
        path="/settings",
        params={"filter": "type:eq('SystemSettings')"},
    )
    data = resp.json()["data"][0]
    if Debug:
        print("get_system_info:")
        pprint(data)
    return data


def get_system_version():
    info = get_system_info()
    version = info["version"]
    if Debug:
        print(f"get_system_version: {version}")
    return version


def _request(method, path, params=None, payload=None):
    global Sess, Header_Printed

    url = f"https://{Base}/api/v2{path}"
    if Debug:
        if not Header_Printed:
            print("_request: Session Header")
            [print(f"{key}: {val}") for key, val in Sess.headers.items()]
            print()
            Header_Printed = True
        if params is not None:
            print(f"_request: parameters: {params}")
        if payload is not None:
            print(f"_request: json payload: {payload}")
    try:
        resp = Sess.request(method, url, params=params, json=payload, timeout=(5, 10))
        resp.raise_for_status()
    except exceptions.HTTPError as http_err:
        print(f"HTTP error status: {http_err}")
    except exceptions.ConnectionError as conn_err:
        print(f"Connection error status: {conn_err}")
    except exceptions.ReadTimeout as read_timeout_err:
        print(f"Read Timeout error status: {read_timeout_err}")
    except exceptions.Timeout as timeout_err:
        print(f"Timeout error status: {timeout_err}")
    except exceptions.URLRequired as url_err:
        print(f"Invalid URL error status: {url_err}")
    except exceptions.RequestException as err:
        print(f"An error occurred status: {err}")
    else:
        if resp.ok:
            return resp
        else:
            print(f"_request: return code: {resp.status_code}")
            print(f"_request: url: {resp.url}")
            print(f"_request method {resp.request.method}")
            print(f"_request header {resp.request.headers}")
            print(f"_request body {resp.request.body}")
            print(f"_request response: {resp.text}")


def test(nm, z):
    params = {}

    az_zone = "privatelink.openai.azure.com"
    hr_num = "434"
    hr_num = "543"
    hr_num = "278"
    hname = f"q{hr_num}-txt-rr"
    fqdn = f"{hname}.{hr_num}.{az_zone}"

    zone = f"{hr_num}.{az_zone}"
    zone = "i.was.once.to"

    zid = get_zone_id(f"{hr_num}.{az_zone}")
    data = get_zone_rrs(zid)
    pprint(data)

    data = delete_zone(zone)
    data = create_zone(zone)
    pprint(data)

    data = get_collection_zones(ViewID)
    zones = get_all_leaf_zones()
    for zone in zones:
        zid = get_zone_id(zone)
        data = get_all_A_rrs(zid)
        if len(data):
            pprint(data)
    data = delete_TXT_rr(fqdn, "Brian Mulroney has been deceased!")
    pprint(data)
    data = add_TXT_rr(fqdn, "Brian Mulroney is now resurrected")
    pprint(data)

    data = get_hostname_addresses(fqdn)
    data = add_Host_rr(f"q434-bozo-2.434.{az_zone}", "10.141.10.10")
    pprint(data)

    data = add_A_rr(f"q434-test.434.{az_zone}", "10.141.15.15")
    pprint(data)

    data = create_zone(az_zone)
    data = create_hostrecord(f"hrec3.{z}", "10.141.10.5")
    delete_network("10.141.10.0/24")
    data = add_ipv4_network("10.141.1.0/24")
    pprint(data)
    data = add_ipv4_network("10.141.0.0/24")

    params = {"fields": "name,id,range,type"}
    data = get_collection_networks(BlockID, params=params)
    pprint(data)

    data = get_collection_blocks(ConfID)
    blkid = create_block(ConfID, CIDRBlock)
    print(blkid)
    blkid = get_ipv4_block_id(ConfID)
    if blkid:
        delete_block(blkid)
    pprint(data)
    data = get_ipv4_blocks(ConfID)

    data = is_CNAME_rr("who.c.b.a.com")
    zid = get_zone_id(z)
    data = get_zone_rrs(zid, "AliasRecord")
    data = get_collection_blocks(ConfID, params=params)
    pprint(data)

    data = create_alias_rr(f"who.{z}", "www.quist.ca")
    pprint(data)
    get_confs()
    views = get_conf_views()
    views = get_views(params=params)
    pprint(views)
    data = get_conf(ConfID, params=params)
    data = get_view(ViewID, params=params)
    data = get_zones(params=params)
    data = get_zone_info(ExHostZoneID, params=params)
    data = get_collection_zones(ViewID, params=params)
    data = get_rrs(ConfID, params)
    data = create_ex_host("mary.woman.name.com")

    create_ex_host("stan.kazy.person.org")
    zones = get_all_zones(ConfID, ViewID)
    pprint(zones)
    print(f"Zone: {zone} exists? {is_zone(zone)}")
    data = get_tlds()
    for dname in data:
        dd = get_subzones(data[dname])
        print(f"Subzones of: {dname}")
        pprint(dd)
    zones = get_view_zones(ViewID)
    pprint(zones)
    for zone in zones:
        zid = zone["id"]
        rrs = get_zone_rrs(zid)
        pprint(rrs)
        print()
    zones = get_zones()
    pprint(zones)
    rrs = get_rrs(ConfID)
    pprint(rrs)
    confs = get_confs()
    for conf in confs:
        print()
        print("Individual Conf")
        cnf = get_conf(conf["id"])
        pprint(cnf)
    confs = get_confs()
    for conf in confs:
        cid = conf["id"]
        data = get_conf_views(cid)
        print(f"Conf ID: {cid} Views")
        pprint(data)
    views = get_views()
    for view in views:
        vid = view["id"]
        print()
        print("View List Item")
        print(view)
        print()
        print(f"View: {vid}")
        data = get_view(vid)
        print(data)


"""

Does NOT create the zone component if it's not there

"""


def decouple(fqdn):
    toks = fqdn.split(Dot)
    name = toks.pop(0)
    zone = Dot.join(toks)
    zid = get_zone_id(zone)
    return (name, zone, zid)


def main():
    return True


def test2():
    global Debug
    arglist = sys.argv[1:]
    # options
    opts = "hdvq"
    # longer options
    long_opts = ["help", "debug", "verbose", "quiet"]
    try:
        args, vals = getopt.getopt(arglist, opts, long_opts)
        for cur_arg, cur_val in args:
            if cur_arg in ["-h", "--help"]:
                print("This is a holding area for help information")
                exit()
            elif cur_arg in ["-d", "--debug"]:
                Debug = True
            elif cur_arg in ["-v", "--verbose"]:
                Debug = True
            elif cur_arg in ["-q", "--quiet"]:
                Debug = False
    except getopt.error as err:
        print(str(err))
        exit()

    basic_auth()


if __name__ == "__main__":
    main()
