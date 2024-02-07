CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities (
    Time date,
    Username varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

CREATE TABLE Patients (
	Username varchar(255),
	Salt BINARY(16),
	Hash BINARY(16),
	PRIMARY KEY (Username)
);
	
CREATE TABLE Appointments (
	id_num int IDENTITY(1,1),
	Time date,
	User_caregiver varchar(255) REFERENCES Caregivers,
	User_patient varchar(255) UNIQUE REFERENCES Patients,
	Vaccine varchar(255) REFERENCES Vaccines,
	PRIMARY KEY (id_num)
);
	
