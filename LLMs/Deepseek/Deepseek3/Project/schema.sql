-- database_setup.sql
-- Run this in MySQL to set up the database

CREATE DATABASE IF NOT EXISTS football_club;
USE football_club;

-- Members table
CREATE TABLE IF NOT EXISTS members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- News posts table
CREATE TABLE IF NOT EXISTS news_posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
);

-- Insert an admin user (password: admin123)
-- Note: Generate actual hash using Python: generate_password_hash('admin123')
INSERT INTO members (username, email, password_hash, is_admin) 
VALUES ('admin', 'admin@fcchampions.com', 'scrypt:32768:8:1$abc123...', TRUE);

-- Sample member (for testing)
INSERT INTO members (username, email, password_hash, is_admin) 
VALUES ('john_doe', 'john@example.com', 'scrypt:32768:8:1$abc123...', FALSE);

-- Sample news post
INSERT INTO news_posts (member_id, title, content) 
VALUES (1, 'Welcome to the new season!', 'We are excited to announce our upcoming season...');