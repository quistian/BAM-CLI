#!/usr/bin/env python3

import os
import sys
import json
import csv

from pprint import pprint
from dotenv import load_dotenv
from bluecat_libraries.address_manager.apiv2 import Client, MediaType, BAMV2ErrorResponse

load_dotenv("/home/russ/.bamrc")

ca_bundle = '/etc/ssl/Sectigo-AAA-chain.pem'
verfy = False
verfy = ca_bundle
View_Id = '0'

url = os.environ.get('BAM_APIv2_URL')
uname = os.environ.get('BAM_DEV_USER')
pw = os.environ.get('BAM_DEV_PW')

# Retrieve the configurations. Request the data as per BAM's default content type.

def init():
    client = Client(url, verify=ca_bundle)
    data = client.login(uname, pw)
    if client.is_authenticated:
        print(f'BAM auth: {client.auth}')
        return client
    else:
        print(f'Could not authenticate: {data}')
        exit()

#        params = {"fields": "id,name"},

def get_confs(clt):
    resp = clt.http_get(
        "/configurations",
        headers = {"Accept": MediaType.JSON},
    )
    return resp['data']

def get_conf(clt, idy):
    resp = clt.http_get(
        f"/configurations/{idy}",
        headers = {"Accept": MediaType.JSON},
    )
    return resp['data']

#        headers = {"Accept": MediaType.JSON},
def get_views(clt):
    resp = clt.http_get(
        "/views",
        headers = {'Accept': MediaType.JSON},
    )
    return resp['data']

#        headers = {"Accept": MediaType.JSON},
def get_view(clt, idy):
    resp = clt.http_get(
        f"/views/{idy}",
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

def get_view_id(clt, conf_name, view_name):
    views = get_views(clt)
    for view in views:
        if view['configuration']['name'] == conf_name and view['name'] == view_name:
            return view['id']
    return 0

def get_tld_zones(clt, vid):
    zones = clt.http_get(
        f"/views/{vid}/zones",
        headers = {"Accept": MediaType.JSON},
        )
    return zones['data']

def get_zone_subzones(clt, zid):
    parms = {'fields': 'embed(resourceRecords.addresses)'}
    rrs = clt.http_get(
            f"/zones/{zid}/zones",
            params = parms,
    )
    return rrs['data']

def main():
    client = init()

    View_Id = get_view_id(client, 'Test', 'Azure')
    zones = get_tld_zones(client, View_Id)
    for zone in zones:
        if zone['type'] == 'Zone':
            zid = zone['id']
            zname = zone['name']
            print(f'Zone ID Name: {zid} {zname}')
            data = get_zone_subzones(client, zid)
            if len(data):
                for d in data:
                    pprint(d)
                    if d['type'] == 'Zone':
                        zz = d['id']
                        zns = get_zone_subzones(client,zz)
                        pprint(zns)

    client.logout()

if __name__ == '__main__':
    main()
