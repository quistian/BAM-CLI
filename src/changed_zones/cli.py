#!/usr/bin/env python

"""Code to see what BlueCat data has changed"""

import json
import sys
import sqlite3
from click import Choice, Context, argument, group, option, pass_context, echo

from contextlib import closing
from datetime import datetime, timezone, timedelta
from rich import print
from tqdm import tqdm

from changed_zones import v2api

DB = "bc_dns_delta.db"
Changed_zones = []
Transaction_ids = []
Now = datetime.now(timezone.utc)
ISO_now = Now.strftime("%Y-%m-%dT%H:%M:%SZ")
ISO_then = '1970-01-01T00:00:00Z'

@group()
@option(
        "--verbose/--no-verbose",
        default=False,
        help="Show extra information"
)
@option(
        "--debug/--no-debug",
        default=False,
        help="Help runtime code with debugging info",
        )
@pass_context
def run(ctx: Context, verbose, debug):
    ctx.obj = dict()
    ctx.obj["DEBUG"] = debug
    ctx.obj["VERBOSE"] = verbose
    v2api.Debug = debug
    if debug:
        echo(f"action: {ctx.invoked_subcommand}")
    v2api.basic_auth()

@run.command()
@pass_context
@option(
    "-s", "--seconds", "secs",
    default=0,
    type=int,
    help="Number of seconds to offset in the past",
)
@option(
    "-m", "--minute", "mins",
    default=0,
    type=int,
    help="Number of minutes to offset in the past",
)
@option(
    "-h", "--hours", "hrs",
    default=0,
    type=int,
    help="Number of hours to offset in the past",
)
@option(
    "-d", "--days", "days",
    default=0,
    type=int,
    help="Number of days to offset in the past",
)
@option(
    "-w", "--weeks", "wks",
    default=0,
    type=int,
    help="Number of wks to offset in the past",
)
@option(
    "-m", "--months", "mths",
    default=0,
    type=int,
    help="Number of months to offset in the past",
)
@option(
    "-y", "--years", "yrs",
    default=0,
    type=int,
    help="Number of years to offset in the past",
)
def offset(ctx, secs, mins, hrs, days, wks, mths, yrs):
    global ISO_then
    years = timedelta(days=365*yrs)
    months = timedelta(days=30*mths)
    delta = timedelta(
        weeks = wks,
        days = days,
        hours = hrs,
        minutes = mins,
        seconds = secs,
        microseconds = 0
    )
    then = Now - years - months - delta
    ISO_then = then.strftime("%Y-%m-%dT%H:%M:%SZ")
    print(ISO_now, ISO_then)


@run.command()
@pass_context
@option(
    "--write",
    is_flag=True
)
def from_last_change(ctx, write):
    """ lets go! """
    if ctx.obj["DEBUG"]:
        print("Running from the last time a change was made")
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
    Now = datetime.now(timezone.utc)
    tau_now = Now.strftime("%Y-%m-%dT%H:%M:%SZ")
    return tau_now


if __name__ == "__main__":
    run()
