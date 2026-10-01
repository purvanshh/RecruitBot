-- =============================================
-- RecruiterFlow Section B seed data
-- Exact candidate/job values from the assignment PDF.
-- Junction tables are cleared first so re-seeding replaces
-- obsolete traits/skills instead of leaving stale rows.
-- =============================================

DELETE FROM candidate_traits;
DELETE FROM candidate_skills;
DELETE FROM job_culture_keywords;
DELETE FROM job_required_skills;

-- =============================================
-- SKILLS
-- =============================================
INSERT INTO skills (id, name) VALUES
(1, 'deduction'),
(2, 'pattern-recognition'),
(3, 'forensics'),
(4, 'research'),
(5, 'time-management'),
(6, 'public-speaking'),
(7, 'systems-design'),
(8, 'rapid-prototyping'),
(9, 'leadership'),
(10, 'project-management'),
(11, 'stakeholder-management'),
(12, 'woodworking'),
(13, 'minimalism'),
(14, 'negotiation'),
(15, 'chemistry'),
(16, 'persuasion'),
(17, 'resourcefulness'),
(18, 'theoretical-analysis'),
(19, 'precision'),
(20, 'strategy'),
(21, 'crisis-management'),
(22, 'sales'),
(23, 'team-building'),
(24, 'mentorship'),
(25, 'security'),
(26, 'loyalty'),
(27, 'optimism')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

-- =============================================
-- CANDIDATES
-- =============================================
INSERT INTO candidates (id, name, experience_years, availability, quirk) VALUES
(1, 'Sherlock H.', 8, 'Immediate', 'Solves problems by eliminating the impossible; occasionally insufferable in standups.'),
(2, 'Hermione G.', 4, '2 weeks', 'Reads the entire documentation before writing a single line of code.'),
(3, 'Tony S.', 12, 'Not looking', 'Ships an MVP overnight, refuses to write tests.'),
(4, 'Leslie K.', 6, 'Immediate', 'Has a binder for everything, including the binder.'),
(5, 'Ron S.', 15, 'Not looking', 'Refuses to use more than one monitor.'),
(6, 'Rick S.', 20, 'Immediate', 'Solution works, mechanism deeply concerning.'),
(7, 'Elle W.', 3, 'Immediate', 'Underestimated in every standup, correct in every retro.'),
(8, 'MacGyver', 10, '2 weeks', 'Fixes production outages with duct tape and a paperclip metaphor.'),
(9, 'Sheldon C.', 9, 'Immediate', 'Correct 95% of the time, insufferable 100% of the time.'),
(10, 'Katniss E.', 5, 'Immediate', 'Excellent under pressure, terrible with public speaking.'),
(11, 'Michael S.', 11, 'Not looking', 'World''s best boss, according to a mug he bought himself.'),
(12, 'Olivia P.', 13, '2 weeks', 'Handles it. Whatever it is.'),
(13, 'Ted L.', 7, 'Immediate', 'Turns every technical setback into a folksy metaphor.'),
(14, 'Miranda P.', 18, 'Not looking', 'Reviews every PR personally. Says nothing. Everyone panics.'),
(15, 'Dwight S.', 9, 'Immediate', 'Assistant to the regional backend engineer.')
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    experience_years = EXCLUDED.experience_years,
    availability = EXCLUDED.availability,
    quirk = EXCLUDED.quirk;

