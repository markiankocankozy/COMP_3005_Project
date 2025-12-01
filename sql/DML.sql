INSERT INTO Member (full_name, date_of_birth, phone_number, email) VALUES
('Alice Johnson', '1998-04-12', '613-555-1234', 'alice@example.com'),
('Bob Smith', '1995-09-30', '416-555-9876', 'bob@example.com'),
('Charlie Brown', '2000-01-15', '905-555-4567', 'charlie@example.com');

INSERT INTO Trainer (full_name, email) VALUES
('John Miller', 'john.miller@gympro.com'),
('Sarah Lee', 'sarah.lee@gympro.com'),
('Andy Smith', 'andy.smith@gympro.com');

INSERT INTO Room (name, capacity) VALUES
('Studio A', 20),
('Studio B', 15),
('Yoga Room', 10);

INSERT INTO FitnessClass (title, default_duration_min) VALUES
('Yoga Beginner', 60),
('HIIT Blast', 45),
('Strength Training', 75);

INSERT INTO Trainer_Availability (tid, start_at, end_at) VALUES
(1, '2025-12-01 09:00', '2025-12-01 12:00'),
(1, '2025-11-30 14:00', '2025-11-30 18:00'),
(2, '2025-12-05 08:00', '2025-12-05 11:00'),
(2, '2025-04-13 16:00', '2025-04-13 19:00');

INSERT INTO Scheduled_Class (cid, tid, rid, start_at, end_at, capacity) VALUES
(1, 1, 3, '2025-12-01 09:00', '2025-12-01 10:00', 10),
(2, 2, 1, '2025-11-30 10:30', '2025-11-30 11:15', 15), 
(3, 1, 2, '2025-04-13 14:00', '2025-04-13 15:15', 12);

INSERT INTO Class_Registration (mid, scid) VALUES
(1, 1),
(2, 1),
(3, 2),
(1, 3);   

INSERT INTO Health_Metric (mid, weight_kg, heart_bpm, body_fat_pct) VALUES
(1, 68.5, 72, 18.5),
(2, 82.3, 78, 22.1),
(3, 75.0, 70, 20.4),
(1, 67.8, 70, 18.0);

INSERT INTO Fitness_Goals (mid, goal_type, target_value) VALUES
(1, 'weight_loss', 65.0),
(2, 'muscle_gain', 85.0),
(3, 'body_fat_reduction', 18.0);