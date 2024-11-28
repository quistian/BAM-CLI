#!/usr/bin/env python

import getopt
import json
import sys
import sqlite3

import v2api

from contextlib import closing
from datetime import datetime, date, time, timezone, timedelta
from pprint import pprint


Db = 'bc_dns_delta.db'
Changed_zones = list()
Transaction_ids = list()

'''
           cur.execute("INSERT or IGNORE INTO last_run (id, isodate, unixtime) VALUES (1, ?, ?)",  (isodate, unixtime))
           cur.execute("UPDATE last_run SET isodate = ?, unixtime = ? WHERE id = 1", (isodate, unixtime))
'''

def update_last_run():
    idx = 1
    dt = datetime.now(timezone.utc)
    unixtime = int(dt.timestamp())
    isodate = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    with closing(sqlite3.connect(Db)) as con:
        with closing(con.cursor()) as cur:
            sql = '''
            INSERT into last_run (id, isodate, unixtime) VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET isodate = excluded.isodate, unixtime = excluded.unixtime;
            '''
            cur.execute(sql, (idx, isodate, unixtime))
            con.commit()

def update_log():
    dt = datetime.now(timezone.utc)
    unixtime = int(dt.timestamp())
    isodate = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    tids = ''
    zones = ''
    if len(Transaction_ids):
        tids = json.dumps(Transaction_ids)
    if len(Changed_zones):
        zones = json.dumps(Changed_zones)
    with closing(sqlite3.connect(Db)) as con:
        with closing(con.cursor()) as cur:
            sql = '''
                INSERT into log (isodate,unixtime,transaction_ids,changed_zones) VALUES (?,?,?,?);
            '''
            cur.execute(sql, (isodate,unixtime,tids,zones))
            con.commit()

'''
 {'comment': None,
 'creationDateTime': '2024-11-19T19:09:47Z',
 'description': 'Generic Record was added',
 'id': 63263,
 'operation': 'ADD_GENERIC_RECORD',
 'transactionType': 'ADD',
 'type': 'Transaction',
 'user': {'_links': {'self': {'href': '/api/v2/users/108726'}},
          'id': 108726,
          'name': 'sutherl4',
          'type': 'User'}}
'''

def update_transactions(act):
    with closing(sqlite3.connect(Db)) as con:
        with closing(con.cursor()) as cur:
            sql = '''
            INSERT OR IGNORE INTO transactions (act_id, datetime, description, operation, user)
            VALUES (?, ?, ?, ?, ?)
            '''
            cur.execute(sql, (act['id'], act['creationDateTime'],act['description'],act['operation'],act['user']['name']))
            con.commit()

'''

operations:
[
{'fieldUpdates': [{'name': 'name', 'previousValue': 'q000_aaa', 'value': None},
                   {'name': 'comments', 'previousValue': 'RPS', 'value': None},
                   {'name': 'recordType', 'previousValue': 'A', 'value': None},
                   {'name': 'rdata',
                    'previousValue': '10.141.1.22',
                    'value': None},
                   {'name': 'ttl', 'previousValue': None, 'value': None},
                   {'name': 'absoluteName',
                    'previousValue': 'q000_aaa.privatelink_openai_azure_com.000',
                    'value': None},
                   {'name': 'dynamic', 'previousValue': 'No', 'value': None}],
  'operationType': 'DELETE',
  'resourceId': 167100,
  'resourceType': 'GenericRecord'},

 {'fieldUpdates': [{'name': 'name', 'previousValue': 'q000_qwe', 'value': None},
                   {'name': 'comments', 'previousValue': None, 'value': None},
                   {'name': 'recordType', 'previousValue': 'A', 'value': None},
                   {'name': 'rdata',
                    'previousValue': '10.141.11.33',
                    'value': None},
                   {'name': 'ttl', 'previousValue': None, 'value': None},
                   {'name': 'absoluteName',
                    'previousValue': 'q000_qwe.privatelink_openai_azure_com.000',
                    'value': None},
                   {'name': 'dynamic', 'previousValue': 'No', 'value': None}],
  'operationType': 'DELETE',
  'resourceId': 167102,
  'resourceType': 'GenericRecord'},

 {'fieldUpdates': [
     {'name': 'name', 'previousValue': 'q000_ccc', 'value': None},
     {'name': 'comments', 'previousValue': None, 'value': None},
     {'name': 'recordType', 'previousValue': 'A', 'value': None},
     {'name': 'rdata', 'previousValue': '10.141.22.33', 'value': None},
     {'name': 'ttl', 'previousValue': None, 'value': None},
     {'name': 'absoluteName', 'previousValue': 'q000_ccc.privatelink_openai_azure_com.000', 'value': None},
     {'name': 'dynamic', 'previousValue': 'No', 'value': None}
     ],
  'operationType': 'DELETE',
  'resourceId': 167101,
  'resourceType': 'GenericRecord'}
]

'''