-- =============================================
-- CANDIDATE SKILLS
-- =============================================
INSERT INTO candidate_skills (candidate_id, skill_id) VALUES
-- Sherlock H.
(1, 1), (1, 2), (1, 3),
-- Hermione G.
(2, 4), (2, 5), (2, 6),
-- Tony S.
(3, 7), (3, 8), (3, 9),
-- Leslie K.
(4, 10), (4, 11), (4, 6),
-- Ron S.
(5, 12), (5, 13), (5, 14),
-- Rick S.
(6, 7), (6, 8), (6, 15),
-- Elle W.
(7, 16), (7, 4), (7, 6),
-- MacGyver
(8, 8), (8, 17), (8, 15), (8, 7),
-- Sheldon C.
(9, 18), (9, 2), (9, 4),
-- Katniss E.
(10, 19), (10, 20), (10, 21),
-- Michael S.
(11, 22), (11, 6), (11, 23),
-- Olivia P.
(12, 21), (12, 14), (12, 20), (12, 9),
-- Ted L. (team-building, optimism, mentorship, public-speaking)
(13, 23), (13, 27), (13, 24), (13, 6),
-- Miranda P.
(14, 9), (14, 14), (14, 11), (14, 19),
-- Dwight S.
(15, 22), (15, 14), (15, 25), (15, 26);

-- =============================================
-- CANDIDATE TRAITS (exact PDF values)
-- =============================================
INSERT INTO candidate_traits (candidate_id, trait) VALUES
(1, 'analytical'), (1, 'blunt'),
(2, 'detail-oriented'), (2, 'overachiever'),
(3, 'confident'), (3, 'innovative'),
(4, 'tenacious'), (4, 'organized'),
(5, 'stubborn'), (5, 'principled'),
(6, 'genius'), (6, 'reckless'),
(7, 'optimistic'), (7, 'sharp'),
(8, 'calm'), (8, 'improviser'),
(9, 'rigid'), (9, 'brilliant'),
(10, 'resilient'), (10, 'decisive'),
(11, 'enthusiastic'), (11, 'chaotic'),
(12, 'decisive'), (12, 'intense'),
(13, 'empathetic'), (13, 'persistent'),
(14, 'demanding'), (14, 'decisive'),
(15, 'intense'), (15, 'loyal');

-- =============================================
-- JOBS
-- =============================================
INSERT INTO jobs (id, title, min_experience, tagline) VALUES
(1, 'Backend Detective', 3, 'We have a bug. We have no leads. We have you.'),
(2, 'Rapid Prototyping Engineer', 2, 'Ship first, document never (kidding — please document).'),
(3, 'Developer Relations Lead', 2, 'Explain complex things to confused humans, cheerfully.'),
(4, 'Engineering Manager, Chaos Team', 5, 'Herd cats. The cats are senior engineers.'),
(5, 'Incident Commander', 4, '3am page. You''re the one who picks up.'),
(6, 'Sales Engineer', 3, 'Sell the vision, then go build it.')
ON CONFLICT (id) DO UPDATE SET
    title = EXCLUDED.title,
    min_experience = EXCLUDED.min_experience,
    tagline = EXCLUDED.tagline;

-- =============================================
-- JOB REQUIRED SKILLS
-- =============================================
INSERT INTO job_required_skills (job_id, skill_id) VALUES
-- Backend Detective
(1, 1), (1, 2), (1, 3),
-- Rapid Prototyping Engineer
(2, 8), (2, 7),
-- Developer Relations Lead
(3, 6), (3, 4),
-- Engineering Manager, Chaos Team
(4, 23), (4, 11), (4, 9),
-- Incident Commander
(5, 21), (5, 20), (5, 14),
-- Sales Engineer
(6, 22), (6, 6), (6, 14);

-- =============================================
-- JOB CULTURE KEYWORDS
-- =============================================
INSERT INTO job_culture_keywords (job_id, keyword) VALUES
(1, 'analytical'), (1, 'autonomous'),
(2, 'innovative'), (2, 'fast-paced'),
(3, 'energetic'), (3, 'curious'),
(4, 'empathetic'), (4, 'organized'),
(5, 'decisive'), (5, 'calm-under-pressure'),
(6, 'enthusiastic'), (6, 'persistent');

-- Keep SERIAL sequences in sync with explicit IDs
SELECT setval(pg_get_serial_sequence('skills', 'id'), (SELECT MAX(id) FROM skills));
SELECT setval(pg_get_serial_sequence('candidates', 'id'), (SELECT MAX(id) FROM candidates));
SELECT setval(pg_get_serial_sequence('jobs', 'id'), (SELECT MAX(id) FROM jobs));
