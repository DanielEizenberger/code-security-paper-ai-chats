-- FC Ironclad - MySQL Schema
-- Run this file once to initialize the database:
--   mysql -u root -p < schema.sql

CREATE DATABASE IF NOT EXISTS fc_ironclad
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE fc_ironclad;

-- ── Members ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS members (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(64)  NOT NULL UNIQUE,
    email       VARCHAR(255) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL COMMENT 'bcrypt hash',
    role        ENUM('admin','member') NOT NULL DEFAULT 'member',
    joined_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username)
) ENGINE=InnoDB;

-- ── News Posts ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS posts (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    member_id   INT UNSIGNED NOT NULL,
    title       VARCHAR(255) NOT NULL,
    body        TEXT         NOT NULL,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE,
    INDEX idx_created (created_at)
) ENGINE=InnoDB;

-- ── Fixtures / Match Schedule ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fixtures (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    match_date  DATE         NOT NULL,
    kick_off    TIME         NOT NULL DEFAULT '15:00:00',
    home_team   VARCHAR(100) NOT NULL,
    away_team   VARCHAR(100) NOT NULL,
    venue       VARCHAR(150) NOT NULL DEFAULT 'Ironclad Stadium',
    competition VARCHAR(100) NOT NULL DEFAULT 'League',
    result      VARCHAR(10)  NULL COMMENT 'e.g. 2-1 or NULL if not played',
    INDEX idx_date (match_date)
) ENGINE=InnoDB;

-- ── Seed: default admin ──────────────────────────────────────────────────────
-- Password is "admin123" (bcrypt). Change immediately in production!
INSERT IGNORE INTO members (username, email, password, role) VALUES (
    'admin',
    'admin@fcironclad.com',
    '$2b$12$KkB8Y3x6zXxQw5GQqmJyxuY3v8z.nOwVZpXkJYXqC7lO8gXcJBo2a',
    'admin'
);

-- ── Seed: sample fixtures ────────────────────────────────────────────────────
INSERT IGNORE INTO fixtures (match_date, kick_off, home_team, away_team, venue, competition, result) VALUES
    ('2025-08-10', '15:00:00', 'FC Ironclad',       'Red Phoenix FC',  'Ironclad Stadium',  'League',      '3-1'),
    ('2025-08-24', '14:00:00', 'Steel City United',  'FC Ironclad',    'Steel Arena',        'League',      '0-2'),
    ('2025-09-07', '15:00:00', 'FC Ironclad',       'Harbor Athletic', 'Ironclad Stadium',  'Cup',         '1-1'),
    ('2025-09-21', '16:00:00', 'FC Ironclad',       'Northgate Rovers','Ironclad Stadium',  'League',      NULL),
    ('2025-10-05', '15:00:00', 'Westfield City',    'FC Ironclad',     'Westfield Ground',  'League',      NULL),
    ('2025-10-19', '14:00:00', 'FC Ironclad',       'Blue Ridge SC',   'Ironclad Stadium',  'Cup',         NULL),
    ('2025-11-02', '15:00:00', 'FC Ironclad',       'Eastgate FC',     'Ironclad Stadium',  'League',      NULL),
    ('2025-11-16', '14:00:00', 'Crestwood Town',    'FC Ironclad',     'Crestwood Park',    'League',      NULL);