def update_operations(act_id, ops):
    global Changed_zones
    global Transaction_ids

    Transaction_ids.append(act_id)
    op_inserts = list()
    for op in ops:
        fupdates = op['fieldUpdates']
        rr_id = op['resourceId']
        bc_type = op['resourceType']
        op_type = op['operationType']
        if op_type == 'DELETE':
            key = 'previousValue'
        else:
            key = 'value'
        for field in fupdates:
            rr_comment = None
            nm = field['name']
            if nm == 'name':
                rr_hname = field[key]
            if nm == 'comments':
                rr_comment = field[key]
            if nm == 'ttl':
                rr_ttl = field[key]
            if nm == 'absoluteName':
                rr_fqdn = field[key]
            if bc_type == 'GenericRecord':
                if nm == 'recordType':
                    rr_type = field[key]
                if nm == 'rdata':
                    rr_value = field[key]
            if bc_type == 'AliasRecord':
                if nm == 'linkedRecord':
                    rr_value = field[key]
                rr_type = 'CNAME'
        op_inserts.append((act_id,rr_id,op_type,bc_type,rr_comment,rr_hname,rr_fqdn,rr_type,rr_value,rr_ttl))
        toks = rr_fqdn.split('.')
        zone = '.'.join(toks[-2:])
        if zone not in Changed_zones:
            Changed_zones.append(zone)
    with closing(sqlite3.connect(Db)) as con:
        with closing(con.cursor()) as cur:
 #           (act_id,rr_id,op_type,bc_type,rr_comment,rr_hname,rr_fqdn,rr_type,rr_value,rr_ttl)
            sql = 'INSERT INTO operations (act_id,rr_id,op_type,bc_type,rr_comment,rr_hname,rr_fqdn,rr_type,rr_value,rr_ttl) VALUES (?,?,?,?,?,?,?,?,?,?)' 
            if Debug:
                print(f'update_operations: sql query: {sql}')
                print(op_inserts)
            cur.executemany(sql, op_inserts)
        con.commit()

def fetch_last_run():
    with closing(sqlite3.connect(Db)) as con:
        with closing(con.cursor()) as cur:
            sql = "SELECT isodate from last_run WHERE id = 1"
            row = cur.execute(sql).fetchone()
            con.commit()
    return row[0]

def get_isodate_now():
    tau_now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return tau_now

def main():
    global Debug

    Debug = False
    arglist= sys.argv[1:]
#options
    opts = 'hdvq'
# longer options
    long_opts = ['help', 'debug', 'verbose', 'quiet']
    try:
        args, vals = getopt.getopt(arglist, opts, long_opts)
        for cur_arg,cur_val in args:
            if cur_arg in ['-h', '--help']:
                print('This is a holding area for help information')
                exit()
            elif cur_arg in ['-d', '--debug']:
                Debug = True
            elif cur_arg in ['-v', '--verbose']:
                Debug = True
            elif cur_arg in ['-q', '--quiet']:
                Debug = False
    except getopt.error as err:
        print(str(err))
        exit()

    v2api.Debug = Debug

    v2api.basic_auth()
    then = fetch_last_run()
    now = get_isodate_now()
    all_acts = v2api.get_all_transactions(then,now)
    pprint(all_acts)
    tactions = v2api.get_rr_transactions(then, now)
    for action in tactions:
        if Debug:
            pprint(action)
        update_transactions(action)
        ops = v2api.get_transactions_operations(action['id'])
        if Debug:
            print(f'action id: {action["id"]}')
            print(f'operations:')
            pprint(ops)
        update_operations(action['id'],ops)
    update_last_run()
    update_log()
    if len(Changed_zones):
        print(Changed_zones)
    exit()

if __name__ == '__main__':
    main()
