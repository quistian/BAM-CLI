#!/usr/bin/env python

import os
import sys
import json
import psycopg2

from time import sleep
from pprint import pprint
from dotenv import load_dotenv
from progressbar import progressbar

from bluecat_libraries.address_manager.api import Client
from bluecat_libraries.address_manager.api.models import APIEntity
from bluecat_libraries.address_manager.constants import ObjectType
from bluecat_libraries.address_manager.constants import AccessRightValues
from bluecat_libraries.http_client.exceptions import ErrorResponse

# local configuration constants, variables and initial values

Debug = True
Debug = False

V_Type = ObjectType.VIEW
Z_Type = ObjectType.ZONE
Cf_Type = ObjectType.CONFIGURATION
RR_Type = ObjectType.GENERIC_RECORD
Host_Type = ObjectType.HOST_RECORD
Ent_Type = ObjectType.ENTITY

Z_Props = {
        'deployable': 'true',
        'dynamicUpdate': 'false',
}

import config

'''

{'details': 'Missing parameter types, supported types:[HostRecord, '
            'HINFORecord, DHCP6Range, Configuration, Zone, IP4Address, '
            'IP6Address, AliasRecord, IP4Network, View, NAPTRRecord, '
            'IP6Network, TXTRecord, MACAddress, ExternalHostRecord, '
            'DHCP4Range, MXRecord, IP4Block, SRVRecord, GenericRecord, '
            'IP6Block]',
 'hint': '"selectCriteria":{"selector":"search", "types":"Configuration, View, '
         '...","keyword":"*"}',
 'issue': 'Missing required parameter'}

'''


# returns an iterator, not the data itself
def export_entities(start_id):
    selection = {
            "selector": "get_entitytree",
            "types": "Zone,GenericRecord,HostRecord,SRVRecord,TXTRecord,ExternalHostRecord",
            "startEntityId": start_id,
            "keyword": "*",
    }
    ent_iterator = Clnt.export_entities(select_criteria=selection, start=0, count=55000 )
    return ent_iterator

def import_entities():
    Clnt.import_entities()

def get_system_info():
    return Clnt.get_system_info()

def get_parent(eid):
    Clnt.get_parent(eid)


'''
Adds and Entity Object 
Returns the Id of the new entity

Parameters:
    parent_id (int): The parent ID of the object to be created
    entity (APIEntity): The entity to add, structured as such

    e.g.
        props = {
               "comments": "A solo A Resource Record",
               "type": "A"
               "rdata": "128.100.166.120",
        }
        entity = APIEntity(name='bozo', type='GenericRecord', properties=props)

'''

def add_entity(pid, ent):
    new_ent_id = Clnt.add_entity(parent_id=pid, entity=ent)
    return new_ent_id

def delete_entity(eid):
    Clnt.delete_entity(eid)

def delete_entity_with_optipons(eid):
    Clnt.delete_entity_with_optipons(eid)

'''
Gets a list of entities for a given parent object
Parameters:
    parent_id (int):
    type (str): the type of object to return
    start (int, optional); where on the list to begin
    count (int, optional): the maximum child objects to return, default is 10
    include_ha (bool, optional) include HA info from server. default is True
Returns a list of entities
'''

def get_entities(pid, typ):
    ents = Clnt.get_entities(parent_id=pid, type=typ, start=0, count=100)
    return ents

def get_entities_by_name(pid, nm, typ):
    return Clnt.get_entities_by_name(pid, nm, typ)

def get_entities_by_name_using_options(pid, nm, typ):
    return Clnt.get_entities_by_name_using_options(pid, nm, typ)

def get_entity_by_id(pid):
    return Clnt.get_entity_by_id(pid)

def get_entity_by_name(pid, nm, typ):
    return Clnt.get_entity_by_name(pid, nm, typ)

def update_entity(ent):
    return Clnt.update_entity(ent)

def update_entity_with_options(ent):
    return Clnt.update_entity_with_options(ent)

'''
add a zone at the top level
returns (int) the Id of the new zone

entity_id (int):
    The object ID of the parent object to which the zone is being added.
    For top-level domains, the parent object is a DNS view.
    For sub- zones, the parent object is a top-level domain or DNS zone.

absolute_name (str):
    The FQDN of the zone with no trailing dot.

properties (dict, optional):
    template - An optional network template association.
    deployable - A boolean value. Set to true to make the zone deployable. The default value is false.

These properties are supported by Address Manager v9.4.0:

    dynamicUpdate - A boolean value.
        If set to true, any resource records that are added, updated, or deleted
        within the zone will be selectively deployed to the associated primary DNS/DHCP Server of that zone.
        The default value is false.
    moveDottedResourceRecords - A boolean value.
        If set to false, existing dotted-name resource records matching the new subdomain will not be moved into the new subdomain.
        The default value is true.
'''

