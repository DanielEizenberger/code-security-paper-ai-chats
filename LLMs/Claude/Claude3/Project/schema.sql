-- ============================================================
--  FC Ironwall — Database Schema
--  Run:  mysql -u root -p < schema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS football_club
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE football_club;

-- ── Members ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS members (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    full_name     VARCHAR(120)  NOT NULL,
    email         VARCHAR(180)  NOT NULL UNIQUE,
    password_hash VARCHAR(256)  NOT NULL,
    position      VARCHAR(60)   NOT NULL DEFAULT 'Player',
    is_active     TINYINT(1)    NOT NULL DEFAULT 1,
    joined_at     TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ── News Posts ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS posts (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    member_id   INT UNSIGNED NOT NULL,
    title       VARCHAR(220) NOT NULL,
    content     TEXT         NOT NULL,
    category    ENUM('General','Match Report','Announcement','Training','Other')
                NOT NULL DEFAULT 'General',
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ── Match Schedule ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS matches (
    id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    opponent     VARCHAR(120) NOT NULL,
    match_date   DATETIME     NOT NULL,
    location     VARCHAR(200) NOT NULL,
    is_home      TINYINT(1)   NOT NULL DEFAULT 1,
    competition  VARCHAR(80)  NOT NULL DEFAULT 'Friendly',
    result       VARCHAR(10)  NULL COMMENT 'e.g. 3-1, or NULL if not played',
    notes        TEXT         NULL
) ENGINE=InnoDB;

-- ── Seed: demo admin member (password: Admin1234!) ────────────
-- Hash generated with werkzeug generate_password_hash('Admin1234!')
INSERT IGNORE INTO members (full_name, email, password_hash, position)
VALUES (
    'Club Admin',
    'admin@fcironwall.com',
    'scrypt:32768:8:1$demo$placeholder_run_seed_py',
    'Manager'
);

-- ── Seed: sample schedule ─────────────────────────────────────
INSERT IGNORE INTO matches (opponent, match_date, location, is_home, competition) VALUES
('Red Lions FC',       '2025-09-06 15:00:00', 'Ironwall Stadium, Gate 2',       1, 'League'),
('Blue Hawks United',  '2025-09-14 13:00:00', 'Hawks Arena, Northfield',         0, 'League'),
('Golden Stars SC',    '2025-09-21 15:00:00', 'Ironwall Stadium, Gate 2',       1, 'Cup'),
('River Rovers',       '2025-09-28 11:00:00', 'Riverside Ground, Eastwick',      0, 'League'),
('Northgate City FC',  '2025-10-05 15:00:00', 'Ironwall Stadium, Gate 2',       1, 'League'),
('Westfield Athletic', '2025-10-12 14:00:00', 'Westfield Sports Complex',        0, 'Friendly'),
('Old Town Rangers',   '2025-10-19 15:00:00', 'Ironwall Stadium, Gate 2',       1, 'Cup'),
('Bayshore Dynamos',   '2025-10-26 13:00:00', 'Bayshore Community Ground',       0, 'League'),
('Hillside Wanderers', '2025-11-02 15:00:00', 'Ironwall Stadium, Gate 2',       1, 'League'),
('Phoenix Rising FC',  '2025-11-09 15:00:00', 'Phoenix United Park',             0, 'Cup');
