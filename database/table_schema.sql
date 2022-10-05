CREATE TABLE [Users] ( 
	[UserId] INTEGER NOT NULL PRIMARY KEY, 
	[JobId] INTEGER NULL  
); 
CREATE TABLE [Payments] (
    [Id] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    [OwedBy] INTEGER NOT NULL,
    [OwedTo] INTEGER NOT NULL,
    [Amount] FLOAT NOT NULL,
    FOREIGN KEY(OwedBy) REFERENCES Users(UserId)
    FOREIGN KEY(OwedTo) REFERENCES Users(UserId)
);
CREATE TABLE [Outstanding] (
    [Id] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    [Amount] FLOAT NOT NULL,
    [RequestedBy] INTEGER NOT NULL,
    [PaidBy] TEXT NULL,
    FOREIGN KEY(RequestedBy) REFERENCES Users(UserId)
);