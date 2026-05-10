-- Run this once to create the MySQL database and user
-- Execute as root: mysql -u root -p < setup_db.sql

CREATE DATABASE IF NOT EXISTS football_club_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'football_user'@'localhost'
  IDENTIFIED BY 'change_this_password';

GRANT ALL PRIVILEGES ON football_club_db.*
  TO 'football_user'@'localhost';

FLUSH PRIVILEGES;

-- Verify
SELECT User, Host FROM mysql.user WHERE User = 'football_user';
SHOW GRANTS FOR 'football_user'@'localhost';
