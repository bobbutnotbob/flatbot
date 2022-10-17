CREATE TABLE IF NOT EXISTS [Users] ( 
	[UserId] INTEGER NOT NULL PRIMARY KEY, 
	[JobId] INTEGER NULL  
); 
/*CREATE TABLE [Payments] (
    [Id] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    [OwedBy] INTEGER NOT NULL,
    [OwedTo] INTEGER NOT NULL,
    [Amount] FLOAT NOT NULL,
    FOREIGN KEY(OwedBy) REFERENCES Users(UserId)
    FOREIGN KEY(OwedTo) REFERENCES Users(UserId)
);*/
CREATE TABLE IF NOT EXISTS [Payments] (
    [MessageId] INTEGER PRIMARY KEY NOT NULL,
    [Amount] FLOAT NOT NULL,
    [Description] TEXT NULL,
    [RequestedBy] INTEGER NOT NULL,
    [RequestedFrom] TEXT NOT NULL,
    [UnpaidBy] TEXT NOT NULL,
    FOREIGN KEY(RequestedBy) REFERENCES Users(UserId)
);
CREATE TABLE IF NOT EXISTS [Archive] (
    [MessageId] INTEGER PRIMARY KEY NOT NULL,
    [Amount] FLOAT NOT NULL,
    [Description] TEXT NULL,
    [RequestedBy] INTEGER NOT NULL,
    [RequestedFrom] TEXT NOT NULL,
    FOREIGN KEY(RequestedBy) REFERENCES Users(UserId)
);