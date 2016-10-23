DROP TABLE if exists user;
CREATE TABLE user (
  user_id integer PRIMARY KEY autoincrement,
  username text NOT NULL,
  email text NOT NULL,
  pw_hash text NOT NULL
);

DROP TABLE if exists follower;
CREATE TABLE follower (
  who_id integer,
  whom_id integer
);

DROP TABLE if exists message;
CREATE TABLE message (
  message_id integer PRIMARY KEY autoincrement,
  author_id integer NOT NULL,
  text text NOT NULL,
  pub_date integer
);

DROP TABLE if exists `group`;
CREATE TABLE `group` (
  group_id integer PRIMARY KEY autoincrement,
  groupname text NOT NULL,
  description text
);

DROP TABLE if exists manages;
CREATE TABLE manages (
  group_id integer,
  manager_id integer,
  FOREIGN KEY(group_id) REFERENCES 'group'(group_id),
  FOREIGN KEY(user_id) REFERENCES user(user_id) 
);

DROP TABLE if exists in;
CREATE TABLE in(	
  group_id integer,
  member_id integer,
  FOREIGN KEY(group_id) REFERENCES 'group'(group_id),
  FOREIGN KEY(user_id) REFERENCES user(user_id)
);