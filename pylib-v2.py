#!/usr/bin/env python

# a one liner

"""
A v2 API for BAM based on the pip bluecat libraries

Base v2 API documentation:

    https://docs.bluecatnetworks.com/r/en-US/Address-Manager-RESTful-v2-API-Guide/9.5.0

Python Specific documentation:
    https://docs.bluecatnetworks.com/r/en-US/BlueCat-Python-Library-Guide/24.1
    https://docs.bluecatnetworks.com/r/BlueCat-Python-Library-Guide/BlueCat-Library-Address-Manager-REST-v2-API-client-reference/24.1

Install/Upgrade:
    pip install --upgrade bluecat-libraries

Client class:

    A client for making HTTP calls to BAM REST v2 API.

    There is a method for each HTTP verb - GET, POST, PUT, PATCH, and
    DELETE - as well as a generic method for a HTTP request: http_get,
    http_post, http_put, http_patch, http_delete, and http_request. The
    functionality of the client relies on the use of these methods.

    The benefits of this client over a direct use of the requests Python
    library are:

        Available methods for performing login and logout, as well as
        determining the version of the BlueCat Address Manager.

        The client keeps track of the authentication token and automatically
        sends it with each request.

        The client keeps track of the base API URL, needing only the relative
        path to be specified when making a request.

        The client automatically parses the responses and returns Python
        data structures - dictionaries or strings - based on the response
        content type.

        The client detects error responses and raises a Python exception,
        which holds the fields that the BAM API replied with, e.g, code.

    Overall, users of the client can write less code and keep track of
    less data when making requests to the BAM REST v2 API.

    Nonetheless, the client allows for taking advantage of the full
    functionality of the BAM REST v2 API by exposing all available
    requests parameters in its methods. That way a user can, for example,
    specify filters and fields selection through URL query parameters.

    You need to authenticate to the BAM REST v2 API when making
    calls. The client will use HTTP header Authorization as per the
    BAM documentation. You have to either perform a login via the
    client method (with a username and a password) or set the auth
    property to the full value for the header, including the
    authorization scheme.

    Note:

    The client does not specify a value for the Accept header by
    default. This results in the Content-Type of the response to
    be determined by the defaults of BAM.

"""

import os
import sys
import json
import csv

from pprint import pprint
from dotenv import load_dotenv
from bluecat_libraries.address_manager.apiv2 import Client, MediaType, BAMV2ErrorResponse

load_dotenv("/home/russ/.bamrc")

# Some global variables

Debug = False
Debug = True

Ca_bundle = '/etc/ssl/Sectigo-AAA-chain.pem'
Verfy = False
Verfy = Ca_bundle

Header = {"Accept": MediaType.JSON}

EndPoint = os.environ.get('BAM_ENDPOINT')
Url = f'https://{EndPoint}/api/v2/'
Uname = os.environ.get('BAM_USER')
Pw = os.environ.get('BAM_PW')

# Name and IDs of BAM Configuration and View
Conf = os.environ.get('BAM_CONF')
View = os.environ.get('BAM_VIEW')
View_Id = 0
Conf_Id = 0

# Static cached list of zones and their respective IDs
# Zones is all zones, starting at the root
# Leaves are the endpoints of the Zone tree
# Private are the Zones which correspond to the Azure Resource names

Zones = {}
Leaves = {}
Private = {}

# Retrieve the configurations. Request the data as per BAM's default content type.

def init():
    global Clt
    global Conf_Id, View_Id

    Clt = Client(Url, verify=Ca_bundle)
    data = Clt.login(Uname, Pw)
    if Clt.is_authenticated:
        if Debug:
            print(f'BAM auth: {Clt.auth}')
            print(f'BAM url: {Clt.bam_url}')
        Conf_Id = get_conf_id()
        View_Id = get_view_id()
        if Debug:
            print(f'Conf ID: {Conf_Id}')
            print(f'View ID: {View_Id}')
    else:
        print(f'Could not authenticate: {data}')
        exit()

