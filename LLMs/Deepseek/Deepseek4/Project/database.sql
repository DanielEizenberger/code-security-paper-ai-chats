CREATE DATABASE IF NOT EXISTS football_club;
USE football_club;

-- Members table (users who can post)
CREATE TABLE members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- News posts table
CREATE TABLE news_posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
);

-- Insert a test member (password: club123)
INSERT INTO members (username, password_hash, is_admin) 
VALUES ('manager', 'scrypt:32768:8:1$99wh39gyje3ocYMA$231fd307301887add7d4461e2b771ac403934ff40d60fc144538c5da575e14cf816dea554774ce3ce75e83c9d0ea6d19d65499952ab5820dc7fa555feb411199', TRUE);

-- Note: Run `python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('club123'))"` to generate a valid hash.