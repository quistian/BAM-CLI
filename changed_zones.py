#!/usr/bin/env python

"""Code to see what BlueCat data has changed"""

import json
import sys
import sqlite3
import argparse

from contextlib import closing
from datetime import datetime, timezone
from rich import print
from tqdm import tqdm

import v2api

DB = "bc_dns_delta.db"
Changed_zones = []
Transaction_ids = []


def update_last_change():
    """ update last change to be now """
    idx = 1
    dt = datetime.now(timezone.utc)
    unixtime = int(dt.timestamp())
    isodate = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    with closing(sqlite3.connect(DB)) as con:
        with closing(con.cursor()) as cur:
            sql = """
            INSERT into last_change (run_id, last_change_isodate, last_change_unixtime) VALUES (?, ?, ?)
            ON CONFLICT(run_id) DO UPDATE SET last_change_isodate = excluded.last_change_isodate, last_change_unixtime = excluded.last_change_unixtime;
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
        if Debug:
            print(op)
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
            if Debug:
                print(f"update_operations: sql query: {sql}")
                print(op_inserts)
            cur.executemany(sql, op_inserts)
        con.commit()


def fetch_last_change():
    Tau0 = '2024-12-17T12:00:00Z'
    """gets the last time stamp from the last run."""
    with closing(sqlite3.connect(DB)) as con:
        with closing(con.cursor()) as cur:
            sql = "SELECT last_change_isodate from last_change WHERE run_id = 1"
            row = cur.execute(sql).fetchone()
            con.commit()
    if row is not None:
        return row[0]
    else:
        return Tau0


def get_isodate_now():
    """get the current ISO date and time Zulu."""
    tau_now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return tau_now


def main():
    """ lets go! """
    global Debug

    """
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
                Debug = True
            elif cur_arg in ["-v", "--verbose"]:
                Debug = True
            elif cur_arg in ["-q", "--quiet"]:
                Debug = False
    except getopt.error as err:
        print(str(err))
        sys.exit()
    """

    parser = argparse.ArgumentParser(
        prog='changed_zones.py',
        description='Probes the BC database to find out which RRs have \
        changed since the last time the program was run',
        epilog='That is all folks',
    )

    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    parser.add_argument('-c', '--count') # optional value
    parser.add_argument('-d', '--debug', help='show data to assist in debugging', action='store_true') # on or off flag
    parser.add_argument('--start', help='optional ISO date start time', type=str)
    parser.add_argument('--stop',  help='optional ISO date stop time', type=str)

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', help='increase the verbosity of the output', action='store_true')
    group.add_argument('-q', '--quiet', help='make sure there is minimal output', action='store_true')

    subparsers = parser.add_subparsers(help='sub command help')
    parser_offset = subparsers.add_parser('offset', help='offset subcommand help')
    parser_offset.add_argument('-s', '--seconds', type=int, default=0, help='number of seconds offset from now in the past')
    parser_offset.add_argument('-m', '--minutes', type=int, default=0, help='number of minutes offset from now in the past')
    parser_offset.add_argument('-H', '--hours', type=int, default=0, help='number of hours offset from now in the past')
    parser_offset.add_argument('-d', '--days', type=int, default=0, help='number of days offset from now in the past')
    parser_offset.add_argument('-M', '--months', type=int, default=0, help='number of months offset from now in the past')
    parser_offset.add_argument('-y', '--years', type=int, default=0, help='number of years offset from now in the past')

    args = parser.parse_args()

    Debug = None
    if args.debug:
        Debug = 1
    if args.quiet:
        Debug = False
    elif args.verbose:
        Debug = True

    offset = 0
    offset += args.seconds
    offset += args.minutes * 60
    offset += args.hours * 3600
    offset += args.days * 86400
    offset += args.months * 2592000
    offset += args.years * 946080000 

    v2api.Debug = Debug

    print(Debug)
    print(offset)
    exit()

    v2api.basic_auth()
    v2api.get_system_version()
    then = fetch_last_change()
    now = get_isodate_now()
    # all_acts = v2api.get_all_transactions(then, now)
    # if Debug:
    #     print(all_acts)
    tactions = v2api.get_rr_transactions(then, now)
    for action in tqdm(tactions, leave=False):
        if Debug:
            print(action)
        update_transactions(action)
        ops = v2api.get_transactions_operations(action["id"])
        if Debug:
            print(f'action id: {action["id"]}')
            print("operations:")
            print(ops)
        update_operations(action["id"], ops)
    if Changed_zones:
        update_last_change()
        print(Changed_zones)
    update_log()


if __name__ == "__main__":
    main()