#        params = {"fields": "id,name"},

def get_confs():
    resp = Clt.http_get(
        "/configurations",
        headers = Header,
    )
    return resp['data']

def get_conf(idy):
    path = f'/configurations/{idy}'
    resp = Clt.http_get(
        path,
        headers = Header,
    )
    return resp['data']

def get_views():
    path = '/views'
    parms = {
        'offset': 0,
        'limit': 100,
    }
    resp = Clt.http_get(
        path,
        params = parms,
    )
    return resp['data']

def get_view(idy):
    path = f'/views/{idy}'
    resp = Clt.http_get(
        path,
        headers = Header,
    )
    return resp['data']

'''
View Data Structure:

View: 163799

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
 'userDefinedFields': None}

'''

def get_view_id():
    path = '/views'
    parms = {
        'offset': 0,
        'limit': 100,
        'fields': 'id,name,configuration',
        'filter': f"name:eq('{View}') and configuration.id:eq({Conf_Id})",
    }
    resp = Clt.http_get(
        path,
        headers = Header,
        params = parms,
    )
    return resp['data'][0]['id']

def get_conf_id():
    path = '/configurations'
    parms = {
        'fields': 'id,name',
        'filter': f"name:eq('{Conf}')", 
    }
    resp = Clt.http_get(
        path,
        headers = Header,
        params = parms,
    )
    return resp['data'][0]['id']

"""
Full zone data structure from view collection:

 {'absoluteName': 'ms',
  'configuration': {'id': 2200891, 'name': 'Test', 'type': 'Configuration'},
  'deploymentEnabled': False,
  'dynamicUpdateEnabled': False,
  'id': 2865098,
  'name': 'ms',
  'signed': False,
  'signingPolicy': None,
  'template': None,
  'type': 'Zone',
  'userDefinedFields': None,
  'view': {'id': 2734992, 'name': 'Azure', 'type': 'View'}},
"""

def get_view_zones(vid):
    path = f'/views/{vid}/zones'
    parms = {
            'fields': 'absoluteName,id,name,type',
            'filter': 'type:eq("Zone")',
    }
    zones = Clt.http_get(
        path,
        headers = Header,
        params = parms,
        )
    return zones['data']

def get_zone_zones(zid):
    path = f'/zones/{zid}/zones'
    # parms = {'fields': 'embed(resourceRecords.addresses)'}
    parms = {
            'fields': 'absoluteName,id',
            'filter': 'type:eq("Zone")',
    }
    zones = Clt.http_get(
            path,
            headers = Header,
            params = parms,
    )
    return zones['data']

"""

{
'id': 3035964,
'type': 'GenericRecord',
'name': 'q573_test_646',
'configuration': {'id': 2200891, 'type': 'Configuration', 'name': 'Test'},
'ttl': None,
'absoluteName': 'q573_test_646.573.privatelink.redisenterprise.cache.azure.net',
'comment': None,
'dynamic': False,
'recordType': 'A',
'rdata': '10.141.144.179',
'userDefinedFields': None
}

"""

def get_zone_rrs(zid):
    path = f'/zones/{zid}/resourceRecords'
    parms = {
        'fields': 'id,name,absoluteName,rdata,ttl',
        'filter': 'type:eq("GenericRecord") and recordType:eq("A")',
    }
    rrs = Clt.http_get(
            path,
            headers = Header,
            params = parms,
    )
    return rrs['data']

"""
Get all zones for a given view and type == Zone
"""

def get_zones():
    global Zones

    if len(Zones):
        return Zones
    else:
        path = '/zones'
        parms = {
            'fields': 'id,name,absoluteName',
            'filter': f'type:eq("Zone") and view.id:eq({View_Id})',
        }
        resp = Clt.http_get(
                path,
                headers = Header,
                params = parms,
        )
        Zones = resp['data']
        return Zones