def add_zone(zone):
    try:
        ent_id = Clnt.add_zone(entity_id=config.ViewId, absolute_name=zone, properties=Z_Props)
        return ent_id
    except ErrorResponse as e:
        print(f'Error tryong to add zone {zone}: {e.message}')

'''
Gets a list of accessible zones of child objects for a given container_id value.
Returns a list of zone entities

container_id (int):
    The object ID of the container object.
    It can be the object ID of any object in the parent object hierarchy.
    The highest parent object is the configuration level.

options (dict_:
    A dictionary containing search options. It includes the following keys:
        hint: A string specifying the start of a zone name.
        overrideType: A string specifying the overriding of the zone. Must be a BAM Object value.
        accessRight: A string specifying the access right for the zone. Must be a BAM Access right value.

start (int, optional):
    Indicates where in the list of objects to start returning objects.
    The list begins at an index of 0. The default value is 0.

count (int, optional):
    Indicates the maximum number of child objects that this method will return.
    The maximum value is 10. The default value is 10.

'''

def get_zones_by_hint(zone):
    opts = {
        'hint': zone,
        'overrideType': Z_Type,
        'accessRight': AccessRightValues.ViewAccess,
    }
    ents = Clnt.get_zones_by_hint(container_id=config.ViewId, options=opts, start=0, count=10)
    return(ents)

# zone properties
# {'id': 100919, 'name': 'ca', 'type': 'Zone', 'properties': {'deployable': 'false', 'dynamicUpdate': 'false', 'absoluteName': 'ca'}}

# orgs table fields
# id  |  name   |  org |  hrid

def get_hr_nums():
    hrids = []
    load_dotenv(".psqlrc")

    host = os.environ.get('PGHOST')
    db = os.environ.get('PGDATABASE')
    uname = os.environ.get('PGUSER')
    pw = os.environ.get('PGPASSWORD')

    conn = psycopg2.connect(host=host, dbname=db, user=uname, password=pw)
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM orgs")
        for rec in cur:
            (i, nm, org, hrid) = rec
            if hrid is not None:
                hid = int(hrid)
                if hid < 1000 and hid not in hrids:
                    hrids.append(hid)
        return hrids
    except psycopg2.Error as e:
        print(f'Database error: {e.pgerror}')

#    conn = psycopg2.conn(dbname='obm', user='eng_ro_api', password='w7NDGTzm')

def get_azure_zones():
    azones = []
    for f in config.Azure_Zone_Files:
        fd = open(f)
        d = json.load(fd)
        for k in d:
            zname = d[k]['zoneName']
            if zname not in azones:
                azones.append(zname)
        fd.close()
    return azones

def gen_leaf_zones():
    leafs = []
    fd = open('hris-azure-subscriptions')
    d = json.load(fd)
    for n in d:
        for i in d[n]:
            leaf = f'{i:03}.{n}'
            leafs.append(leaf)
    return(leafs)

def print_leaf_zones():
    leaves = gen_leaf_zones()
    for leaf in leaves:
        print(leaf)

def create_leaf_zones():
    for leaf in gen_leaf_zones():
        add_zone_if_new(leaf)

def create_test_A_records():
    for zone in gen_leaf_zones():
        ip = '10.141.1.1'
        hris_num = zone.split('.')[0]
        hname = f'Q{hris_num}test'
        fqdn = f'{hname}.{zone}'
        add_A_RR(fqdn, ip)

def get_tlds(zones):
    tlds = []
    for z in zones:
        tks = z.split('.')
        if tks[-1] not in tlds:
            tlds.append(tks[-1])
    return tlds

def init():
    global Clnt

    ca_bundle = '/etc/ssl/Sectigo-AAA-chain.pem'
    load_dotenv("/home/russ/.bamrc")
    url = os.environ.get('BAM_API_URL')
    uname = os.environ.get('BAM_USER')
    pw = os.environ.get('BAM_PW')

    try:
        Clnt = Client(url, verify=ca_bundle)
        Clnt.login(uname, pw)
        conf_ent = Clnt.get_entity_by_name(config.RootId, config.Conf, Cf_Type)
        if Debug:
            pprint(conf_ent)
        config.ConfId = conf_ent['id']
        view_ent = Clnt.get_entity_by_name(config.ConfId, config.View, V_Type)
        if Debug:
            pprint(view_ent)
        config.ViewId = view_ent['id']
        return config.ViewId
    except ErrorResponse as e:
        print(f'Top Level Error: {e.message}')

def create_all_azure_zones():
    azones = get_azure_zones()
    cnt = len(azones)
    for i in progressbar(range(cnt)):
        azone = azones[i]
        add_zone_if_new(azone)

# create a Zone if it does not exist in a recursive way

