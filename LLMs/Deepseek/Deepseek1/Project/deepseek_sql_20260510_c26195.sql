CREATE DATABASE football_club;
USE football_club;

-- Users table (members only)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_member BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- News posts (only members can insert)
CREATE TABLE news_posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Game schedule (pre-defined)
CREATE TABLE games (
    id INT AUTO_INCREMENT PRIMARY KEY,
    opponent VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    game_date DATE NOT NULL,
    game_time TIME NOT NULL
);

-- Insert some sample games
INSERT INTO games (opponent, location, game_date, game_time) VALUES
('FC United', 'Home Stadium', '2025-04-15', '15:00:00'),
('City Rivals', 'Away Ground', '2025-04-22', '17:30:00'),
('North End', 'Home Stadium', '2025-04-29', '14:00:00'),
('Southampton Stars', 'Away', '2025-05-06', '16:00:00');