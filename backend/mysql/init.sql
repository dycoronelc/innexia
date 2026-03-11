-- Script de inicialización para MySQL
-- Este script se ejecuta automáticamente cuando se crea el contenedor MySQL

-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS `innovai_db` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Usar la base de datos
USE `innovai_db`;

-- Crear usuario si no existe (para desarrollo local)
-- En producción, esto debe hacerse manualmente por seguridad
CREATE USER IF NOT EXISTS 'bmc'@'localhost' IDENTIFIED BY 'Innexia';
CREATE USER IF NOT EXISTS 'bmc'@'%' IDENTIFIED BY 'Innexia';

-- Otorgar permisos al usuario
GRANT ALL PRIVILEGES ON `innovai_db`.* TO 'bmc'@'localhost';
GRANT ALL PRIVILEGES ON `innovai_db`.* TO 'bmc'@'%';

-- Aplicar cambios
FLUSH PRIVILEGES;

-- Mostrar información
SELECT 'Base de datos InnovAI configurada exitosamente' AS message;
SHOW DATABASES;
SHOW GRANTS FOR 'bmc'@'localhost';

