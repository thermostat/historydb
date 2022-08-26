
CREATE TABLE execution (
       id INTEGER PRIMARY KEY,
       cmd_id INTEGER,
       args_id INTEGER,
       ex_date INTEGER,
       hostname TEXT,
       tmux_session TEXT,
       runtime REAL
);

CREATE TABLE commands (
       id INTEGER PRIMARY KEY,
       name TEXT UNIQUE
);

CREATE TABLE args (
       id INTEGER PRIMARY KEY,
       args TEXT UNIQUE
);
