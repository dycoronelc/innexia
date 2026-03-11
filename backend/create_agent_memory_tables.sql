-- Script SQL para crear las tablas de memoria del agente
-- Ejecutar este script en MySQL

-- Tabla para memorias del agente
CREATE TABLE IF NOT EXISTS agent_memories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    memory_type VARCHAR(50) NOT NULL,
    `key` VARCHAR(255) NOT NULL,
    value JSON NOT NULL,
    importance INT DEFAULT 1,
    expires_at DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id),
    INDEX idx_memory_type (memory_type),
    INDEX idx_key (`key`),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tabla para sesiones de conversación
CREATE TABLE IF NOT EXISTS conversation_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_id VARCHAR(255) NOT NULL UNIQUE,
    project_id INT NULL,
    current_context JSON NULL,
    conversation_summary TEXT NULL,
    user_intent VARCHAR(100) NULL,
    is_active BOOLEAN DEFAULT TRUE,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id),
    INDEX idx_project_id (project_id),
    INDEX idx_is_active (is_active),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
);

-- Tabla para mensajes de conversación
CREATE TABLE IF NOT EXISTS conversation_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    message_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    metadata JSON NULL,
    intent_detected VARCHAR(100) NULL,
    confidence_score INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session_id (session_id),
    INDEX idx_message_type (message_type),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (session_id) REFERENCES conversation_sessions(id) ON DELETE CASCADE
);

-- Tabla para contexto del usuario
CREATE TABLE IF NOT EXISTS user_contexts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    current_project_id INT NULL,
    expertise_level VARCHAR(50) DEFAULT 'beginner',
    business_sector VARCHAR(100) NULL,
    preferred_language VARCHAR(10) DEFAULT 'es',
    notification_preferences JSON NULL,
    learning_goals JSON NULL,
    last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_current_project_id (current_project_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (current_project_id) REFERENCES projects(id) ON DELETE SET NULL
);

-- Insertar datos de prueba (opcional)
INSERT INTO user_contexts (user_id, expertise_level, business_sector, preferred_language) 
SELECT id, 'beginner', 'Tecnología', 'es' 
FROM users 
WHERE id NOT IN (SELECT user_id FROM user_contexts);

