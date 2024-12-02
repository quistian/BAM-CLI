-- DROP TABLE IF EXISTS transactions;
CREATE TABLE transactions (
    trans_id INTEGER PRIMARY KEY,
    act_id INTEGER UNIQUE,
    trans_dt TEXT,
    trans_cmt TEXT,
    trans_desc TEXT,
    trans_op TEXT,
    trans_type TEXT,
    trans_user TEXT
);
-- DROP TABLE IF EXISTS last_run;
CREATE TABLE last_run (
    run_id INTEGER PRIMARY KEY,
    run_isodate TEXT,
    run_unixtime INTEGER
);
-- DROP TABLE IF EXISTS log;
CREATE TABLE log (
    log_id INTEGER PRIMARY KEY,
    log_isodate TEXT NOT NULL,  -- ISO 8601 date format with milliseconds E.g. 2024-11-21T14:21:53+00:00
    log_unixtime INTEGER,       -- seconds since the epoch
    log_transaction_ids TEXT,   -- CSV representation of the transaction ids which occurred since the last scan
    log_changed_zones TEXT      -- CSV representation of changed zones since last scan
);
-- DROP TABLE IF EXISTS operations;
CREATE TABLE operations (
    ops_id INTEGER PRIMARY KEY,
    act_id INTEGER,
    rr_id INTEGER,
    op_type TEXT,
    bc_type TEXT,
    rr_comment TEXT,
    rr_hname TEXT,
    rr_fqdn TEXT,
    rr_type TEXT,
    rr_value TEXT,
    rr_ttl INTEGER
);
