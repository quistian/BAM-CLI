#!/usr/local/bin/python3 -tt

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import csv
import pybam
from pprint import pprint


def rr_exec(text):
    print('input:', text)
    command = text.split(' ')
    func = command[0]
    args = ','.join(command[1:])
    print('function:', func)
    print('args:', args)
    if func in functions:
#       functions[func](args)
        eval(func + '(' + args + ')')

def add_TXT_rr(fqdn, value, ttl):
    props = 'comments=None|'
    obj_id = pybam.add_TXT_Record(pybam.ViewId, fqdn, value, ttl, props)
    print(obj_id)

def add_A_rr(fqdn, value, ttl):
    props = 'comments=None|'
    obj_id = pybam.add_Generic_Record(pybam.ViewId, fqdn, 'A', value, ttl, props)
    print(obj_id)

def add_MX_rr(fqdn, value, ttl):
    props = 'comments=None|'
    mx = value.split()
    obj_id = pybam.add_MX_Record(pybam.ViewId, fqdn, mx[0], mx[1], ttl, props)
    print(obj_id)

functions = {
        'add_TXT_rr': add_TXT_rr,
        'add_A_rr': add_A_rr,
        'add_MX_rr': add_MX_rr,
}

def process_bulk_data(fname):
    fieldnames = ['action', 'fqdn', 'ttl', 'rr_type', 'value']
    with open(fname) as csv_file:
        data = csv.DictReader(csv_file, delimiter=',', fieldnames=fieldnames, skipinitialspace=True)
        for row in data:
            action = row['action']
            if action[0] == '#':
                continue
            row['fqdn'] = row['fqdn'].strip('.').lower()
            fqdn = row['fqdn']
            if 'uoft.ca' in row['fqdn']:
                if action == 'update':
                    update_rr(row)
                if action == 'add':
                    if pybam.Debug and pybam.is_zone(fqdn):
                        print('Adding RR at the zone level:', fqdn)
                    pybam.add_entity_rr(row)
                if action == 'delete':
                    delete_rr(row)
                if action == 'get':
                    id = get_rr(row)
                    pent = pybam.get_parent(id)
                    ent = pybam.get_entity_by_id(id)
                    print('child:', ent)
                    print('parent', pent)

#
# do a probe/get to see if a given RR exists in BAM
# if it does return its Entity ID otherwise return False
#

def get_rr(data):
    fqdn = data['fqdn']
    rr_type = data['rr_type']
    value =  data['value']
    id = object_find(fqdn, rr_type, value)
    return id


def object_find(fqdn, rr_type, value):
    id = 0
    if rr_type == 'MX':
        (priority, value) = value.split(' ')

    obj_type = pybam.RRTypeMap[rr_type]['obj_type']
    prop_key = pybam.RRTypeMap[rr_type]['prop_key']

    names = fqdn.split('.')
    tld = names.pop()
    tld_ent = pybam.get_entity_by_name(pybam.ViewId, tld, 'Zone')
    pid = tld_ent['id']
    pname = tld
    while (len(names)):
        name = names.pop()
        ent = pybam.get_entity_by_name(pid, name, 'Entity')
        obj_id = ent['id']
        obj_ent = pybam.get_entity_by_id(obj_id)
        if len(names) == 0:
            if obj_ent['type'] == 'Zone':
                print('fqdn', fqdn, 'is a Zone')
                pid = obj_id
            ents = pybam.get_entities(pid, obj_type, 0, 100)
            if len(ents):
                for ent in ents:
                    if 'properties' in ent and ent['properties'] is not None:
                        d = pybam.props2dict(ent['properties'])
                        if d['absoluteName'] == fqdn and value == d[prop_key]:
                            id = ent['id']
        pname = name
        pid = obj_id
    return id

'''

AliasRecord
HINFORecord
HOSTRecord
MXRecord
TXTRecord
    'id': 2519630, 'name': '', 'type': 'TXTRecord',
    'properties': 'comments=Zone Information|ttl=7600|absoluteName=yes.uoft.ca|txt=STOP GO|'}

'''

#
# now done by add/update/delete entity
#

def add_host(fqdn,ip,ttl):
    props = '|'
    val = pybam.add_host_record(fqdn, ip, ttl, props)
    return val


def add_RR_rr(data):
    fqdn = data['fqdn']
    rr_type = data['rr_type']
    obj_type = pybam.RRTypeMap[rr_type]['obj_type']
    rdata = data['value']
    ttl = data['ttl']
    props = 'comments=Place Holder|'

    val = pybam.add_resource_record(fqdn, obj_type, rdata, ttl, props)
    print(val)


#
# delete a given generic RR
#

def delete_rr(data):
    id = get_rr(data)
    if id:
        pybam.delete(id)
        print('Deleted RR associated with:', data)
    else:
        print('No RR associated with:', data)

def delete_rr_old(data):
    if pybam.Debug:
        print()
        print('input data:', data)
    fqdn = data['fqdn']
    rr_type = data['rr_type']
    value = data['value']
    obj_type = pybam.RRTypeMap[rr_type]['obj_type']
    prop_key = pybam.RRTypeMap[rr_type]['prop_key']
    ent = pybam.get_info_by_name(fqdn)
    if pybam.Debug:
        print('initial Entity:', ent)
    if ent['type'] == 'Zone':
        pid = ent['id']
        ents = pybam.get_entities(pid, rr_obj_type, 0, 100)
        for ent in ents:
            if ent['name'] == '':
                d = pybam.props2dict(ent['properties'])
                if d['type'] == rr_type and d['rdata'] == value:
                    if pybam.Debug:
                        print('deleting:', ent)
                    pybam.delete(ent['id'])


#
# Perform an update to a current RR
#


def update_rr(data):
    if pybam.Debug:
        print()
        print('input data', data)
    (value_old, value_new) =  data['value'].split(':')
    obj_id =  object_find(data['fqdn'], data['rr_type'], value_old)
    if obj_id:
        rr_type = data['rr_type']
        ttl = data['ttl']
        prop_key = pybam.RRTypeMap[rr_type]['prop_key']
        if rr_type ==  'MX':
            (priority, value) = value_new.split(' ')
            pybam.add_external_host(value)
        else:
            value = value_new
        if rr_type == 'CNAME':
            pybam.add_external_host(value)
        ent = pybam.get_entity_by_id(obj_id)
        if pybam.Debug:
            print('ent bef', ent)
        d = pybam.props2dict(ent['properties'])
        d[prop_key] = value
        d['ttl'] = ttl
        if rr_type  == 'MX':
            d['priority'] = priority
        ent['properties'] = pybam.dict2props(d)
        if pybam.Debug:
            print('ent aft:', ent)
        val = pybam.update_object(ent)
        print(val)
    else:
        print('Can not find RR')


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
    d = pybam.props2dict(props)
    ttl = int(d['ttl']) - 3600
    d['ttl'] = str(ttl) 
    props2 = pybam.dict2props(d)
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

#    sysinfo = pybam.get_system_info()
#    print('System Information:')
#    for item in sysinfo.split('|'):
#        print(item)

    process_bulk_data('update.txt')

#   test_search_functions()

    pybam.bam_logout()

    for i in [2520076, 2520077, 2519963]:
        ent = pybam.get_entity_by_id(i)
        print(i, ent)
    
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
