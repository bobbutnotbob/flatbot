CREATE TABLE [Users] ( 
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
CREATE TABLE [Payments] (
    [MessageId] INTEGER PRIMARY KEY NOT NULL,
    [Amount] FLOAT NOT NULL,
    [Description] TEXT NULL,
    [RequestedBy] INTEGER NOT NULL,
    [UnpaidBy] TEXT NOT NULL,
    [PaidBy] TEXT NULL,
    FOREIGN KEY(RequestedBy) REFERENCES Users(UserId)
);