-- VM1: MySQL schema for storing art photos and descriptions
-- Run on VM1's MySQL server:  mysql -u root -p < vm1_db_setup.sql

CREATE DATABASE IF NOT EXISTS artdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE artdb;

-- Create a dedicated user (replace strong_password)
CREATE USER IF NOT EXISTS 'artuser'@'%' IDENTIFIED BY 'strong_password_here';
GRANT ALL PRIVILEGES ON artdb.* TO 'artuser'@'%';
FLUSH PRIVILEGES;

-- Table to hold artworks (including image as LONGBLOB)
DROP TABLE IF EXISTS artworks;
CREATE TABLE artworks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  artist VARCHAR(255) DEFAULT NULL,
  year VARCHAR(50) DEFAULT NULL,
  medium VARCHAR(255) DEFAULT NULL,
  description_th TEXT NOT NULL,
  image LONGBLOB NOT NULL,
  image_mime VARCHAR(64) DEFAULT 'image/jpeg',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
