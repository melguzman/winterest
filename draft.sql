use mguzman2_db;

drop table if exists meeting;
drop table if exists icebreaker;
drop table if exists firstMatch;
drop table if exists bio;
drop table if exists classes;
drop table if exists genres;
drop table if exists Myers-Briggs;
drop table if exists loveLanguages;
drop table if exists favorites;
drop table if exists professionalInterests;
drop table if exists contact;
drop table if exists userAccount;
 
create table userAccount ( 
    wemail varchar(50) primary key,
    fname varchar(30),
    lname varchar(30),
    major varchar(50),
    year int unsigned,
    country varchar(50).
    state varchar(2),
    city varchar(50),
    onCampus enum("yes", "no")
    )
 
ENGINE = InnoDB;

create table contact (
    contactID int not null primary key,
    number int unsigned primary key,
    handle varchar(50),
    URL varchar(150),
    platform enum('facebook', 'instagram', 'whatsapp', 'text'),
    INDEX (contactID),
    foreign key (wemail) references userAccount(wemail)
        on update restrict
        on delete restrict
)

ENGINE = InnoDB;

create table professionalInterests (
    profInt int not null primary key,
    industry varchar(50),
    dream job varchar(50),
    INDEX (profInt),
    foreign key (wemail) references userAccount(wemail)
        on update restrict
        on delete restrict
)

ENGINE = InnoDB;

create table favorites (
    favoritesID int not null primary key,
    name varchar(50),
    type enum('album' 'song' 'artist' 'book' 'movie' 'tvshow' 'color' 'emoji' 'food' 'restaurant' 'game'),
    INDEX (favoritesID),
    foreign key (wemail) references userAccount(wemail)
        on update restrict
        on delete restrict
)

ENGINE = InnoDB;

create table loveLanguages (
    loveLangID int not null primary key,
    ranking int,
    type enum('affirmation' 'service' 'gift' 'time' 'physical'),
    INDEX (loveLangID),
    foreign key (wemail) references userAccount(wemail)
        on update restrict
        on delete restrict
)

ENGINE = InnoDB;

create table Myers-Briggs (
    myersBID int not null primary key,
    personality enum('analysts', 'diplomats', 'sentinels', 'explorers'),
    role varchar(15),
    rode varchar(6),
    INDEX (myersBID),
    foreign key (wemail) references userAccount(wemail)
        on update restrict
        on delete restrict
)

ENGINE = InnoDB;

create table genres (
    genresID int not null primary key,
    type enum(‘music’, ‘book’, ‘movie’, ‘tvshow’),
    name varchar(20),
    INDEX (genresID),
    foreign key (wemail) references userAccount(wemail)
        on update restrict
        on delete restrict
)

ENGINE = InnoDB;

create table classes (
    classesID int not null primary key,
    classCode varchar(8),
    INDEX (classesID),
    foreign key (wemail) references userAccount(wemail)
        on update restrict
        on delete restrict
)

ENGINE = InnoDB;

create table bio (
    bioID int not null primary key,
    bio varchar(200),
    INDEX (bioID),
    foreign key (wemail) references userAccount(wemail)
        on update restrict
        on delete restrict
)

ENGINE = InnoDB;

create table firstMatch (
    matchID int not null primary key,
    wemail varchar(50),
    wemailMatch varchar(50),
    INDEX (matchID),
    foreign key (wemail) references userAccount(wemail)
        on update restrict
        on delete restrict
)

ENGINE = InnoDB;

create table icebreaker (
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
    meetingID int not null primary key,
    time date,
    type varchar(30),
    wemailMatch varchar(50),
    location varchar(30),
    INDEX (meetingID),
    foreign key (wemail) references userAccount(wemail)
        on update restrict
        on delete restrict
)

ENGINE = InnoDB;
