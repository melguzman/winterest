use wellesleymatch_db;

drop table if exists matches;
drop table if exists matches_scored;
drop table if exists meeting;
drop table if exists icebreaker;
drop table if exists firstMatch;
drop table if exists bio;
drop table if exists loveLanguages;
drop table if exists favorites;
drop table if exists professionalInterests;
drop table if exists contact;
drop table if exists userAccount;
drop table if exists MBResults;

create table MBResults (
    MBCode varchar(6) not null primary key,
    personality enum('analysts', 'diplomats', 'sentinels', 'explorers'),
    role varchar(15),
    INDEX (role)
)
ENGINE = InnoDB;
 
create table userAccount ( 
    wemail char(8) not null primary key,
    password varchar(50),
    fname varchar(30),
    lname varchar(30),
    major varchar(50),
    year int unsigned,
    country varchar(50),
    state varchar(2),
    city varchar(50),
    onCampus enum("yes", "no"),
    MBCode varchar(6),

    foreign key (MBCode) references MBResults(MBCode)
        on update restrict
        on delete restrict
    )

ENGINE = InnoDB;

create table contact (
    wemail char(8) not null,
    phoneNumber int unsigned not null primary key,
    handle varchar(50),
    url varchar(150),
    platform enum('facebook', 'instagram', 'whatsapp', 'text'),
    INDEX (phoneNumber),
    foreign key (wemail) references userAccount(wemail)
        on update restrict
        on delete restrict
)

ENGINE = InnoDB;

create table professionalInterests (
    wemail char(8) not null,
    industry varchar(50),
    dreamJob varchar(50),
    INDEX (industry),
    foreign key (wemail) references userAccount(wemail)
        on update restrict
        on delete restrict
)

ENGINE = InnoDB;

create table favorites (
    wemail char(8) not null,
    name varchar(50),
    itemType enum('album', 'song', 'artist', 'book', 'movie',
        'tvshow', 'color', 'emoji', 'food', 'restaurant', 'game'),
    INDEX (itemType),
    foreign key (wemail) references userAccount(wemail)
        on update restrict
        on delete restrict
)

ENGINE = InnoDB;

create table loveLanguages (
    wemail char(8) not null,
    langNum enum("1", "2", "3"),
    language enum('affirmation', 'service', 'gift', 'time', 'physical'),
    foreign key (wemail) references userAccount(wemail)
        on update restrict
        on delete restrict
)

ENGINE = InnoDB;

create table bio (
    wemail char(8) not null,
    bio varchar(200),
    foreign key (wemail) references userAccount(wemail)
        on update restrict
        on delete restrict
)

ENGINE = InnoDB;

create table firstMatch (
    wemail char(8) not null,
    matchID int not null primary key,
    wemailMatch varchar(50),
    INDEX (matchID),
    foreign key (wemail) references userAccount(wemail)
        on update restrict
        on delete restrict
)

ENGINE = InnoDB;

create table icebreaker (
    wemail char(8) not null,
    icebreakerID int not null primary key,
    question varchar(50),
    answer varchar(70),
    INDEX (icebreakerID),
    foreign key (wemail) references userAccount(wemail)
        on update restrict
        on delete restrict
)

ENGINE = InnoDB;

create table meeting (
    wemail char(8) not null,
    meetingID int not null primary key,
    time date,
    itemType varchar(30),
    wemailMatch varchar(50),
    location varchar(30),
    INDEX (meetingID),
    foreign key (wemail) references userAccount(wemail)
        on update restrict
        on delete restrict
)

ENGINE = InnoDB;

create table matches_scored (
    wemail char(8), -- person who is logged in
    wemail2 char(8), -- wemail of second person, unmatched yet
    score int not null,
    isMatched char(3), -- value of yes/no depending on if this pair is matched or not
    INDEX (wemail),
    foreign key (wemail) references userAccount(wemail)
        on update restrict
        on delete restrict
)

ENGINE = InnoDB;

