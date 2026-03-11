-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1:3306
-- Tiempo de generación: 05-03-2026 a las 14:13:45
-- Versión del servidor: 9.1.0
-- Versión de PHP: 8.3.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `bmc`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `activity_assignees`
--

DROP TABLE IF EXISTS `activity_assignees`;
CREATE TABLE IF NOT EXISTS `activity_assignees` (
  `id` int NOT NULL AUTO_INCREMENT,
  `activity_id` int NOT NULL,
  `user_id` int NOT NULL,
  `assigned_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `activity_id` (`activity_id`),
  KEY `user_id` (`user_id`),
  KEY `ix_activity_assignees_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `activity_attachments`
--

DROP TABLE IF EXISTS `activity_attachments`;
CREATE TABLE IF NOT EXISTS `activity_attachments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `activity_id` int NOT NULL,
  `name` varchar(200) NOT NULL,
  `original_name` varchar(255) NOT NULL,
  `file_path` varchar(500) NOT NULL,
  `file_type` varchar(100) NOT NULL,
  `file_size` bigint NOT NULL,
  `description` text,
  `uploader_id` int NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `activity_id` (`activity_id`),
  KEY `uploader_id` (`uploader_id`),
  KEY `ix_activity_attachments_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `activity_checklists`
--

DROP TABLE IF EXISTS `activity_checklists`;
CREATE TABLE IF NOT EXISTS `activity_checklists` (
  `id` int NOT NULL AUTO_INCREMENT,
  `activity_id` int NOT NULL,
  `title` varchar(200) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `activity_id` (`activity_id`),
  KEY `ix_activity_checklists_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `activity_checklist_items`
--

DROP TABLE IF EXISTS `activity_checklist_items`;
CREATE TABLE IF NOT EXISTS `activity_checklist_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `checklist_id` int NOT NULL,
  `content` varchar(500) NOT NULL,
  `completed` tinyint(1) NOT NULL,
  `completed_at` datetime DEFAULT NULL,
  `completed_by_id` int DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `checklist_id` (`checklist_id`),
  KEY `completed_by_id` (`completed_by_id`),
  KEY `ix_activity_checklist_items_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `activity_comments`
--

DROP TABLE IF EXISTS `activity_comments`;
CREATE TABLE IF NOT EXISTS `activity_comments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `activity_id` int NOT NULL,
  `author_id` int NOT NULL,
  `content` text NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `activity_id` (`activity_id`),
  KEY `author_id` (`author_id`),
  KEY `ix_activity_comments_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `activity_labels`
--

DROP TABLE IF EXISTS `activity_labels`;
CREATE TABLE IF NOT EXISTS `activity_labels` (
  `id` int NOT NULL AUTO_INCREMENT,
  `activity_id` int NOT NULL,
  `category_id` int NOT NULL,
  `created_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `activity_id` (`activity_id`),
  KEY `category_id` (`category_id`),
  KEY `ix_activity_labels_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `activity_tags`
--

DROP TABLE IF EXISTS `activity_tags`;
CREATE TABLE IF NOT EXISTS `activity_tags` (
  `id` int NOT NULL AUTO_INCREMENT,
  `activity_id` int NOT NULL,
  `tag_id` int NOT NULL,
  `created_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `activity_id` (`activity_id`),
  KEY `tag_id` (`tag_id`),
  KEY `ix_activity_tags_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `agent_memories`
--

DROP TABLE IF EXISTS `agent_memories`;
CREATE TABLE IF NOT EXISTS `agent_memories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `session_id` varchar(255) NOT NULL,
  `memory_type` varchar(50) NOT NULL,
  `key` varchar(255) NOT NULL,
  `value` json NOT NULL,
  `importance` int DEFAULT '1',
  `expires_at` datetime DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_session_id` (`session_id`(250)),
  KEY `idx_memory_type` (`memory_type`),
  KEY `idx_key` (`key`(250))
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `analytics_events`
--

DROP TABLE IF EXISTS `analytics_events`;
CREATE TABLE IF NOT EXISTS `analytics_events` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `event_type` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `event_category` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `event_data` json DEFAULT NULL,
  `metadata` json DEFAULT NULL,
  `session_id` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `project_id` int DEFAULT NULL,
  `activity_id` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_analytics_events_user_id` (`user_id`),
  KEY `idx_analytics_events_type` (`event_type`),
  KEY `idx_analytics_events_category` (`event_category`),
  KEY `idx_analytics_events_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `audit_logs`
--

DROP TABLE IF EXISTS `audit_logs`;
CREATE TABLE IF NOT EXISTS `audit_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `action` varchar(100) NOT NULL,
  `entity_type` varchar(100) NOT NULL,
  `entity_id` varchar(100) DEFAULT NULL,
  `details` text,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` text,
  `timestamp` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `ix_audit_logs_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `business_model_canvases`
--

DROP TABLE IF EXISTS `business_model_canvases`;
CREATE TABLE IF NOT EXISTS `business_model_canvases` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_id` int NOT NULL,
  `key_partners` text,
  `key_activities` text,
  `key_resources` text,
  `value_propositions` text,
  `customer_relationships` text,
  `channels` text,
  `customer_segments` text,
  `cost_structure` text,
  `revenue_streams` text,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `project_id` (`project_id`),
  KEY `ix_business_model_canvases_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categories`
--

DROP TABLE IF EXISTS `categories`;
CREATE TABLE IF NOT EXISTS `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `company_id` int NOT NULL,
  `description` text,
  `color` varchar(7) DEFAULT NULL,
  `icon` varchar(50) DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `company_id` (`company_id`),
  KEY `ix_categories_name` (`name`),
  KEY `ix_categories_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `companies`
--

DROP TABLE IF EXISTS `companies`;
CREATE TABLE IF NOT EXISTS `companies` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `slug` varchar(100) NOT NULL,
  `description` text,
  `logo_url` varchar(500) DEFAULT NULL,
  `primary_color` varchar(7) DEFAULT NULL,
  `secondary_color` varchar(7) DEFAULT NULL,
  `favicon_url` varchar(500) DEFAULT NULL,
  `industry` varchar(100) DEFAULT NULL,
  `website` varchar(200) DEFAULT NULL,
  `phone` varchar(50) DEFAULT NULL,
  `email` varchar(200) DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `state` varchar(100) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `address` text,
  `timezone` varchar(50) DEFAULT NULL,
  `subscription_plan` varchar(50) DEFAULT NULL,
  `max_users` int DEFAULT NULL,
  `max_projects` int DEFAULT NULL,
  `max_storage_gb` int DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `trial_ends_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_companies_slug` (`slug`),
  UNIQUE KEY `ix_companies_name` (`name`),
  KEY `ix_companies_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `conversation_flows`
--

DROP TABLE IF EXISTS `conversation_flows`;
CREATE TABLE IF NOT EXISTS `conversation_flows` (
  `id` int NOT NULL AUTO_INCREMENT,
  `flow_id` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `flow_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'linear',
  `flow_steps` json DEFAULT NULL,
  `flow_rules` json DEFAULT NULL,
  `flow_conditions` json DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `version` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT '1.0',
  `priority` int DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `flow_id` (`flow_id`),
  KEY `idx_conversation_flows_flow_id` (`flow_id`),
  KEY `idx_conversation_flows_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `conversation_messages`
--

DROP TABLE IF EXISTS `conversation_messages`;
CREATE TABLE IF NOT EXISTS `conversation_messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `message_type` enum('user','agent','system') COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `intent` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `confidence` float DEFAULT NULL,
  `context_data` json DEFAULT NULL,
  `metadata` json DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_session_id` (`session_id`),
  KEY `idx_message_type` (`message_type`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `conversation_sessions`
--

DROP TABLE IF EXISTS `conversation_sessions`;
CREATE TABLE IF NOT EXISTS `conversation_sessions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` int NOT NULL,
  `project_id` int DEFAULT NULL,
  `session_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'general',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'active',
  `context_data` json DEFAULT NULL,
  `metadata` json DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `last_activity` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `session_id` (`session_id`),
  KEY `idx_session_id` (`session_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_project_id` (`project_id`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `conversation_states`
--

DROP TABLE IF EXISTS `conversation_states`;
CREATE TABLE IF NOT EXISTS `conversation_states` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` int NOT NULL,
  `current_state` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `state_type` enum('active','paused','completed','abandoned','transitioning') COLLATE utf8mb4_unicode_ci DEFAULT 'active',
  `state_data` json DEFAULT NULL,
  `primary_context` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `secondary_contexts` json DEFAULT NULL,
  `context_stack` json DEFAULT NULL,
  `current_intent` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `intent_type` enum('primary','secondary','contextual','fallback') COLLATE utf8mb4_unicode_ci DEFAULT 'primary',
  `intent_confidence` float DEFAULT '0',
  `intent_history` json DEFAULT NULL,
  `flow_id` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `flow_step` int DEFAULT '0',
  `flow_data` json DEFAULT NULL,
  `flow_history` json DEFAULT NULL,
  `short_term_memory` json DEFAULT NULL,
  `long_term_memory` json DEFAULT NULL,
  `memory_priority` json DEFAULT NULL,
  `active_threads` json DEFAULT NULL,
  `thread_priorities` json DEFAULT NULL,
  `thread_contexts` json DEFAULT NULL,
  `previous_state` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `transition_reason` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `transition_data` json DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `last_activity` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_conversation_states_session_id` (`session_id`),
  KEY `idx_conversation_states_user_id` (`user_id`),
  KEY `idx_conversation_states_current_state` (`current_state`),
  KEY `idx_conversation_states_state_type` (`state_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `conversation_threads`
--

DROP TABLE IF EXISTS `conversation_threads`;
CREATE TABLE IF NOT EXISTS `conversation_threads` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `thread_id` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `thread_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'main',
  `thread_context` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `thread_data` json DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `priority` int DEFAULT '1',
  `last_activity` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `parent_thread_id` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `related_threads` json DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_conversation_threads_session_id` (`session_id`),
  KEY `idx_conversation_threads_thread_id` (`thread_id`),
  KEY `idx_conversation_threads_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `data_sources`
--

DROP TABLE IF EXISTS `data_sources`;
CREATE TABLE IF NOT EXISTS `data_sources` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `source_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `collection_frequency` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'daily',
  `is_active` tinyint(1) DEFAULT '1',
  `last_collection` timestamp NULL DEFAULT NULL,
  `data_schema` json DEFAULT NULL,
  `collection_parameters` json DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_data_sources_type` (`source_type`),
  KEY `idx_data_sources_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `document_generation_logs`
--

DROP TABLE IF EXISTS `document_generation_logs`;
CREATE TABLE IF NOT EXISTS `document_generation_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_id` int NOT NULL,
  `user_id` int NOT NULL,
  `document_type` varchar(50) NOT NULL,
  `status` varchar(20) NOT NULL,
  `error_message` text,
  `generation_time` int DEFAULT NULL,
  `tokens_used` int DEFAULT NULL,
  `model_used` varchar(50) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `project_id` (`project_id`),
  KEY `user_id` (`user_id`),
  KEY `ix_document_generation_logs_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `document_templates`
--

DROP TABLE IF EXISTS `document_templates`;
CREATE TABLE IF NOT EXISTS `document_templates` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `document_type` varchar(50) NOT NULL,
  `template_content` text NOT NULL,
  `variables` json DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `ix_document_templates_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `educational_categories`
--

DROP TABLE IF EXISTS `educational_categories`;
CREATE TABLE IF NOT EXISTS `educational_categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` text,
  `icon` varchar(100) DEFAULT NULL,
  `color` varchar(7) DEFAULT NULL,
  `parent_id` int DEFAULT NULL,
  `sort_order` int DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `parent_id` (`parent_id`),
  KEY `ix_educational_categories_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `educational_content`
--

DROP TABLE IF EXISTS `educational_content`;
CREATE TABLE IF NOT EXISTS `educational_content` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `description` text,
  `content_type` enum('ARTICLE','VIDEO','PODCAST','INFOGRAPHIC','COURSE','WEBINAR') NOT NULL,
  `content_source` enum('INTERNAL','RSS_FEED','YOUTUBE','VIMEO','SPOTIFY','CUSTOM_API') NOT NULL,
  `source_url` varchar(500) DEFAULT NULL,
  `content_data` json DEFAULT NULL,
  `difficulty` enum('BEGINNER','INTERMEDIATE','ADVANCED') DEFAULT NULL,
  `duration_minutes` int DEFAULT NULL,
  `author` varchar(255) DEFAULT NULL,
  `instructor` varchar(255) DEFAULT NULL,
  `thumbnail_url` varchar(500) DEFAULT NULL,
  `tags` json DEFAULT NULL,
  `categories` json DEFAULT NULL,
  `status` enum('DRAFT','PUBLISHED','ARCHIVED','MODERATION') DEFAULT NULL,
  `published_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `moderated_by` int DEFAULT NULL,
  `moderation_notes` text,
  `view_count` int DEFAULT NULL,
  `like_count` int DEFAULT NULL,
  `bookmark_count` int DEFAULT NULL,
  `rating` decimal(3,2) DEFAULT NULL,
  `rating_count` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `created_by` (`created_by`),
  KEY `moderated_by` (`moderated_by`),
  KEY `ix_educational_content_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `educational_tags`
--

DROP TABLE IF EXISTS `educational_tags`;
CREATE TABLE IF NOT EXISTS `educational_tags` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` text,
  `color` varchar(7) DEFAULT NULL,
  `usage_count` int DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `ix_educational_tags_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `external_content_sources`
--

DROP TABLE IF EXISTS `external_content_sources`;
CREATE TABLE IF NOT EXISTS `external_content_sources` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `source_type` enum('RSS_FEED','YOUTUBE_CHANNEL','VIMEO_CHANNEL','SPOTIFY_SHOW','CUSTOM_API') NOT NULL,
  `source_url` varchar(500) NOT NULL,
  `api_key` varchar(255) DEFAULT NULL,
  `api_secret` varchar(255) DEFAULT NULL,
  `refresh_interval_minutes` int DEFAULT NULL,
  `last_sync_at` datetime DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `auto_import` tinyint(1) DEFAULT NULL,
  `category_mapping` json DEFAULT NULL,
  `tag_mapping` json DEFAULT NULL,
  `content_filters` json DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `created_by` (`created_by`),
  KEY `ix_external_content_sources_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `generated_documents`
--

DROP TABLE IF EXISTS `generated_documents`;
CREATE TABLE IF NOT EXISTS `generated_documents` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_id` int NOT NULL,
  `user_id` int NOT NULL,
  `document_type` varchar(50) NOT NULL,
  `title` varchar(255) NOT NULL,
  `content` text NOT NULL,
  `file_path` varchar(500) DEFAULT NULL,
  `file_size` int DEFAULT NULL,
  `is_downloaded` tinyint(1) DEFAULT NULL,
  `download_count` int DEFAULT NULL,
  `metadata_info` json DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `project_id` (`project_id`),
  KEY `user_id` (`user_id`),
  KEY `ix_generated_documents_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `learning_paths`
--

DROP TABLE IF EXISTS `learning_paths`;
CREATE TABLE IF NOT EXISTS `learning_paths` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `category` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `difficulty_level` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'beginner',
  `current_step` int DEFAULT '0',
  `total_steps` int DEFAULT '0',
  `completion_percentage` float DEFAULT '0',
  `content_items` json DEFAULT NULL,
  `prerequisites` json DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `is_completed` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `completed_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_learning_paths_user_id` (`user_id`),
  KEY `idx_learning_paths_category` (`category`),
  KEY `idx_learning_paths_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `locations`
--

DROP TABLE IF EXISTS `locations`;
CREATE TABLE IF NOT EXISTS `locations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `company_id` int NOT NULL,
  `description` text,
  `country` varchar(100) DEFAULT NULL,
  `state` varchar(100) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `address` text,
  `coordinates` varchar(50) DEFAULT NULL,
  `timezone` varchar(50) DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `company_id` (`company_id`),
  KEY `ix_locations_id` (`id`),
  KEY `ix_locations_name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `official_documents`
--

DROP TABLE IF EXISTS `official_documents`;
CREATE TABLE IF NOT EXISTS `official_documents` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `description` text,
  `document_type` enum('GUIDE','MANUAL','BROCHURE','POLICY','PROCEDURE','TEMPLATE','FORM') NOT NULL,
  `category` enum('HR','OPERATIONS','FINANCE','MARKETING','SALES','TECHNICAL','COMPLIANCE','TRAINING') NOT NULL,
  `file_path` varchar(500) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `file_size` bigint NOT NULL,
  `file_type` varchar(50) NOT NULL,
  `version` varchar(20) DEFAULT NULL,
  `is_public` tinyint(1) DEFAULT NULL,
  `requires_approval` tinyint(1) DEFAULT NULL,
  `approval_status` enum('DRAFT','PENDING','APPROVED','REJECTED','ARCHIVED') DEFAULT NULL,
  `approved_by` int DEFAULT NULL,
  `approved_at` datetime DEFAULT NULL,
  `expires_at` datetime DEFAULT NULL,
  `tags` json DEFAULT NULL,
  `document_metadata` json DEFAULT NULL,
  `download_count` int DEFAULT NULL,
  `view_count` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `approved_by` (`approved_by`),
  KEY `created_by` (`created_by`),
  KEY `ix_official_documents_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `proactive_suggestions`
--

DROP TABLE IF EXISTS `proactive_suggestions`;
CREATE TABLE IF NOT EXISTS `proactive_suggestions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `suggestion_type` varchar(50) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `priority` int DEFAULT '1',
  `category` varchar(100) DEFAULT NULL,
  `context_data` json DEFAULT NULL,
  `action_url` varchar(500) DEFAULT NULL,
  `action_text` varchar(100) DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT '0',
  `is_dismissed` tinyint(1) DEFAULT '0',
  `expires_at` datetime DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `read_at` datetime DEFAULT NULL,
  `dismissed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_suggestion_type` (`suggestion_type`),
  KEY `idx_category` (`category`),
  KEY `idx_priority` (`priority`),
  KEY `idx_is_read` (`is_read`),
  KEY `idx_is_dismissed` (`is_dismissed`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `projects`
--

DROP TABLE IF EXISTS `projects`;
CREATE TABLE IF NOT EXISTS `projects` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `description` text,
  `company_id` int NOT NULL,
  `category_id` int DEFAULT NULL,
  `location_id` int DEFAULT NULL,
  `status_id` int NOT NULL,
  `owner_id` int NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `company_id` (`company_id`),
  KEY `category_id` (`category_id`),
  KEY `location_id` (`location_id`),
  KEY `status_id` (`status_id`),
  KEY `owner_id` (`owner_id`),
  KEY `ix_projects_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `project_activities`
--

DROP TABLE IF EXISTS `project_activities`;
CREATE TABLE IF NOT EXISTS `project_activities` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `description` text,
  `status` varchar(20) NOT NULL,
  `priority` varchar(20) NOT NULL,
  `assignee_id` int NOT NULL,
  `project_id` int NOT NULL,
  `start_date` datetime NOT NULL,
  `due_date` datetime NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `assignee_id` (`assignee_id`),
  KEY `project_id` (`project_id`),
  KEY `ix_project_activities_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `project_documents`
--

DROP TABLE IF EXISTS `project_documents`;
CREATE TABLE IF NOT EXISTS `project_documents` (
  `id` int NOT NULL AUTO_INCREMENT,
  `filename` varchar(255) NOT NULL,
  `original_filename` varchar(255) NOT NULL,
  `file_path` varchar(500) NOT NULL,
  `file_type` varchar(100) NOT NULL,
  `file_size` bigint NOT NULL,
  `description` text,
  `project_id` int NOT NULL,
  `uploader_id` int NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `project_id` (`project_id`),
  KEY `uploader_id` (`uploader_id`),
  KEY `ix_project_documents_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `project_tags`
--

DROP TABLE IF EXISTS `project_tags`;
CREATE TABLE IF NOT EXISTS `project_tags` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_id` int NOT NULL,
  `tag_id` int NOT NULL,
  `created_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `project_id` (`project_id`),
  KEY `tag_id` (`tag_id`),
  KEY `ix_project_tags_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `recommendation_engine`
--

DROP TABLE IF EXISTS `recommendation_engine`;
CREATE TABLE IF NOT EXISTS `recommendation_engine` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `recommendation_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `category` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `priority` int DEFAULT '1',
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `reasoning` text COLLATE utf8mb4_unicode_ci,
  `expected_impact` float DEFAULT NULL,
  `data_sources` json DEFAULT NULL,
  `confidence_score` float DEFAULT '0',
  `action_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `action_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `is_read` tinyint(1) DEFAULT '0',
  `is_applied` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `expires_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_recommendation_user_id` (`user_id`),
  KEY `idx_recommendation_type` (`recommendation_type`),
  KEY `idx_recommendation_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `recommendation_engines`
--

DROP TABLE IF EXISTS `recommendation_engines`;
CREATE TABLE IF NOT EXISTS `recommendation_engines` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `recommendation_type` varchar(50) NOT NULL,
  `title` varchar(200) NOT NULL,
  `description` text,
  `priority` int DEFAULT '0',
  `category` varchar(100) DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT '0',
  `is_applied` tinyint(1) DEFAULT '0',
  `metadata` json DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `state_transitions`
--

DROP TABLE IF EXISTS `state_transitions`;
CREATE TABLE IF NOT EXISTS `state_transitions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `from_state` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `to_state` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `transition_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'automatic',
  `transition_reason` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `context_data` json DEFAULT NULL,
  `intent_data` json DEFAULT NULL,
  `flow_data` json DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_state_transitions_session_id` (`session_id`),
  KEY `idx_state_transitions_from_state` (`from_state`),
  KEY `idx_state_transitions_to_state` (`to_state`),
  KEY `idx_state_transitions_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `statuses`
--

DROP TABLE IF EXISTS `statuses`;
CREATE TABLE IF NOT EXISTS `statuses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `company_id` int NOT NULL,
  `description` text,
  `color` varchar(7) DEFAULT NULL,
  `icon` varchar(50) DEFAULT NULL,
  `is_final` tinyint(1) DEFAULT NULL,
  `order` int DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `company_id` (`company_id`),
  KEY `ix_statuses_name` (`name`),
  KEY `ix_statuses_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `suggestion_rules`
--

DROP TABLE IF EXISTS `suggestion_rules`;
CREATE TABLE IF NOT EXISTS `suggestion_rules` (
  `id` int NOT NULL AUTO_INCREMENT,
  `rule_name` varchar(100) NOT NULL,
  `rule_type` varchar(50) NOT NULL,
  `conditions` json NOT NULL,
  `suggestion_template` json NOT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `priority` int DEFAULT '5',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `rule_name` (`rule_name`),
  KEY `idx_rule_name` (`rule_name`),
  KEY `idx_rule_type` (`rule_type`),
  KEY `idx_is_active` (`is_active`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tags`
--

DROP TABLE IF EXISTS `tags`;
CREATE TABLE IF NOT EXISTS `tags` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `company_id` int NOT NULL,
  `description` text,
  `color` varchar(7) DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `company_id` (`company_id`),
  KEY `ix_tags_name` (`name`),
  KEY `ix_tags_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `hashed_password` varchar(255) NOT NULL,
  `role` varchar(20) NOT NULL,
  `company_id` int NOT NULL,
  `active` tinyint(1) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_email` (`email`),
  UNIQUE KEY `ix_users_username` (`username`),
  KEY `company_id` (`company_id`),
  KEY `ix_users_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user_analytics`
--

DROP TABLE IF EXISTS `user_analytics`;
CREATE TABLE IF NOT EXISTS `user_analytics` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `login_frequency` float DEFAULT '0',
  `session_duration` float DEFAULT '0',
  `project_completion_rate` float DEFAULT '0',
  `activity_completion_rate` float DEFAULT '0',
  `content_consumption_rate` float DEFAULT '0',
  `learning_progress` json DEFAULT NULL,
  `preferred_content_types` json DEFAULT NULL,
  `project_success_rate` float DEFAULT '0',
  `business_model_complexity` float DEFAULT '0',
  `market_research_depth` float DEFAULT '0',
  `chatbot_usage_frequency` float DEFAULT '0',
  `feature_usage_patterns` json DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `idx_user_analytics_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user_context`
--

DROP TABLE IF EXISTS `user_context`;
CREATE TABLE IF NOT EXISTS `user_context` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `business_domain` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `experience_level` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'beginner',
  `interests` json DEFAULT NULL,
  `learning_goals` json DEFAULT NULL,
  `preferred_content_types` json DEFAULT NULL,
  `communication_style` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'formal',
  `time_zone` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'UTC',
  `language_preference` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT 'es',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_business_domain` (`business_domain`),
  KEY `idx_experience_level` (`experience_level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user_contexts`
--

DROP TABLE IF EXISTS `user_contexts`;
CREATE TABLE IF NOT EXISTS `user_contexts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `current_project_id` int DEFAULT NULL,
  `expertise_level` varchar(50) DEFAULT NULL,
  `business_sector` varchar(100) DEFAULT NULL,
  `preferred_language` varchar(10) DEFAULT NULL,
  `notification_preferences` json DEFAULT NULL,
  `learning_goals` json DEFAULT NULL,
  `last_interaction` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `current_project_id` (`current_project_id`),
  KEY `ix_user_contexts_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user_suggestion_preferences`
--

DROP TABLE IF EXISTS `user_suggestion_preferences`;
CREATE TABLE IF NOT EXISTS `user_suggestion_preferences` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `notification_frequency` varchar(20) DEFAULT 'daily',
  `preferred_categories` json DEFAULT NULL,
  `max_suggestions_per_day` int DEFAULT '10',
  `quiet_hours_start` varchar(5) DEFAULT '22:00',
  `quiet_hours_end` varchar(5) DEFAULT '08:00',
  `timezone` varchar(50) DEFAULT 'UTC',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
