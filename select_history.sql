SELECT execution.id, commands.name, args.args, datetime(execution.ex_date, 'unixepoch'), execution.tmux_session
FROM execution LEFT JOIN commands ON execution.cmd_id = commands.id
               LEFT JOIN args ON execution.args_id = args.id
               ;
