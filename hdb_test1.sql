
INSERT OR IGNORE INTO commands (name)
  VALUES ('echo'), ('gcc'), ('cmake');

INSERT OR IGNORE INTO args (args)
  VALUES ('hello world'), ('--std=c++11 foo.c'), ('..');

INSERT INTO execution (cmd_id, args_id, ex_date, hostname, tmux_session)
  VALUES (1, 1, strftime('%s', 'now'), 'DESKTOP-OFC0HOS', 'historydb');

SELECT * FROM commands;
SELECT * FROM execution;

SELECT execution.id, commands.name, args.args, datetime(execution.ex_date, 'unixepoch'), execution.tmux_session
FROM execution LEFT JOIN commands ON execution.cmd_id = commands.id
               LEFT JOIN args ON execution.args_id = args.id
               ;
