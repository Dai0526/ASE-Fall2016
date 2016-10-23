drop table if exists user;
create table user (
  user_id integer primary key autoincrement,
  username text not null,
  email text not null,
  pw_hash text not null
);

drop table if exists follower;
create table follower (
  who_id integer,
  whom_id integer
);

drop table if exists message;
create table message (
  message_id integer primary key autoincrement,
  author_id integer not null,
  text text not null,
  pub_date integer
);

drop table if exists `group`;
create table `group` (
  group_id integer primary key autoincrement,
  groupname text not null,
  description text
);

drop table if exists groupmember;
create table groupmember (
  group_id integer,
  member_id integer
);