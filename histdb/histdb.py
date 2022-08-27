
import sqlite3
import shlex, platform
import time, subprocess, os, re

SQLCMD_INSERT_COMMAND = """
INSERT OR IGNORE INTO commands (name)
  VALUES (?);
"""

SQLCMD_SELECT_COMMAND_ID = """
SELECT id FROM commands
WHERE name = ?;
"""


SQLCMD_INSERT_ARGS = """
INSERT OR IGNORE INTO args (args)
  VALUES (?);
"""


SQLCMD_SELECT_ARGS_ID = """
SELECT id FROM args
WHERE args = ?;
"""

SQLCMD_INSERT_EX = """
INSERT INTO execution (cmd_id, args_id, ex_date, hostname, tmux_session)
  VALUES (?, ?, ?, ?, ?);

"""

SQLCMD_SELECT_ALL_CMDS = """
SELECT execution.id, commands.name, args.args, datetime(execution.ex_date, 'unixepoch'), execution.tmux_session
FROM execution LEFT JOIN commands ON execution.cmd_id = commands.id
               LEFT JOIN args ON execution.args_id = args.id
               ORDER BY execution.ex_date ASC;
"""

###########################################################################
#
# SQLite DB insertion
#
###########################################################################

def cmd_to_name_and_args(cmd):
    try:
        cmdname, args = cmd.split(' ', maxsplit=1)
    except ValueError as v:
        cmdname = cmd
        args = ''
    return cmdname, args

def get_id_cmd(cmdname, sqlcur):
    sqlcmd = SQLCMD_INSERT_COMMAND
    sqlcur.execute(sqlcmd, (cmdname,))
    res = sqlcur.execute(SQLCMD_SELECT_COMMAND_ID, (cmdname,))
    row = res.fetchone()
    return row[0]


def get_id_args(cmdname, sqlcur):
    sqlcmd = SQLCMD_INSERT_ARGS
    sqlcur.execute(sqlcmd, (cmdname,))
    res = sqlcur.execute(SQLCMD_SELECT_ARGS_ID, (cmdname,))
    row = res.fetchone()
    return row[0]


def add_cmd(sqlcur, cmd, host=None,
            timestamp=None, tmux_session=None, runtime=None):
    """
    Add a command to the database.
    """
    cmdname, args = cmd_to_name_and_args(cmd)
    if cmdname == "":
        return
    cmdid = get_id_cmd(cmdname, sqlcur)
    argid = get_id_args(args, sqlcur)

    if host == None:
        host = platform.node()

    if tmux_session == None and ('TMUX' in os.environ):
        r = subprocess.run("tmux display-message -p '#S:#W'",
                           capture_output=True, shell=True)
        if r.returncode == 0:
            tmux_session = r.stdout.decode('ascii').strip()
    if timestamp == None:
        timestamp = int(time.time())
    #cmd_id, args_id, ex_date, hostname, tmux_session
    sqlcur.execute(SQLCMD_INSERT_EX,
                   (cmdid,  argid, timestamp, host, tmux_session))


###########################################################################
#
# Bash history parse
#
###########################################################################

def parse_bash_history(sqlcur, fd):
    """
    Assumes a HISTTIMEFORMAT='%s ' time formatting
    """
    regex = re.compile(r'\d+\s+(\d+)\s+(.+)')

    for line in fd:
        res = regex.search(line)
        if res:
            timestamp = res.groups()[0]
            cmd = res.groups()[1]
            add_cmd(sqlcur, cmd, timestamp=timestamp)


def populate_history(sqlcur, fname):
    res = sqlcur.execute(SQLCMD_SELECT_ALL_CMDS)
    rows = res.fetchall()
    fd = open(fname, 'w')
    for row in rows:
        print("{} {}".format(row[1], row[2]), file=fd)

    
if __name__ == '__main__':
    con = sqlite3.connect('test.db')
    cur = con.cursor()
    #add_cmd(cur, 'echo hello from histdb.py')
    #fd = open('history.txt', 'r')
    #parse_bash_history(cur, fd)
    populate_history(cur, '/tmp/dwhist')
    con.commit()
    con.close()
