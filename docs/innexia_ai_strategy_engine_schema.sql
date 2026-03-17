-- Innexia AI Strategy Engine - Core persistence schema
-- Compatible with MySQL / MariaDB
-- Creates the 5 core tables used by the AI Strategy Engine:
--   1) analysis_requests
--   2) analysis_results
--   3) analysis_modules
--   4) analysis_activities
--   5) analysis_risks

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE IF NOT EXISTS analysis_requests (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  request_id VARCHAR(64) NOT NULL,
  project_id BIGINT UNSIGNED NULL,
  project_name VARCHAR(255) NOT NULL,
  analysis_type VARCHAR(100) DEFAULT NULL,
  language_code VARCHAR(10) NOT NULL DEFAULT 'es',
  organization_name VARCHAR(255) DEFAULT NULL,
  input_json LONGTEXT NOT NULL,
  status ENUM('pending','running','completed','failed') NOT NULL DEFAULT 'pending',
  workflow_version VARCHAR(20) NOT NULL,
  execution_time_ms INT DEFAULT NULL,
  created_by VARCHAR(255) DEFAULT NULL,
  error_message TEXT DEFAULT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_analysis_requests_request_id (request_id),
  KEY idx_analysis_requests_project_id (project_id),
  KEY idx_analysis_requests_status (status),
  KEY idx_analysis_requests_created_at (created_at),
  KEY idx_analysis_requests_project_name (project_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS analysis_results (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  request_id VARCHAR(64) NOT NULL,
  consolidated_json LONGTEXT NOT NULL,
  executive_summary MEDIUMTEXT DEFAULT NULL,
  verdict_decision VARCHAR(100) DEFAULT NULL,
  confidence_score DECIMAL(5,2) DEFAULT NULL,
  market_score DECIMAL(5,2) DEFAULT NULL,
  viability_score DECIMAL(5,2) DEFAULT NULL,
  risk_score DECIMAL(5,2) DEFAULT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_analysis_results_request_id (request_id),
  KEY idx_analysis_results_verdict (verdict_decision),
  KEY idx_analysis_results_created_at (created_at),
  CONSTRAINT fk_analysis_results_request
    FOREIGN KEY (request_id)
    REFERENCES analysis_requests(request_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS analysis_modules (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  request_id VARCHAR(64) NOT NULL,
  module_name VARCHAR(100) NOT NULL,
  module_status ENUM('pending','running','completed','failed') NOT NULL DEFAULT 'completed',
  input_json LONGTEXT DEFAULT NULL,
  output_json LONGTEXT DEFAULT NULL,
  started_at DATETIME DEFAULT NULL,
  completed_at DATETIME DEFAULT NULL,
  error_message TEXT DEFAULT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_analysis_modules_request_module (request_id, module_name),
  KEY idx_analysis_modules_status (module_status),
  KEY idx_analysis_modules_created_at (created_at),
  CONSTRAINT fk_analysis_modules_request
    FOREIGN KEY (request_id)
    REFERENCES analysis_requests(request_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS analysis_activities (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  request_id VARCHAR(64) NOT NULL,
  activity_id VARCHAR(50) NOT NULL,
  epic VARCHAR(255) DEFAULT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT DEFAULT NULL,
  priority ENUM('baja','media','alta','critica') DEFAULT 'media',
  owner_role VARCHAR(100) DEFAULT NULL,
  estimated_days INT DEFAULT NULL,
  depends_on_json TEXT DEFAULT NULL,
  kanban_status ENUM('todo','in_progress','review','done') NOT NULL DEFAULT 'todo',
  phase_id VARCHAR(50) DEFAULT NULL,
  start_date DATE DEFAULT NULL,
  end_date DATE DEFAULT NULL,
  sort_order INT DEFAULT NULL,
  raw_json LONGTEXT DEFAULT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_analysis_activities_request_activity (request_id, activity_id),
  KEY idx_analysis_activities_request_id (request_id),
  KEY idx_analysis_activities_phase_id (phase_id),
  KEY idx_analysis_activities_kanban_status (kanban_status),
  KEY idx_analysis_activities_priority (priority),
  KEY idx_analysis_activities_dates (start_date, end_date),
  CONSTRAINT fk_analysis_activities_request
    FOREIGN KEY (request_id)
    REFERENCES analysis_requests(request_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS analysis_risks (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  request_id VARCHAR(64) NOT NULL,
  risk_id VARCHAR(50) NOT NULL,
  title VARCHAR(255) NOT NULL,
  category VARCHAR(100) DEFAULT NULL,
  probability ENUM('baja','media','alta') DEFAULT 'media',
  impact ENUM('bajo','medio','alto','critico') DEFAULT 'medio',
  mitigation TEXT DEFAULT NULL,
  owner VARCHAR(100) DEFAULT NULL,
  raw_json LONGTEXT DEFAULT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_analysis_risks_request_risk (request_id, risk_id),
  KEY idx_analysis_risks_category (category),
  KEY idx_analysis_risks_probability (probability),
  KEY idx_analysis_risks_impact (impact),
  CONSTRAINT fk_analysis_risks_request
    FOREIGN KEY (request_id)
    REFERENCES analysis_requests(request_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
