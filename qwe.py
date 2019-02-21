#!/usr/local/bin/python3 -tt

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import csv
import pybam
from pprint import pprint

def process_bulk_data(fname):
    fieldnames = ['action', 'fqdn', 'ttl', 'rr_type', 'value']
    with open(fname) as csv_file:
        data = csv.DictReader(csv_file, delimiter=',', fieldnames=fieldnames, skipinitialspace=True)
        for row in data:
            row['fqdn'] = row['fqdn'].strip('.').lower()
            action = row['action']
            if action == 'update':
                if 'athletics' in row['fqdn']:
                    update_rr(row)

def update_rr(data):
    pprint(data)
    fqdn = data['fqdn']
    ent = pybam.get_info_by_name(fqdn)
    pprint(ent)
    pid = ent['pid']
    if ent['type'] == 'Zone':
        key = fqdn.split('.')[0]
        vars = pybam.search_by_category(key, 'RESOURCE_RECORD', 0, 5)
        pprint(vars)
#        vals = pybam.search_by_object_types(key, 'GenericRecord', 0, 5)
#        pprint(vals)
    data = pybam.get_entity_by_id(2443015)
    pprint(data)


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
    for id in [2200891, 2203565, 2217649, 2217650, 2512206, 2512207, 251697]:
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
        vals = pybam.get_parent(objid)
        print('child id', objid)
        print('parent object',vals)
    
    print()
    for nm in ['goofy.zulu.org', 'frodo.utoronto.ca']:
        pid = pybam.get_pid_by_name(nm)
        print(nm, 'has a parent id of', pid)
    
    print()
    for nm in ['goofy.zulu.org', 'frodo.utoronto.ca']:
        id = pybam.get_id_by_name(nm)
        pinfo = pybam.get_parent(id)
        parent = pybam.parent_name(nm)
        print('Parent info for', parent, pinfo)


# Tests for Searching for and Retrieving Entities

def test_custom_search():
    filters = ['ttl=86400']
    vars = pybam.custom_search(filters, 'MXRecord', 0, 25)
    pprint(vars)

    filters = ['recordType=A', 'rdata=128.100.103*']
    vars = pybam.custom_search(filters, 'GenericRecord', 0, 15)
    pprint(vars)


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

# Takes a property list as a dictionary e.g. 
# {'ttl': '86400', 'absoluteName': 'fwsm-tabu.bkup.utoronto.ca', 'addresses': '128.100.96.158', 'reverseRecord': 'true'}
# and returns it as a string equivalent:
#   ttl=86400|absoluteName=fwsm-tabu.bkup.utoronto.ca|addresses=128.100.96.158|reverseRecord=true|

def dict2props(d):
    props = []
    for k,v in d.items():
        props.append('='.join([k,v]))
    return '|'.join(props) + '|'

def test_rr_functions():

    ip = '128.100.103.123'
    props = 'reverseRecord=false|'
    ttl = '3600'
    zone = 'bozo.math.utoronto.ca'
    fqdn = 'hamster' + '.' + zone

    print(fqdn,ip,ttl,props)

    vals = pybam.add_host_record(fqdn, '128.100.103.123', 3600, props)
    pprint(vals)

def test_zone_functions():
    dot = '.'
    
    for z in ['zulu.org', 'watusi.zulu.org']:
        val = pybam.is_zone(z)
        print(val)
        val = pybam.delete_zone(z)
        val = pybam.add_zone_generic(z)
        print(val)

    print('Generic zone add')
    for z in ['yes.uoft.ca', 'no.uoft.ca']:
        ent = pybam.add_zone_generic(z)
        print(ent)
        val = pybam.get_info_by_name(z)
        print(val)
    
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
    id = pybam.get_id_by_name('goofy.ring.frodo.utoronto.ca')
    print(id)


def test_category_search():
    entities = pybam.search_by_category('utoronto', pybam.Categories['resourceRecords'], 0, 20)
    pprint(entities)
    entities = pybam.search_by_category('math', pybam.Categories['resourceRecords'], 0, 20)
    pprint(entities)
    entities = pybam.search_by_category('128', pybam.Categories['IP4Objects'], 0, 20)
    pprint(entities)
    entities = pybam.search_by_category('cs.utoronto.ca', pybam.Categories['all'], 0, 20)
    pprint(entities)

