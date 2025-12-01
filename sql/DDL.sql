CREATE TABLE Member (
    MID SERIAL PRIMARY KEY,
    FULL_NAME TEXT NOT NULL,
    Date_Of_Birth DATE,
    Phone_Number TEXT,
    Email TEXT UNIQUE NOT NULL
);

CREATE TABLE Health_Metric (
    HMID SERIAL PRIMARY KEY,
    MID INT NOT NULL REFERENCES Member(MID) ON DELETE CASCADE,
    Measured_At TIMESTAMP DEFAULT NOW(),
    Weight_kg NUMERIC(5,2),
    Heart_BPM INT,
    Body_Fat_PCT NUMERIC(4,1)
);

CREATE TABLE Fitness_Goals (
    GID SERIAL PRIMARY KEY,
    MID INT NOT NULL REFERENCES Member(MID) ON DELETE CASCADE,
    Goal_Type TEXT NOT NULL,
    Target_Value NUMERIC(10,2),
    Created_At TIMESTAMP DEFAULT NOW(),
    Achieved_At TIMESTAMP
);

CREATE TABLE Trainer (
    TID SERIAL PRIMARY KEY,
    Full_Name TEXT NOT NULL,
    Email TEXT UNIQUE NOT NULL
);

CREATE TABLE Trainer_Availability (
    AID SERIAL PRIMARY KEY,
    TID INT NOT NULL REFERENCES Trainer(TID) ON DELETE CASCADE,
    Start_At TIMESTAMP NOT NULL,
    End_At   TIMESTAMP NOT NULL,
    CHECK (End_At > Start_At)
);

CREATE TABLE FitnessClass (
    CID SERIAL PRIMARY KEY,
    Title TEXT NOT NULL,
    Default_Duration_Min INT NOT NULL CHECK (Default_Duration_Min > 0)
);

CREATE TABLE Room (
    RID SERIAL PRIMARY KEY,
    Name TEXT UNIQUE NOT NULL,
    Capacity INT NOT NULL CHECK (Capacity > 0)
);

CREATE TABLE Scheduled_Class (
    SCID SERIAL PRIMARY KEY,
    CID INT NOT NULL REFERENCES FitnessClass(CID) ON DELETE CASCADE,
    TID INT NOT NULL REFERENCES Trainer(TID) ON DELETE CASCADE,
    RID INT NOT NULL REFERENCES Room(RID) ON DELETE CASCADE,
    Start_At TIMESTAMP NOT NULL,
    End_At TIMESTAMP NOT NULL,
    Capacity INT NOT NULL CHECK (Capacity > 0),
    CHECK (End_At > Start_At)
);

CREATE TABLE Class_Registration (
    CRID SERIAL PRIMARY KEY,
    MID INT NOT NULL REFERENCES Member(MID) ON DELETE CASCADE,
    SCID INT NOT NULL REFERENCES Scheduled_Class(SCID) ON DELETE CASCADE,
    Register_At TIMESTAMP DEFAULT NOW(),
    UNIQUE (MID, SCID)
);

--make sure that the availabilities of a trainer do not overlap
ALTER TABLE Trainer_Availability
ADD CONSTRAINT ex_trainer_availability_no_overlap
EXCLUDE USING gist (
    TID WITH =,
    tsrange(Start_At, End_At) WITH &&
);

CREATE INDEX idx_registration_member ON Class_Registration(MID);
CREATE INDEX idx_registration_scid ON Class_Registration(SCID);
CREATE INDEX idx_healthmetric_member_time ON Health_Metric(MID, Measured_At DESC);

--make sure that the class is not full when registering a new user
CREATE OR REPLACE FUNCTION check_class_capacity()
RETURNS TRIGGER AS $$
DECLARE
    current_count INT;
    class_cap INT;
BEGIN
    SELECT COUNT(*) INTO current_count
    FROM Class_Registration
    WHERE SCID = NEW.SCID;

    SELECT Capacity INTO class_cap
    FROM Scheduled_Class 
    WHERE SCID = NEW.SCID;

    IF current_count >= class_cap THEN
        RAISE EXCEPTION 'Class % is full', NEW.SCID;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_class_capacity
BEFORE INSERT ON Class_Registration
FOR EACH ROW 
EXECUTE FUNCTION check_class_capacity();

CREATE EXTENSION IF NOT EXISTS btree_gist;

--prevent a room from being used by two classes at the same time
ALTER TABLE Scheduled_Class
ADD CONSTRAINT ex_no_room_overlap
EXCLUDE USING gist (
    RID WITH =,
    tsrange(Start_At, End_At) WITH &&
);

--prevent a trainer from being scheduled for two classes at the same time
ALTER TABLE Scheduled_Class
ADD CONSTRAINT ex_no_trainer_overlap
EXCLUDE USING gist (
    TID WITH =,
    tsrange(Start_At, End_At) WITH &&
);

CREATE OR REPLACE VIEW v_member_dashboard AS
SELECT
    m.mid,
    m.full_name,
    m.email,

    (SELECT hm.Weight_kg
     FROM health_metric hm
     WHERE hm.mid = m.mid
     ORDER BY hm.measured_at DESC
     LIMIT 1) AS last_weight_kg,

     (SELECT hm.Heart_BPM
      FROM health_metric hm
      WHERE hm.mid = m.mid
      ORDER BY hm.measured_at DESC
      LIMIT 1) AS last_heart_bpm,

     (SELECT hm.body_fat_pct
      FROM health_metric hm
      WHERE hm.mid = m.mid
      ORDER BY hm.measured_at DESC
      LIMIT 1) AS last_body_fat_pct,

     (SELECT COUNT(*)
      FROM class_registration cr
      JOIN scheduled_class sc ON sc.scid = cr.scid
      WHERE cr.mid = m.mid
        AND sc.end_at < now()) AS total_classes_attended,
    
     (SELECT COUNT(*)
      FROM class_registration cr
      JOIN scheduled_class sc ON sc.scid = cr.scid
      WHERE cr.mid = m.mid
        AND sc.start_at >= now()
        AND sc.start_at < now() + INTERVAL '30 days') AS upcoming_30d_count
FROM member m;