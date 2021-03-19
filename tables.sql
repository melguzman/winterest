use sk1_db;
--use wellesleymatch_db;

drop table if exists meeting;
drop table if exists icebreaker;
drop table if exists firstMatch;
drop table if exists bio;
drop table if exists genres;
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
    wemail varchar(50) not null primary key,
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
    wemail varchar(50) not null,
    phoneNumber int unsigned not null primary key,
    handle varchar(50),
    URL varchar(150),
    platform enum('facebook', 'instagram', 'whatsapp', 'text'),
    INDEX (phoneNumber),
    foreign key (wemail) references userAccount(wemail)
        on update restrict
        on delete restrict
)

ENGINE = InnoDB;

create table professionalInterests (
    wemail varchar(50) not null,
    industry varchar(50),
    dreamJob varchar(50),
    INDEX (industry),
    foreign key (wemail) references userAccount(wemail)
        on update restrict
        on delete restrict
)

ENGINE = InnoDB;

create table favorites (
    wemail varchar(50) not null,
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
    wemail varchar(50) not null,
    langNum enum("1", "2", "3"),
    language enum('affirmation', 'service', 'gift', 'time', 'physical'),
    foreign key (wemail) references userAccount(wemail)
        on update restrict
        on delete restrict
)

ENGINE = InnoDB;

create table genres (
    wemail varchar(50) not null,
    genresID int not null primary key,
    itemType enum('music', 'book', 'movie', 'tvshow'),
    name varchar(20),
    INDEX (genresID),
    foreign key (wemail) references userAccount(wemail)
        on update restrict
        on delete restrict
)

ENGINE = InnoDB;

create table bio (
    wemail varchar(50) not null,
    bioID int not null primary key,
    bio varchar(200),
    INDEX (bioID),
    foreign key (wemail) references userAccount(wemail)
        on update restrict
        on delete restrict
)

ENGINE = InnoDB;

create table firstMatch (
    wemail varchar(50) not null,
    matchID int not null primary key,
    wemailMatch varchar(50),
    INDEX (matchID),
    foreign key (wemail) references userAccount(wemail)
        on update restrict
        on delete restrict
)

ENGINE = InnoDB;

create table icebreaker (
    wemail varchar(50) not null,
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
    wemail varchar(50) not null,
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
