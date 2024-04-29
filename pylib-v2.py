#!/usr/bin/env python3

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

Ca_bundle = '/etc/ssl/Sectigo-AAA-chain.pem'
Verfy = False
Verfy = Ca_bundle
Header = {"Accept": MediaType.JSON}

EndPoint = os.environ.get('BAM_ENDPOINT')
Url = f'https://{EndPoint}/api/v2/'
Uname = os.environ.get('BAM_USER')
Pw = os.environ.get('BAM_PW')

Conf = os.environ.get('BAM_CONF')
View = os.environ.get('BAM_VIEW')
View_Id = 0
Conf_Id = 0

# Retrieve the configurations. Request the data as per BAM's default content type.

def init():
    global Clt

    Clt = Client(Url, verify=Ca_bundle)
    data = Clt.login(Uname, Pw)
    if Clt.is_authenticated:
        print(f'BAM auth: {Clt.auth}')
        print(f'BAM url: {Clt.bam_url}')
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

def get_tld_zones(vid):
    path = f'/views/{vid}/zones'
    zones = Clt.http_get(
        path,
        headers = Header,
        )
    return zones['data']

def get_zone_subzones(zid):
    path = f'/zones/{zid}/zones'
    parms = {'fields': 'embed(resourceRecords.addresses)'}
    rrs = Clt.http_get(
            path,
            params = parms,
    )
    return rrs['data']

def get_rrs():
    path = '/resourceRecords'
    parms = {
        'fields': 'id,name,configuration,ttl,absoluteName,recordType,rdata',
        'filter': f'configuration.id:eq({Conf_Id})',
        'limit': 100,
        'total': True,
    }
    resp = Clt.http_get(
        path,
        headers = Header,
        params = parms,
    )
    data = resp['data']
    pprint(data)
    return data

def main():
    global Conf_Id, View_Id

    init() #sets Clt
    Conf_Id = get_conf_id()
    View_Id = get_view_id()

    print(f'Conf ID: {Conf_Id}')
    print(f'View ID: {View_Id}')
    rrs = get_rrs()
    exit()

    zones = get_tld_zones(View_Id)
    for zone in zones:
        pprint(zone)

    for zone in zones:
        if zone['type'] == 'Zone':
            zid = zone['id']
            zname = zone['name']
            print(f'Zone ID Name: {zid} {zname}')
            data = get_zone_subzones(zid)
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
