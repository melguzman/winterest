use wellesleymatch_db;

drop table if exists meeting;
drop table if exists userpass;
drop table if exists picfile;
drop table if exists matches_scored;
drop table if exists firstMatch;
drop table if exists bio;
drop table if exists loveLanguages;
drop table if exists favorites;
drop table if exists contact;
drop table if exists userAccount;
 
create table userAccount ( 
    wemail varchar(20) not null primary key,
    fname varchar(30),
    lname varchar(30),
    major varchar(50),
    year int unsigned,
    country varchar(50),
    state varchar(2),
    city varchar(50),
    onCampus enum("yes", "no"),
    pronouns varchar(10)
)

ENGINE = InnoDB;

create table contact (
    contactID int not null AUTO_INCREMENT,
    wemail varchar(20) not null,
    phoneNumber varchar(20),
    url varchar(150),
    platform enum('facebook', 'instagram', 'whatsapp', 'text'),
    primary key (contactID),
    foreign key (wemail) references userAccount(wemail)
        on update cascade
        on delete cascade
)

ENGINE = InnoDB;

create table favorites (
    wemail varchar(20) not null,
    name varchar(50),
    itemType enum('album', 'song', 'artist', 'book', 'movie',
        'tvshow', 'color', 'emoji', 'food', 'restaurant', 'game'),
    INDEX (itemType),
    foreign key (wemail) references userAccount(wemail)
        on update cascade
        on delete cascade
)

ENGINE = InnoDB;

create table loveLanguages (
    wemail varchar(20) not null,
    langNum enum("1", "2", "3"),
    language enum('affirmation', 'service', 'gift', 'time', 'physical'),
    foreign key (wemail) references userAccount(wemail)
        on update cascade
        on delete cascade
)

ENGINE = InnoDB;

create table bio (
    wemail varchar(20) not null,
    bio varchar(200),
    foreign key (wemail) references userAccount(wemail)
        on update cascade
        on delete cascade
)

ENGINE = InnoDB;

create table firstMatch (
    wemail varchar(20) not null,
    matchID int not null primary key,
    wemailMatch varchar(50),
    INDEX (matchID),
    foreign key (wemail) references userAccount(wemail)
        on update cascade
        on delete cascade
)

ENGINE = InnoDB;

create table matches_scored (
    wemail varchar(20), -- person who is logged in
    wemail2 char(8), -- wemail of second person, unmatched yet
    score int,
    isMatched char(3), -- value of yes/no depending on if this pair is matched or not
    INDEX (wemail),
    foreign key (wemail) references userAccount(wemail)
        on update cascade
        on delete cascade
)

ENGINE = InnoDB;

create table picfile (
    wemail varchar(20) not null,
    filename varchar(50),
    foreign key (wemail) references userAccount(wemail) 
        on delete cascade 
        on update cascade
)

ENGINE = InnoDB;

create table userpass(
       wemail varchar(20) not null,
       hashed varchar(60),
       unique(wemail),
       index(wemail),
       foreign key (wemail) references userAccount(wemail) 
        on delete restrict 
        on update restrict 
)

ENGINE = InnoDB;

create table meeting(
       meetingID int not null AUTO_INCREMENT,
       wemail varchar(20) not null,
       wemail2 varchar(20) not null,
       what varchar(20),
       type enum("Remote", "In-Person"),
       location varchar(100),
       time varchar(20),
       date varchar(30),
       notes varchar(100),
       INDEX (meetingID),
       foreign key (wemail) references userAccount(wemail) 
        on delete cascade 
        on update cascade
)

ENGINE = InnoDB;

