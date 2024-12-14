#!/usr/bin/env python

"""Code to see what BlueCat data has changed"""

import json
import sys
import sqlite3
import getopt

from contextlib import closing
from datetime import datetime, timezone
from pprint import pprint
from tqdm import tqdm

import v2api

DB = "bc_dns_delta.db"
Changed_zones = []
Transaction_ids = []

DEBUG = False

"""
cur.execute(
"INSERT or IGNORE INTO last_run (run_id, run_isodate, run_unixtime) VALUES (1, ?, ?)", 
(isodate, unixtime)
)
cur.execute(
"UPDATE last_run SET run_isodate = ?, run_unixtime = ?  WHERE run_id = 1",
(isodate, unixtime)
)
"""


def update_last_run():
    """write the current time into the database."""
    idx = 1
    dt = datetime.now(timezone.utc)
    unixtime = int(dt.timestamp())
    isodate = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    with closing(sqlite3.connect(DB)) as con:
        with closing(con.cursor()) as cur:
            sql = """
            INSERT into last_run (run_id, run_isodate, run_unixtime) VALUES (?, ?, ?)
            ON CONFLICT(run_id) DO UPDATE SET run_isodate = excluded.run_isodate, run_unixtime = excluded.run_unixtime;
            """
            cur.execute(sql, (idx, isodate, unixtime))
            con.commit()


def update_log():
    """update the log table with all the new entries for future ref."""
    dt = datetime.now(timezone.utc)
    unixtime = int(dt.timestamp())
    isodate = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    tids = ""
    zones = ""
    if Transaction_ids:
        tids = json.dumps(Transaction_ids)
    if Changed_zones:
        zones = json.dumps(Changed_zones)
    with closing(sqlite3.connect(DB)) as con:
        with closing(con.cursor()) as cur:
            sql = """
                INSERT into log (log_isodate,log_unixtime,log_transaction_ids,log_changed_zones) VALUES (?,?,?,?);
            """
            cur.execute(sql, (isodate, unixtime, tids, zones))
            con.commit()


def update_transactions(act):
    """
     Update all the new transactions.
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
    """
    with closing(sqlite3.connect(DB)) as con:
        with closing(con.cursor()) as cur:
            sql = """
            INSERT OR IGNORE INTO transactions (act_id, trans_dt, trans_desc, trans_op, trans_user)
            VALUES (?, ?, ?, ?, ?)
            """
            cur.execute(
                sql,
                (
                    act["id"],
                    act["creationDateTime"],
                    act["description"],
                    act["operation"],
                    act["user"]["name"],
                ),
            )
            con.commit()


def update_operations(act_id, ops):
    """ Update the operations table with all new actions.
    Operations data structure:
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
      ...
    ]
    """
    global Changed_zones
    global Transaction_ids

    Transaction_ids.append(act_id)
    op_inserts = []
    for op in ops:
        fupdates = op["fieldUpdates"]
        rr_id = op["resourceId"]
        bc_type = op["resourceType"]
        op_type = op["operationType"]
        if op_type == "DELETE":
            key = "previousValue"
        else:
            key = "value"
        for field in fupdates:
            rr_comment = None
            nm = field["name"]
            if nm == "name":
                rr_hname = field[key]
            elif nm == "comments":
                rr_comment = field[key]
            elif nm == "ttl":
                rr_ttl = field[key]
            elif nm == "absoluteName":
                rr_fqdn = field[key]
            elif bc_type == "GenericRecord":
                if nm == "recordType":
                    rr_type = field[key]
                elif nm == "rdata":
                    rr_value = field[key]
            elif bc_type == "AliasRecord":
                if nm == "linkedRecord":
                    rr_value = field[key]
                rr_type = "CNAME"
        data = (
            act_id,
            rr_id,
            op_type,
            bc_type,
            rr_comment,
            rr_hname,
            rr_fqdn,
            rr_type,
            rr_value,
            rr_ttl,
        )
        op_inserts.append(data)
        toks = rr_fqdn.split(".")
        zone = ".".join(toks[-2:])
        if zone not in Changed_zones:
            Changed_zones.append(zone)
    with closing(sqlite3.connect(DB)) as con:
        with closing(con.cursor()) as cur:
            #           (act_id,rr_id,op_type,bc_type,rr_comment,rr_hname,rr_fqdn,rr_type,rr_value,rr_ttl)
            sql = """
            INSERT INTO operations
            (act_id,rr_id,op_type,bc_type,rr_comment,rr_hname,rr_fqdn,rr_type,rr_value,rr_ttl)
            VALUES (?,?,?,?,?,?,?,?,?,?) 
            """
            if DEBUG:
                print(f"update_operations: sql query: {sql}")
                print(op_inserts)
            cur.executemany(sql, op_inserts)
        con.commit()


def fetch_last_run():
    """gets the last time stamp from the last run."""
    with closing(sqlite3.connect(DB)) as con:
        with closing(con.cursor()) as cur:
            sql = "SELECT run_isodate from last_run WHERE run_id = 1"
            row = cur.execute(sql).fetchone()
            con.commit()
    return row[0]


def get_isodate_now():
    """get the current ISO date and time Zulu."""
    tau_now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return tau_now


def main():
    """lets go!"""
    global DEBUG

    arglist = sys.argv[1:]
    opts = "hdvq"
    long_opts = ["help", "debug", "verbose", "quiet"]
    try:
        args, vals = getopt.getopt(arglist, opts, long_opts)
        for cur_arg, cur_val in args:
            if cur_arg in ["-h", "--help"]:
                print("This is a holding area for help information")
                sys.exit()
            elif cur_arg in ["-d", "--debug"]:
                DEBUG = True
            elif cur_arg in ["-v", "--verbose"]:
                DEBUG = True
            elif cur_arg in ["-q", "--quiet"]:
                DEBUG = False
    except getopt.error as err:
        print(str(err))
        sys.exit()

    v2api.Debug = DEBUG

    v2api.basic_auth()
    v2api.get_system_version()
    then = fetch_last_run()
    now = get_isodate_now()
    # all_acts = v2api.get_all_transactions(then, now)
    # if DEBUG:
    #     pprint(all_acts)
    tactions = v2api.get_rr_transactions(then, now)
    for action in tqdm(tactions, leave=False):
        if DEBUG:
            pprint(action)
        update_transactions(action)
        ops = v2api.get_transactions_operations(action["id"])
        if DEBUG:
            print(f'action id: {action["id"]}')
            print("operations:")
            pprint(ops)
        update_operations(action["id"], ops)
    update_last_run()
    update_log()
    if Changed_zones:
        print(Changed_zones)


if __name__ == "__main__":
    main()
