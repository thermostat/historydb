
import sqlite3
import shlex, platform
import time, subprocess, os

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

def cmd_to_name_and_args(cmd):
    cmdparse = shlex.split(cmd)
    cmdname = cmdparse[0]
    args = shlex.join(cmdparse[1:])
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


def add_cmd(sqlcur, cmd, host=None, timestamp=None, tmux_session=None, runtime=None):
    cmdname, args = cmd_to_name_and_args(cmd)
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
    sqlcur.execute(SQLCMD_INSERT_EX, (cmdid,  argid, timestamp, host, tmux_session))


if __name__ == '__main__':
    con = sqlite3.connect('test.db')
    cur = con.cursor()
    add_cmd(cur, 'echo hello from histdb.py')
    con.commit()
    con.close()
