CREATE TABLE ig_account(
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    abbrv TEXT,
    last_update TEXT
);
%GO%

CREATE TABLE follow (
    id INTEGER PRIMARY KEY,
    username TEXT,
    acc_id INTEGER,
    date TEXT,
    follower BOOLEAN,
    following BOOLEAN,
    FOREIGN KEY (acc_id) REFERENCES ig_account (id)
)
%GO%

CREATE TABLE last_follows(
    username TEXT,
    acc_id INTEGER,
    last_following_id INTEGER,
    last_follower_id INTEGER,
    PRIMARY KEY (acc_id, username),
    FOREIGN KEY (acc_id) REFERENCES ig_account (id),
    FOREIGN KEY (last_following_id) REFERENCES following (id)
    FOREIGN KEY (last_follower_id) REFERENCES following (id)

);
%GO%

CREATE TABLE preferences (
    id INTEGER PRIMARY KEY, 
    default_acc_id INTEGER, 
    progress_dir TEXT, 
    data_dir TEXT, 
    ig_url TEXT,
    FOREIGN KEY (default_acc_id) REFERENCES ig_account (id)
);
%GO%