def get_rrs():
    path = '/resourceRecords'
    parms = {
        'fields': 'id,name,configuration,ttl,absoluteName,recordType,rdata',
        'filter': f'configuration.id:eq({Conf_Id}) and absoluteName:contains("privatelink")',
        'limit': 10000,
        'total': True,
    }
    resp = Clt.http_get(
        path,
        headers = Header,
        params = parms,
    )
    data = resp['data']
    return data


"""

Add a zone in fqdn form below the root view
Returns the ID of the new zone

"""

def add_zone(zone):
    global Zones

    path = f'/views/{View_Id}/zones'
    payload = {
        'type': 'Zone',
        'absoluteName': zone,
    }
    Header['x-bcn-change-control-comment'] = 'Zone Added Python v2 BAM 9.5 API'
    try:
        resp = Clt.http_post(
            path,
            headers = Header,
            json = payload,
        )
        newzone = dict()
        for key in ['id', 'name', 'absoluteName']:
            newzone[key] = resp[key]
        Zones.append(newzone)
        return resp['id']
    except BAMV2ErrorResponse as exc:
        print(exc.message)
        return -exc.status

# zone is a dict item with keys: absoluteName, name, id
def del_zone(zid):
    path = f'/zones/{zid}'
    Header['x-bcn-change-control-comment'] = 'Zone Deleted Python v2 BAM 9.5 API'
    try:
        resp = Clt.http_delete(
            path,
            headers = Header,
        )
        if Debug:
            print(f'Deleting zone associated with id: {zid}')
    except BAMV2ErrorResponse as exc:
        print(exc.message)
        return -exc.status

# Utility functions, based on low level v2 API

# Detail description:
# https://proteus-dev.its.utoronto.ca/api/docs/?context=AddressManager

def delete_zone(zname):
    global Zones

    zid = 0
    for zone in get_zones():
        if zone['absoluteName'] == zname:
            zid = zone['id']
    if zid:
        del_zone(zid)
        Zones.remove(zone)
    else:
        print(f'No zone named {zname} to delete')

def get_tlds():
    return get_view_zones(View_Id)

def get_leaf_zones():
    global Leaves

    if len(Leaves):
        return Leaves
    else:
        zones = get_zones()
        for zone in zones:
            if zone['name'].isnumeric():
                Leaves[zone['absoluteName']] = zone['id']
        return Leaves

def get_private_zones():
    global Private

    if len(Private):
        return Private
    else:
        zones = get_zones()
        for zone in zones:
            if zone['name'] == 'privatelink':
                Private[zone['absoluteName']] = zone['id']
        return Private

def main():

    init() #sets Clt

    Z = 'bozo.com'

    delete_zone(Z)
    add_zone(Z)
    exit()

    for leaf in get_leaf_zones():
        print(leaf)

    for priv in get_private_zones():
        print(priv)

    data = add_zone('a.b.c.com')
    pprint(data)

    leaves = get_leaf_zones()
    for leaf in leaves:
        print(leaf)
        rrs = get_zone_rrs(leaf['id'])
        for rr in rrs:
            print(rr)
        print()
    print(len(leaves))
    exit()

    zones = get_zones()
    for zone in zones:
        print(zone)
    print(len(zones))
    zones = get_zones()
    for zone in zones:
        print(zone)
    print(len(zones))
    exit()

    rrs = get_rrs()
    for rr in rrs:
        print(rr)
    print(len(rrs))

    tlds = get_tlds()
    for tld in tlds:
        zones = get_zone_zones(tld['id'])
        print(f"Parent: {tld['name']}")
        for zone in zones:
            print(zone)
        print()


    for zone in zones:
        if zone['type'] == 'Zone':
            zid = zone['id']
            zname = zone['name']
            print(f'Zone ID Name: {zid} {zname}')
            data = get_zone_zones(zid)
            if len(data):
                for d in data:
                    pprint(d)
                    if d['type'] == 'Zone':
                        zz = d['id']
                        zns = get_zone_subzones(zz)
                        pprint(zns)
    Clt.logout()

if __name__ == '__main__':
    main()
