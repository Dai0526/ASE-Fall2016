drop table if exists entries;

create table entries(
    id int not NULL auto_increment,
    title text not NULL,
    `text` text not NULL,
    Primary key(id)
    );