DROP DATABASE IF EXISTS samMarkSports;

CREATE DATABASE samMarkSports;

GRANT ALL PRIVILEGES ON samMarkSports.* to mark@localhost IDENTIFIED BY 'hud';

USE samMarkSports;

CREATE TABLE `User` (
    uid INTEGER AUTO_INCREMENT NOT NULL,
    name VARCHAR(128),
    email VARCHAR(128),
    password VARCHAR(128),
    PRIMARY KEY (uid)
);

CREATE TABLE `Coach` (
    uid INTEGER NOT NULL,
    salary DOUBLE,
    PRIMARY KEY (uid),
    FOREIGN KEY (uid) REFERENCES User (uid)
        ON DELETE CASCADE
);

CREATE TABLE `Athlete` (
    uid INTEGER NOT NULL,
    height DOUBLE,
    weight DOUBLE,
    PRIMARY KEY (uid),
    FOREIGN KEY (uid) REFERENCES User (uid)
        ON DELETE CASCADE
);

CREATE TABLE `TeamMascot` (
    name VARCHAR(128),
    mascot VARCHAR(128),
    PRIMARY KEY (name)
);

CREATE TABLE `Team` (
    tid INTEGER NOT NULL,
    name VARCHAR(128) NOT NULL,
    PRIMARY KEY (tid),
    FOREIGN KEY (name) REFERENCES TeamMascot (name)
        ON DELETE NO ACTION
);

CREATE TABLE `SportSeason` (
    name VARCHAR(64),
    season VARCHAR(6),
    PRIMARY KEY (name)
);

CREATE TABLE `Sport` (
    sid INTEGER AUTO_INCREMENT NOT NULL,
    name VARCHAR(64),
    PRIMARY KEY (sid),
    FOREIGN KEY (name) REFERENCES SportSeason (name)
        ON DELETE NO ACTION
);

CREATE TABLE `Workout` (
    wid INTEGER AUTO_INCREMENT NOT NULL,
    date_assigned DATETIME,
    uid INTEGER NOT NULL,
    PRIMARY KEY (wid),
    FOREIGN KEY (uid) REFERENCES Coach (uid)
        ON DELETE NO ACTION
);

CREATE TABLE `Exercise` (
    eid INTEGER AUTO_INCREMENT NOT NULL,
    name VARCHAR(128),
    PRIMARY KEY (eid)
);

CREATE TABLE `coaches` (
    uid INTEGER NOT NULL,
    tid INTEGER NOT NULL,
    since DATE,
    PRIMARY KEY (uid, tid),
    FOREIGN KEY (uid) REFERENCES Coach (uid)
        ON DELETE NO ACTION,
    FOREIGN KEY (tid) REFERENCES Team (tid)
        ON DELETE NO ACTION
);

CREATE TABLE `plays` (
    sid INTEGER NOT NULL,
    tid INTEGER NOT NULL,
    PRIMARY KEY (sid, tid),
    FOREIGN KEY (sid) REFERENCES Sport (sid)
        ON DELETE NO ACTION,
    FOREIGN KEY (tid) REFERENCES Team (tid)
        ON DELETE NO ACTION
);

CREATE TABLE `member_of` (
    uid INTEGER NOT NULL,
    tid INTEGER NOT NULL,
    position VARCHAR(10),
    number INTEGER,
    PRIMARY KEY (uid, tid),
    FOREIGN KEY (uid) REFERENCES Athlete (uid)
        ON DELETE NO ACTION,
    FOREIGN KEY (tid) REFERENCES Team (tid)
        ON DELETE NO ACTION
);

CREATE TABLE `consists_of` (
    wid INTEGER,
    eid INTEGER NOT NULL,
    sets INTEGER,
    reps INTEGER,
    PRIMARY KEY (wid, eid),
    FOREIGN KEY (wid) REFERENCES Workout (wid)
        ON DELETE NO ACTION,
    FOREIGN KEY (eid) REFERENCES Exercise (eid)
        ON DELETE NO ACTION
); 

CREATE TABLE `does` (
    wid INTEGER,
    uid INTEGER,
    date_done DATETIME,
    PRIMARY KEY (wid, uid),
    FOREIGN KEY (wid) REFERENCES Workout (wid)
        ON DELETE NO ACTION,
    FOREIGN KEY (uid) REFERENCES Athlete (uid)
        ON DELETE NO ACTION
); 


CREATE TABLE `performance` (
    eid INTEGER,
    uid INTEGER,
    date_performed DATETIME,
    reps_performed INTEGER,
    max_weight DOUBLE,
    PRIMARY KEY (eid, uid, date_performed, reps_performed),
    FOREIGN KEY (eid) REFERENCES Exercise (eid)
        ON DELETE NO ACTION,
    FOREIGN KEY (uid) REFERENCES Athlete (uid)
        ON DELETE NO ACTION
); 