# {'id': 2460953,
# 'name': 'fwsm-tabu',
#  'properties': 'ttl=79200|absoluteName=fwsm-tabu.bkup.utoronto.ca|addresses=128.100.96.158|reverseRecord=true|'

def test_object_type_search():
    types = 'View,Zone,HostRecord,GenericRecord'
    types = 'Zone,GenericRecord'
    vars = pybam.search_by_object_types('*e*', types, 0, 100)
    for var in vars:
        if var['type'] == 'GenericRecord':
            pprint(var['properties'])

def test_search_functions():
    print('Custom Search')
    test_custom_search()
#    print('\nSearch by Category')
#   test_category_search()
#   print('\nSearch by Object Type')
#   test_object_type_search()

# {'id': 2460953,
#  'name': 'fwsm-tabu',
#  'properties': 'ttl=86400|absoluteName=fwsm-tabu.bkup.utoronto.ca|addresses=128.100.96.158|reverseRecord=true|',
#  'type': 'HostRecord'}

def test_update():
    print('Update')
    id = 2460953
    ent = pybam.get_entity_by_id(id)
    props = ent['properties']
    d = props2dict(props)
    ttl = int(d['ttl']) - 3600
    d['ttl'] = str(ttl) 
    props2 = dict2props(d)
    ent['properties'] = props2
    pybam.update_object(ent)
    print('View ID:', ViewId)
    print('Configuration ID:', ConfigId)

# test get_linked, linked and unlink

def test_linked():
    fqdn = 'utoronto.ca'
    id = pybam.get_id_by_name(fqdn)
    vals = pybam.get_linked_entities(id, 'RecordWithLink', 0, 10)
    pprint(vals)

def test_ipam():
    parentid = 2205986
    cidr = '1.2/16'
    properties = 'locationCode=CA TOR UOT'
    vals = pybam.add_IP4_block_by_CIDR(parentid, cidr, properties)
    pprint(vals)

def qwe():
    types = 'View,Zone,HostRecord,GenericRecord'
    types = 'Configuration,View'
    vars = pybam.search_by_object_types('test', types, 0, 100)
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

    pybam.bam_init()

    sysinfo = pybam.get_system_info()
    print('System Information:')
    for item in sysinfo.split('|'):
        print(item)

    process_bulk_data('update.txt')

#   test_search_functions()

    pybam.bam_logout()
    
    ents = pybam.get_host_records_by_hint('hint=^ra|retrieveFields=true', start=0, count=1)
    pprint(ents)
    ents = pybam.get_host_records_by_hint('hint=*x*', start=0, count=10)
    pprint(ents)
    sys.exit()

    test_linked()
    test_update()
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
    print(hostinfo)
    action = 'MAKE_DHCP_rESERVED'
    properties = 'name=frodo|locationCode=CA TOR UOFT'
    res = assign_ip4Address(
            conf_id, ipaddr, macaddr, hostinfo, action, properties
            )
    pprint(res)

    fqdn = 'utoronto.ca'
    obj_id = pybam.get_id_by_name(fqdn)
    par_id = pybam.get_pid_by_id(obj_id)
    print(par_id)

    parent_id = Fqdn2Id(fqdn)
    print(parent_id)

    pid = Fqdn2Id('utoronto.ca')
    vars = pybam.get_entities(pid, 'HostRecord', 0, 10)
    pprint(vars)


    host_info = pybam.add_resource_record(fqdn, 'HostRecord', ip, ttl, props)
    print('\nAdd Host Response:')
    pprint(host_info)

    host_info = pybam.add_host_record(fqdn, ip, ttl, props)
    print('\nAdd Host Response:')
    pprint(host_info)

    obj_id = pybam.get_id_by_name('ca')
    print(obj_id)
    print()

    obj_id = pybam.get_id_by_name('utoronto.ca')
    print(obj_id)
    print()

    obj_id = pybam.get_id_by_name('bozo.math.utoronto.ca')
    print(obj_id)

    host_info = pybam.get_host_info(view_id, 'mail.utoronto.ca')
    pprint(host_info)

    zone_info = pybam.get_entity_by_name(zone_info['id'], 'utoronto', 'Zone')
    pprint(zone_info)

    host_info = pybam.get_entity_by_name(zone_info['id'], 'bozo', 'HostRecord')
    print('\nHost info for ' + fqdn + ':')
    pprint(host_info)

    response = pybam.delete(host_id)
    pprint(response)

    response = pybam.bam_logout()
    pprint(response)

if __name__ == "__main__":
    main()
