CREATE TABLE rooms (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    room_name VARCHAR(255),
    room_type ENUM('private', 'group') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE = InnoDB;

CREATE TABLE messages (
    message_id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT,
    receiver_id INT,
    room_id INT,
    message_text TEXT,
    message_type ENUM('text', 'image', 'file', 'video', 'audio') NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES accounts(accounts_id),
    FOREIGN KEY (receiver_id) REFERENCES accounts(accounts_id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES rooms(room_id) ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE room_members (
    room_id INT,
    user_id INT,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_admin BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (room_id, user_id),
    FOREIGN KEY (room_id) REFERENCES rooms(room_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES accounts(accounts_id) ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE user_status (
    user_id INT,
    status ENUM('online', 'offline', 'away', 'busy') NOT NULL,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES accounts(accounts_id) ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    type ENUM('message', 'mention', 'friend_request', 'system') NOT NULL,
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES accounts(accounts_id) ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE message_reads (
    message_id INT,
    user_id INT,
    read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (message_id, user_id),
    FOREIGN KEY (message_id) REFERENCES messages(message_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES accounts(accounts_id) ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE media (
    media_id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT,
    room_id INT,
    media_url VARCHAR(255),
    media_type ENUM('image', 'video', 'audio', 'document') NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES accounts(accounts_id),
    FOREIGN KEY (room_id) REFERENCES rooms(room_id) ON DELETE CASCADE
) ENGINE = InnoDB;