def create_zone_in_an_iterative_manner(zone):
    toks = zone.split('.')
    toks.reverse()
    pid = config.ViewId
    for tok in toks:
        ents = Clnt.get_entities(pid, Z_Type, 0, 999)
        if Debug:
            pprint(ents)
        cid = pid
        for ent in ents:
            if ent['name'] == tok:
                cid = ent['id']
                break
        if cid == pid:
            apient = APIEntity(name=tok, type=Z_Type, properties=Z_Props)
            cid = Clnt.add_entity(pid, apient)
            e = Clnt.get_entity_by_id(cid)
            if Debug:
                print(f'Created zone {tok} with entity properties: {e}')
        pid = cid

def add_zone_if_new(zone):
    data = get_zones_by_hint(zone)
    if len(data) == 0:
        zone_id = add_zone(zone)
        if Debug:
            print(f'created zone: {zone} with id: {zone_id}')
    else:
        if Debug:
            print(f'DNS zone: {zone} already exists with entity properties: {data}')
        zone_id = data[0]['id']
    return zone_id

# return entity Id if zone exists

def zone_exists(zone):
    data = get_zones_by_hint(zone)
    if len(data):
        return data[0]['id']
    else:
        return False

def delete_zone(zone):
    deleted = False
    ents = get_entities(config.ViewId, Z_Type)
    for ent in ents:
        zid = ent['id']
        zname = ent['name']
        if zname == zone:
            deleted = True
            print(f'deleting TLD: {zname}')
            delete_entity(zid)
    if not deleted:
        print(f'zone {zone} has already been deleted or does not exist')

'''
When the record is to be added:
        props = {
               "comments": "A solo A Resource Record",
               "type": "A",
               "rdata": "128.100.166.120",
        }
        entity = APIEntity(name='bozo', type='GenericRecord', properties=props)

       GenericRecord entity data structure
       {'id': 163642, 'name': 'a', 'type': 'GenericRecord', 'properties': {'comments': 'A solo A Resource Record', 'absoluteName': 'a.b.c.d', 'type': 'A', 'rdata': '1.2.3.4'}}
'''


def add_A_RR(fqdn, ip):
    props = {
           'comments': 'A solo A Resource Record',
           'type': 'A',
           'rdata': ip,
    }
    toks = fqdn.split('.')
    hname = toks[0]
    a_rr_entity = APIEntity(name=hname, type='GenericRecord', properties=props)
    zone = '.'.join(toks[1:])
    zid = add_zone_if_new(zone)
    print(hname, zone, zid)
    ents = get_entities(zid, RR_Type)
    create_flag = True
    for ent in ents:
        if Debug:
            print(f'Generic Record Entity: {ent}')
        if ent['name'] == hname:
            props = ent['properties']
            if props['type'] == 'A' and props['rdata'] == ip:
                create_flag = False
                print(f'A Record with id: {ent["id"]} already exists')
    if create_flag:
        eid = add_entity(zid, a_rr_entity)
        if Debug:
            ent = get_entity_by_id(eid)
            print(f'Added A Record with id: {eid} {ent}')

def del_A_RR(fqdn, ip):
    props = {
           'type': 'A',
           'rdata': ip,
    }
    toks = fqdn.split('.')
    hname = toks[0]
    zone = '.'.join(toks[1:])
    zid = zone_exists(zone)
    if (zid):
        ents = get_entities(zid, RR_Type)
        for ent in ents:
            if ent['name'] == hname:
                props = ent['properties']
                if props['type'] == 'A' and props['rdata'] == ip:
                    if Debug:
                        print(f'Deleting Generic Record Entity: {ent}')
                    delete_entity(ent['id'])

def dump_dns_data():
    ents = get_entities(config.ViewId, Z_Type)
    for ent in ents:
        zid = ent['id']
        zname = ent['name']
        rrs = []
        for e in export_entities(zid):
            rrs.append(e)
        with open(f'{zname}-rrs.json', 'w') as rr_fd:
            json.dump(rrs, rr_fd, indent=4, sort_keys=True)

def main():
    init()
    print(Clnt.system_version)
    sysinfo = get_system_info()
    pprint(sysinfo)
#   add_A_RR('a.b.c.d', '2.3.4.5')
#   add_A_RR('aa.b.c.d', '1.2.3.5')
#   del_A_RR('a.b.c.d', '1.2.3.4')
#   del_A_RR('a.b.c.d', '2.3.4.5')
#   dump_dns_data()
#   export_entities()

    print_leaf_zones()
    Clnt.logout()
    exit()
    create_leaf_zones()
    create_test_A_records()

    exit()

    tlds = get_tlds(get_azure_zones())
    for tld in tlds:
        delete_zone(tld)
    print(f'Creating all azure zones')
    create_all_azure_zones()

if __name__ == '__main__':
    main()
