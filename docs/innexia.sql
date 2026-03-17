-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost:3306
-- Tiempo de generación: 16-03-2026 a las 16:27:03
-- Versión del servidor: 10.6.24-MariaDB-cll-lve
-- Versión de PHP: 8.3.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `innexia`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `activity_assignees`
--

CREATE TABLE `activity_assignees` (
  `id` int(11) NOT NULL,
  `activity_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `assigned_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `activity_attachments`
--

CREATE TABLE `activity_attachments` (
  `id` int(11) NOT NULL,
  `activity_id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `original_name` varchar(255) NOT NULL,
  `file_path` varchar(500) NOT NULL,
  `file_type` varchar(100) NOT NULL,
  `file_size` bigint(20) NOT NULL,
  `description` text DEFAULT NULL,
  `uploader_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `activity_checklists`
--

CREATE TABLE `activity_checklists` (
  `id` int(11) NOT NULL,
  `activity_id` int(11) NOT NULL,
  `title` varchar(200) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `activity_checklist_items`
--

CREATE TABLE `activity_checklist_items` (
  `id` int(11) NOT NULL,
  `checklist_id` int(11) NOT NULL,
  `content` varchar(500) NOT NULL,
  `completed` tinyint(1) NOT NULL,
  `completed_at` datetime DEFAULT NULL,
  `completed_by_id` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `activity_comments`
--

CREATE TABLE `activity_comments` (
  `id` int(11) NOT NULL,
  `activity_id` int(11) NOT NULL,
  `author_id` int(11) NOT NULL,
  `content` text NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `activity_labels`
--

CREATE TABLE `activity_labels` (
  `id` int(11) NOT NULL,
  `activity_id` int(11) NOT NULL,
  `category_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `activity_tags`
--

CREATE TABLE `activity_tags` (
  `id` int(11) NOT NULL,
  `activity_id` int(11) NOT NULL,
  `tag_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `agent_memories`
--

CREATE TABLE `agent_memories` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `session_id` varchar(255) NOT NULL,
  `memory_type` varchar(50) NOT NULL,
  `key` varchar(255) NOT NULL,
  `value` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`value`)),
  `importance` int(11) DEFAULT 1,
  `expires_at` datetime DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `analysis_activities`
--

CREATE TABLE `analysis_activities` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `request_id` varchar(64) NOT NULL,
  `activity_id` varchar(50) NOT NULL,
  `epic` varchar(255) DEFAULT NULL,
  `title` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `priority` enum('baja','media','alta','critica') DEFAULT 'media',
  `owner_role` varchar(100) DEFAULT NULL,
  `estimated_days` int(11) DEFAULT NULL,
  `depends_on_json` text DEFAULT NULL,
  `kanban_status` enum('todo','in_progress','review','done') NOT NULL DEFAULT 'todo',
  `phase_id` varchar(50) DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `sort_order` int(11) DEFAULT NULL,
  `raw_json` longtext DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `analysis_modules`
--

CREATE TABLE `analysis_modules` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `request_id` varchar(64) NOT NULL,
  `module_name` varchar(100) NOT NULL,
  `module_status` enum('pending','running','completed','failed') NOT NULL DEFAULT 'completed',
  `input_json` longtext DEFAULT NULL,
  `output_json` longtext DEFAULT NULL,
  `started_at` datetime DEFAULT NULL,
  `completed_at` datetime DEFAULT NULL,
  `error_message` text DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `analysis_requests`
--

CREATE TABLE `analysis_requests` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `request_id` varchar(64) NOT NULL,
  `project_id` bigint(20) UNSIGNED DEFAULT NULL,
  `project_name` varchar(255) NOT NULL,
  `analysis_type` varchar(100) DEFAULT NULL,
  `language_code` varchar(10) NOT NULL DEFAULT 'es',
  `organization_name` varchar(255) DEFAULT NULL,
  `input_json` longtext NOT NULL,
  `status` enum('pending','running','completed','failed') NOT NULL DEFAULT 'pending',
  `workflow_version` varchar(20) NOT NULL,
  `execution_time_ms` int(11) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  `error_message` text DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `analysis_results`
--

CREATE TABLE `analysis_results` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `request_id` varchar(64) NOT NULL,
  `consolidated_json` longtext NOT NULL,
  `executive_summary` mediumtext DEFAULT NULL,
  `verdict_decision` varchar(100) DEFAULT NULL,
  `confidence_score` decimal(5,2) DEFAULT NULL,
  `market_score` decimal(5,2) DEFAULT NULL,
  `viability_score` decimal(5,2) DEFAULT NULL,
  `risk_score` decimal(5,2) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `analysis_risks`
--

CREATE TABLE `analysis_risks` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `request_id` varchar(64) NOT NULL,
  `risk_id` varchar(50) NOT NULL,
  `title` varchar(255) NOT NULL,
  `category` varchar(100) DEFAULT NULL,
  `probability` enum('baja','media','alta') DEFAULT 'media',
  `impact` enum('bajo','medio','alto','critico') DEFAULT 'medio',
  `mitigation` text DEFAULT NULL,
  `owner` varchar(100) DEFAULT NULL,
  `raw_json` longtext DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `analytics_events`
--

CREATE TABLE `analytics_events` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `event_type` varchar(100) NOT NULL,
  `event_category` varchar(50) DEFAULT NULL,
  `event_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`event_data`)),
  `metadata` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`metadata`)),
  `session_id` varchar(100) DEFAULT NULL,
  `project_id` int(11) DEFAULT NULL,
  `activity_id` int(11) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `audit_logs`
--

CREATE TABLE `audit_logs` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `action` varchar(100) NOT NULL,
  `entity_type` varchar(100) NOT NULL,
  `entity_id` varchar(100) DEFAULT NULL,
  `details` text DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` text DEFAULT NULL,
  `timestamp` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `business_model_canvases`
--

CREATE TABLE `business_model_canvases` (
  `id` int(11) NOT NULL,
  `project_id` int(11) NOT NULL,
  `key_partners` text DEFAULT NULL,
  `key_activities` text DEFAULT NULL,
  `key_resources` text DEFAULT NULL,
  `value_propositions` text DEFAULT NULL,
  `customer_relationships` text DEFAULT NULL,
  `channels` text DEFAULT NULL,
  `customer_segments` text DEFAULT NULL,
  `cost_structure` text DEFAULT NULL,
  `revenue_streams` text DEFAULT NULL,
  `problem_statement` text DEFAULT NULL,
  `differentiators` longtext DEFAULT NULL,
  `fit_score` decimal(5,2) DEFAULT NULL,
  `assumptions` longtext DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL
) ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categories`
--

CREATE TABLE `categories` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `company_id` int(11) NOT NULL,
  `description` text DEFAULT NULL,
  `color` varchar(7) DEFAULT NULL,
  `icon` varchar(50) DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `companies`
--

CREATE TABLE `companies` (
  `id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `slug` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
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
  `address` text DEFAULT NULL,
  `timezone` varchar(50) DEFAULT NULL,
  `subscription_plan` varchar(50) DEFAULT NULL,
  `max_users` int(11) DEFAULT NULL,
  `max_projects` int(11) DEFAULT NULL,
  `max_storage_gb` int(11) DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `trial_ends_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `conversation_flows`
--

CREATE TABLE `conversation_flows` (
  `id` int(11) NOT NULL,
  `flow_id` varchar(100) NOT NULL,
  `name` varchar(200) NOT NULL,
  `description` text DEFAULT NULL,
  `flow_type` varchar(50) DEFAULT 'linear',
  `flow_steps` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`flow_steps`)),
  `flow_rules` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`flow_rules`)),
  `flow_conditions` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`flow_conditions`)),
  `is_active` tinyint(1) DEFAULT 1,
  `version` varchar(20) DEFAULT '1.0',
  `priority` int(11) DEFAULT 1,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `conversation_messages`
--

CREATE TABLE `conversation_messages` (
  `id` int(11) NOT NULL,
  `session_id` varchar(255) NOT NULL,
  `message_type` enum('user','agent','system') NOT NULL,
  `content` text NOT NULL,
  `intent` varchar(100) DEFAULT NULL,
  `confidence` float DEFAULT NULL,
  `context_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`context_data`)),
  `metadata` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`metadata`)),
  `created_at` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `conversation_sessions`
--

CREATE TABLE `conversation_sessions` (
  `id` int(11) NOT NULL,
  `session_id` varchar(255) NOT NULL,
  `user_id` int(11) NOT NULL,
  `project_id` int(11) DEFAULT NULL,
  `session_type` varchar(50) DEFAULT 'general',
  `status` varchar(20) DEFAULT 'active',
  `context_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`context_data`)),
  `metadata` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`metadata`)),
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `last_activity` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `conversation_states`
--

CREATE TABLE `conversation_states` (
  `id` int(11) NOT NULL,
  `session_id` varchar(100) NOT NULL,
  `user_id` int(11) NOT NULL,
  `current_state` varchar(100) NOT NULL,
  `state_type` enum('active','paused','completed','abandoned','transitioning') DEFAULT 'active',
  `state_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`state_data`)),
  `primary_context` varchar(100) DEFAULT NULL,
  `secondary_contexts` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`secondary_contexts`)),
  `context_stack` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`context_stack`)),
  `current_intent` varchar(100) DEFAULT NULL,
  `intent_type` enum('primary','secondary','contextual','fallback') DEFAULT 'primary',
  `intent_confidence` float DEFAULT 0,
  `intent_history` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`intent_history`)),
  `flow_id` varchar(100) DEFAULT NULL,
  `flow_step` int(11) DEFAULT 0,
  `flow_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`flow_data`)),
  `flow_history` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`flow_history`)),
  `short_term_memory` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`short_term_memory`)),
  `long_term_memory` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`long_term_memory`)),
  `memory_priority` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`memory_priority`)),
  `active_threads` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`active_threads`)),
  `thread_priorities` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`thread_priorities`)),
  `thread_contexts` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`thread_contexts`)),
  `previous_state` varchar(100) DEFAULT NULL,
  `transition_reason` varchar(200) DEFAULT NULL,
  `transition_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`transition_data`)),
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `last_activity` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `conversation_threads`
--

CREATE TABLE `conversation_threads` (
  `id` int(11) NOT NULL,
  `session_id` varchar(100) NOT NULL,
  `thread_id` varchar(100) NOT NULL,
  `thread_type` varchar(50) DEFAULT 'main',
  `thread_context` varchar(100) DEFAULT NULL,
  `thread_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`thread_data`)),
  `is_active` tinyint(1) DEFAULT 1,
  `priority` int(11) DEFAULT 1,
  `last_activity` timestamp NULL DEFAULT current_timestamp(),
  `parent_thread_id` varchar(100) DEFAULT NULL,
  `related_threads` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`related_threads`)),
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `data_sources`
--

CREATE TABLE `data_sources` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `source_type` varchar(50) NOT NULL,
  `description` text DEFAULT NULL,
  `collection_frequency` varchar(50) DEFAULT 'daily',
  `is_active` tinyint(1) DEFAULT 1,
  `last_collection` timestamp NULL DEFAULT NULL,
  `data_schema` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`data_schema`)),
  `collection_parameters` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`collection_parameters`)),
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `document_generation_logs`
--

CREATE TABLE `document_generation_logs` (
  `id` int(11) NOT NULL,
  `project_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `document_type` varchar(50) NOT NULL,
  `status` varchar(20) NOT NULL,
  `error_message` text DEFAULT NULL,
  `generation_time` int(11) DEFAULT NULL,
  `tokens_used` int(11) DEFAULT NULL,
  `model_used` varchar(50) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `document_templates`
--

CREATE TABLE `document_templates` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `document_type` varchar(50) NOT NULL,
  `template_content` text NOT NULL,
  `variables` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`variables`)),
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `educational_categories`
--

CREATE TABLE `educational_categories` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `icon` varchar(100) DEFAULT NULL,
  `color` varchar(7) DEFAULT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `sort_order` int(11) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `educational_content`
--

CREATE TABLE `educational_content` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `content_type` enum('ARTICLE','VIDEO','PODCAST','INFOGRAPHIC','COURSE','WEBINAR') NOT NULL,
  `content_source` enum('INTERNAL','RSS_FEED','YOUTUBE','VIMEO','SPOTIFY','CUSTOM_API') NOT NULL,
  `source_url` varchar(500) DEFAULT NULL,
  `content_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`content_data`)),
  `difficulty` enum('BEGINNER','INTERMEDIATE','ADVANCED') DEFAULT NULL,
  `duration_minutes` int(11) DEFAULT NULL,
  `author` varchar(255) DEFAULT NULL,
  `instructor` varchar(255) DEFAULT NULL,
  `thumbnail_url` varchar(500) DEFAULT NULL,
  `tags` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`tags`)),
  `categories` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`categories`)),
  `status` enum('DRAFT','PUBLISHED','ARCHIVED','MODERATION') DEFAULT NULL,
  `published_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `moderated_by` int(11) DEFAULT NULL,
  `moderation_notes` text DEFAULT NULL,
  `view_count` int(11) DEFAULT NULL,
  `like_count` int(11) DEFAULT NULL,
  `bookmark_count` int(11) DEFAULT NULL,
  `rating` decimal(3,2) DEFAULT NULL,
  `rating_count` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `educational_tags`
--

CREATE TABLE `educational_tags` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `color` varchar(7) DEFAULT NULL,
  `usage_count` int(11) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `external_content_sources`
--

CREATE TABLE `external_content_sources` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `source_type` enum('RSS_FEED','YOUTUBE_CHANNEL','VIMEO_CHANNEL','SPOTIFY_SHOW','CUSTOM_API') NOT NULL,
  `source_url` varchar(500) NOT NULL,
  `api_key` varchar(255) DEFAULT NULL,
  `api_secret` varchar(255) DEFAULT NULL,
  `refresh_interval_minutes` int(11) DEFAULT NULL,
  `last_sync_at` datetime DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `auto_import` tinyint(1) DEFAULT NULL,
  `category_mapping` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`category_mapping`)),
  `tag_mapping` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`tag_mapping`)),
  `content_filters` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`content_filters`)),
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `generated_documents`
--

CREATE TABLE `generated_documents` (
  `id` int(11) NOT NULL,
  `project_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `document_type` varchar(50) NOT NULL,
  `title` varchar(255) NOT NULL,
  `content` text NOT NULL,
  `file_path` varchar(500) DEFAULT NULL,
  `file_size` int(11) DEFAULT NULL,
  `is_downloaded` tinyint(1) DEFAULT NULL,
  `download_count` int(11) DEFAULT NULL,
  `metadata_info` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`metadata_info`)),
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `learning_paths`
--

CREATE TABLE `learning_paths` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `description` text DEFAULT NULL,
  `category` varchar(100) DEFAULT NULL,
  `difficulty_level` varchar(20) DEFAULT 'beginner',
  `current_step` int(11) DEFAULT 0,
  `total_steps` int(11) DEFAULT 0,
  `completion_percentage` float DEFAULT 0,
  `content_items` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`content_items`)),
  `prerequisites` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`prerequisites`)),
  `is_active` tinyint(1) DEFAULT 1,
  `is_completed` tinyint(1) DEFAULT 0,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `completed_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `locations`
--

CREATE TABLE `locations` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `company_id` int(11) NOT NULL,
  `description` text DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `state` varchar(100) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `coordinates` varchar(50) DEFAULT NULL,
  `timezone` varchar(50) DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `official_documents`
--

CREATE TABLE `official_documents` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `document_type` enum('GUIDE','MANUAL','BROCHURE','POLICY','PROCEDURE','TEMPLATE','FORM') NOT NULL,
  `category` enum('HR','OPERATIONS','FINANCE','MARKETING','SALES','TECHNICAL','COMPLIANCE','TRAINING') NOT NULL,
  `file_path` varchar(500) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `file_size` bigint(20) NOT NULL,
  `file_type` varchar(50) NOT NULL,
  `version` varchar(20) DEFAULT NULL,
  `is_public` tinyint(1) DEFAULT NULL,
  `requires_approval` tinyint(1) DEFAULT NULL,
  `approval_status` enum('DRAFT','PENDING','APPROVED','REJECTED','ARCHIVED') DEFAULT NULL,
  `approved_by` int(11) DEFAULT NULL,
  `approved_at` datetime DEFAULT NULL,
  `expires_at` datetime DEFAULT NULL,
  `tags` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`tags`)),
  `document_metadata` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`document_metadata`)),
  `download_count` int(11) DEFAULT NULL,
  `view_count` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `proactive_suggestions`
--

CREATE TABLE `proactive_suggestions` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `suggestion_type` varchar(50) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `priority` int(11) DEFAULT 1,
  `category` varchar(100) DEFAULT NULL,
  `context_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`context_data`)),
  `action_url` varchar(500) DEFAULT NULL,
  `action_text` varchar(100) DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT 0,
  `is_dismissed` tinyint(1) DEFAULT 0,
  `expires_at` datetime DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `read_at` datetime DEFAULT NULL,
  `dismissed_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `projects`
--

CREATE TABLE `projects` (
  `id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `description` text DEFAULT NULL,
  `project_type` varchar(100) DEFAULT NULL,
  `analysis_type` varchar(100) DEFAULT NULL,
  `language_code` varchar(10) NOT NULL DEFAULT 'es',
  `workflow_version` varchar(20) DEFAULT NULL,
  `strategic_maturity` varchar(50) DEFAULT NULL,
  `complexity` varchar(50) DEFAULT NULL,
  `company_id` int(11) NOT NULL,
  `category_id` int(11) DEFAULT NULL,
  `location_id` int(11) DEFAULT NULL,
  `status_id` int(11) NOT NULL,
  `owner_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL,
  `last_analysis_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `project_activities`
--

CREATE TABLE `project_activities` (
  `id` int(11) NOT NULL,
  `activity_code` varchar(50) DEFAULT NULL,
  `title` varchar(200) NOT NULL,
  `description` text DEFAULT NULL,
  `epic` varchar(255) DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `priority` varchar(20) NOT NULL,
  `assignee_id` int(11) DEFAULT NULL,
  `owner_role` varchar(100) DEFAULT NULL,
  `estimated_days` int(11) DEFAULT NULL,
  `depends_on_json` longtext DEFAULT NULL,
  `kanban_status` varchar(50) NOT NULL DEFAULT 'todo',
  `phase_id` varchar(50) DEFAULT NULL,
  `sort_order` int(11) NOT NULL DEFAULT 0,
  `progress_percent` decimal(5,2) NOT NULL DEFAULT 0.00,
  `ai_generated` tinyint(1) NOT NULL DEFAULT 0,
  `source_request_id` varchar(64) DEFAULT NULL,
  `project_id` int(11) NOT NULL,
  `start_date` datetime DEFAULT NULL,
  `due_date` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL
) ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `project_agent_output`
--

CREATE TABLE `project_agent_output` (
  `id` int(11) NOT NULL,
  `project_id` int(11) NOT NULL,
  `request_id` varchar(64) DEFAULT NULL,
  `metadata` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'timestamp, workflow_version, modelo_usado' CHECK (json_valid(`metadata`)),
  `supervisor_output` longtext DEFAULT NULL,
  `conversacion` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'mensajes_totales, idea_negocio_original, historial_completo' CHECK (json_valid(`conversacion`)),
  `business_model_canvas` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'Estructura BMC del agente: segmentos_clientes, propuesta_valor, canales, etc.' CHECK (json_valid(`business_model_canvas`)),
  `estrategia_comercial` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'analisis_mercado, estrategia_precios, estrategia_marketing, estrategia_ventas' CHECK (json_valid(`estrategia_comercial`)),
  `roadmap_estrategico` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'fases, hitos, recursos_necesarios, cronograma_total_meses' CHECK (json_valid(`roadmap_estrategico`)),
  `analisis_financiero` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'inversion_inicial, proyecciones_3_anos, metricas_clave, viabilidad_financiera' CHECK (json_valid(`analisis_financiero`)),
  `analisis_riesgos` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'riesgos_identificados, nivel_riesgo_general, recomendaciones' CHECK (json_valid(`analisis_riesgos`)),
  `veredicto_final` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'decision, puntuacion_general, fortalezas, debilidades, recomendacion_estrategica, siguiente_paso' CHECK (json_valid(`veredicto_final`)),
  `plan_actividades` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'generado, actividades[], resumen' CHECK (json_valid(`plan_actividades`)),
  `kanban_json` longtext DEFAULT NULL,
  `gantt_json` longtext DEFAULT NULL,
  `summary_json` longtext DEFAULT NULL,
  `status` varchar(50) NOT NULL DEFAULT 'completed',
  `execution_time_ms` int(11) DEFAULT NULL,
  `modules_executed` longtext DEFAULT NULL,
  `modules_failed` longtext DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL ON UPDATE current_timestamp()
) ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `project_analisis_financiero`
--

CREATE TABLE `project_analisis_financiero` (
  `id` int(11) NOT NULL,
  `project_id` int(11) NOT NULL,
  `inversion_inicial` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`inversion_inicial`)),
  `proyecciones_3_anos` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`proyecciones_3_anos`)),
  `metricas_clave` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`metricas_clave`)),
  `viabilidad_financiera` varchar(50) DEFAULT NULL,
  `costo_operativo_mensual` decimal(14,2) DEFAULT NULL,
  `modelo_ingresos` varchar(100) DEFAULT NULL,
  `ingreso_mensual_esperado` decimal(14,2) DEFAULT NULL,
  `margen_estimado` decimal(8,2) DEFAULT NULL,
  `payback_meses` int(11) DEFAULT NULL,
  `observaciones` longtext DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL ON UPDATE current_timestamp()
) ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `project_analisis_riesgos`
--

CREATE TABLE `project_analisis_riesgos` (
  `id` int(11) NOT NULL,
  `project_id` int(11) NOT NULL,
  `nivel_riesgo_general` varchar(50) DEFAULT NULL,
  `recomendaciones` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'Array de strings' CHECK (json_valid(`recomendaciones`)),
  `assumptions` longtext DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL ON UPDATE current_timestamp()
) ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `project_analysis_module_runs`
--

CREATE TABLE `project_analysis_module_runs` (
  `id` bigint(20) NOT NULL,
  `run_id` bigint(20) NOT NULL,
  `request_id` varchar(64) NOT NULL,
  `project_id` int(11) NOT NULL,
  `module_name` varchar(100) NOT NULL,
  `module_order` int(11) NOT NULL DEFAULT 0,
  `module_status` varchar(50) NOT NULL DEFAULT 'pending',
  `input_json` longtext DEFAULT NULL,
  `output_json` longtext DEFAULT NULL,
  `error_message` text DEFAULT NULL,
  `started_at` datetime DEFAULT NULL,
  `completed_at` datetime DEFAULT NULL,
  `execution_time_ms` int(11) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `project_analysis_runs`
--

CREATE TABLE `project_analysis_runs` (
  `id` bigint(20) NOT NULL,
  `request_id` varchar(64) NOT NULL,
  `project_id` int(11) NOT NULL,
  `workflow_version` varchar(20) NOT NULL DEFAULT 'v5',
  `analysis_type` varchar(100) DEFAULT NULL,
  `language_code` varchar(10) NOT NULL DEFAULT 'es',
  `run_status` varchar(50) NOT NULL DEFAULT 'pending',
  `trigger_source` varchar(50) DEFAULT NULL,
  `input_json` longtext DEFAULT NULL,
  `normalized_input_json` longtext DEFAULT NULL,
  `supervisor_json` longtext DEFAULT NULL,
  `final_output_json` longtext DEFAULT NULL,
  `error_message` text DEFAULT NULL,
  `started_at` datetime DEFAULT NULL,
  `completed_at` datetime DEFAULT NULL,
  `execution_time_ms` int(11) DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `project_documents`
--

CREATE TABLE `project_documents` (
  `id` int(11) NOT NULL,
  `filename` varchar(255) NOT NULL,
  `original_filename` varchar(255) NOT NULL,
  `file_path` varchar(500) NOT NULL,
  `file_type` varchar(100) NOT NULL,
  `file_size` bigint(20) NOT NULL,
  `description` text DEFAULT NULL,
  `project_id` int(11) NOT NULL,
  `uploader_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `project_estrategia_comercial`
--

CREATE TABLE `project_estrategia_comercial` (
  `id` int(11) NOT NULL,
  `project_id` int(11) NOT NULL,
  `analisis_mercado` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`analisis_mercado`)),
  `estrategia_precios` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`estrategia_precios`)),
  `estrategia_marketing` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`estrategia_marketing`)),
  `estrategia_ventas` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`estrategia_ventas`)),
  `swot` longtext DEFAULT NULL,
  `objetivos_estrategicos` longtext DEFAULT NULL,
  `ventajas_competitivas` longtext DEFAULT NULL,
  `factores_criticos_exito` longtext DEFAULT NULL,
  `recomendaciones_estrategicas` longtext DEFAULT NULL,
  `assumptions` longtext DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL ON UPDATE current_timestamp()
) ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `project_riesgo`
--

CREATE TABLE `project_riesgo` (
  `id` int(11) NOT NULL,
  `risk_code` varchar(50) DEFAULT NULL,
  `project_id` int(11) NOT NULL,
  `categoria` varchar(100) DEFAULT NULL,
  `riesgo` varchar(500) DEFAULT NULL,
  `probabilidad` varchar(50) DEFAULT NULL,
  `impacto` varchar(50) DEFAULT NULL,
  `mitigacion` text DEFAULT NULL,
  `owner` varchar(100) DEFAULT NULL,
  `source_request_id` varchar(64) DEFAULT NULL,
  `orden` int(11) DEFAULT 0,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Riesgos identificados por proyecto; editable';

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `project_roadmap`
--

CREATE TABLE `project_roadmap` (
  `id` int(11) NOT NULL,
  `project_id` int(11) NOT NULL,
  `cronograma_total_meses` int(11) DEFAULT NULL,
  `fases` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'Array de {fase, duracion_meses, hitos[], recursos_necesarios[]}' CHECK (json_valid(`fases`)),
  `milestones` longtext DEFAULT NULL,
  `assumptions` longtext DEFAULT NULL,
  `project_start_date` date DEFAULT NULL,
  `project_end_date` date DEFAULT NULL,
  `gantt_json` longtext DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL ON UPDATE current_timestamp()
) ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `project_tags`
--

CREATE TABLE `project_tags` (
  `id` int(11) NOT NULL,
  `project_id` int(11) NOT NULL,
  `tag_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `project_veredicto`
--

CREATE TABLE `project_veredicto` (
  `id` int(11) NOT NULL,
  `project_id` int(11) NOT NULL,
  `decision` varchar(50) DEFAULT NULL,
  `confidence` decimal(5,2) DEFAULT NULL,
  `puntuacion_general` decimal(4,2) DEFAULT NULL,
  `fortalezas` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'Array de strings' CHECK (json_valid(`fortalezas`)),
  `debilidades` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'Array de strings' CHECK (json_valid(`debilidades`)),
  `recomendacion_estrategica` text DEFAULT NULL,
  `siguiente_paso` text DEFAULT NULL,
  `reasons` longtext DEFAULT NULL,
  `conditions_to_proceed` longtext DEFAULT NULL,
  `executive_summary` mediumtext DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL ON UPDATE current_timestamp()
) ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `recommendation_engine`
--

CREATE TABLE `recommendation_engine` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `recommendation_type` varchar(50) NOT NULL,
  `category` varchar(100) DEFAULT NULL,
  `priority` int(11) DEFAULT 1,
  `title` varchar(200) NOT NULL,
  `description` text DEFAULT NULL,
  `reasoning` text DEFAULT NULL,
  `expected_impact` float DEFAULT NULL,
  `data_sources` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`data_sources`)),
  `confidence_score` float DEFAULT 0,
  `action_url` varchar(500) DEFAULT NULL,
  `action_type` varchar(50) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `is_read` tinyint(1) DEFAULT 0,
  `is_applied` tinyint(1) DEFAULT 0,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `expires_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `recommendation_engines`
--

CREATE TABLE `recommendation_engines` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `recommendation_type` varchar(50) NOT NULL,
  `title` varchar(200) NOT NULL,
  `description` text DEFAULT NULL,
  `priority` int(11) DEFAULT 0,
  `category` varchar(100) DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT 0,
  `is_applied` tinyint(1) DEFAULT 0,
  `metadata` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`metadata`)),
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `state_transitions`
--

CREATE TABLE `state_transitions` (
  `id` int(11) NOT NULL,
  `session_id` varchar(100) NOT NULL,
  `from_state` varchar(100) NOT NULL,
  `to_state` varchar(100) NOT NULL,
  `transition_type` varchar(50) DEFAULT 'automatic',
  `transition_reason` varchar(200) DEFAULT NULL,
  `context_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`context_data`)),
  `intent_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`intent_data`)),
  `flow_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`flow_data`)),
  `created_at` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `statuses`
--

CREATE TABLE `statuses` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `company_id` int(11) NOT NULL,
  `description` text DEFAULT NULL,
  `color` varchar(7) DEFAULT NULL,
  `icon` varchar(50) DEFAULT NULL,
  `is_final` tinyint(1) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `suggestion_rules`
--

CREATE TABLE `suggestion_rules` (
  `id` int(11) NOT NULL,
  `rule_name` varchar(100) NOT NULL,
  `rule_type` varchar(50) NOT NULL,
  `conditions` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`conditions`)),
  `suggestion_template` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`suggestion_template`)),
  `is_active` tinyint(1) DEFAULT 1,
  `priority` int(11) DEFAULT 5,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tags`
--

CREATE TABLE `tags` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `company_id` int(11) NOT NULL,
  `description` text DEFAULT NULL,
  `color` varchar(7) DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `hashed_password` varchar(255) NOT NULL,
  `role` varchar(20) NOT NULL,
  `company_id` int(11) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user_analytics`
--

CREATE TABLE `user_analytics` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `login_frequency` float DEFAULT 0,
  `session_duration` float DEFAULT 0,
  `project_completion_rate` float DEFAULT 0,
  `activity_completion_rate` float DEFAULT 0,
  `content_consumption_rate` float DEFAULT 0,
  `learning_progress` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`learning_progress`)),
  `preferred_content_types` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`preferred_content_types`)),
  `project_success_rate` float DEFAULT 0,
  `business_model_complexity` float DEFAULT 0,
  `market_research_depth` float DEFAULT 0,
  `chatbot_usage_frequency` float DEFAULT 0,
  `feature_usage_patterns` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`feature_usage_patterns`)),
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user_context`
--

CREATE TABLE `user_context` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `business_domain` varchar(100) DEFAULT NULL,
  `experience_level` varchar(20) DEFAULT 'beginner',
  `interests` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`interests`)),
  `learning_goals` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`learning_goals`)),
  `preferred_content_types` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`preferred_content_types`)),
  `communication_style` varchar(50) DEFAULT 'formal',
  `time_zone` varchar(50) DEFAULT 'UTC',
  `language_preference` varchar(10) DEFAULT 'es',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user_contexts`
--

CREATE TABLE `user_contexts` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `current_project_id` int(11) DEFAULT NULL,
  `expertise_level` varchar(50) DEFAULT NULL,
  `business_sector` varchar(100) DEFAULT NULL,
  `preferred_language` varchar(10) DEFAULT NULL,
  `notification_preferences` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`notification_preferences`)),
  `learning_goals` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`learning_goals`)),
  `last_interaction` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user_suggestion_preferences`
--

CREATE TABLE `user_suggestion_preferences` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `notification_frequency` varchar(20) DEFAULT 'daily',
  `preferred_categories` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`preferred_categories`)),
  `max_suggestions_per_day` int(11) DEFAULT 10,
  `quiet_hours_start` varchar(5) DEFAULT '22:00',
  `quiet_hours_end` varchar(5) DEFAULT '08:00',
  `timezone` varchar(50) DEFAULT 'UTC',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `activity_assignees`
--
ALTER TABLE `activity_assignees`
  ADD PRIMARY KEY (`id`),
  ADD KEY `activity_id` (`activity_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `ix_activity_assignees_id` (`id`);

--
-- Indices de la tabla `activity_attachments`
--
ALTER TABLE `activity_attachments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `activity_id` (`activity_id`),
  ADD KEY `uploader_id` (`uploader_id`),
  ADD KEY `ix_activity_attachments_id` (`id`);

--
-- Indices de la tabla `activity_checklists`
--
ALTER TABLE `activity_checklists`
  ADD PRIMARY KEY (`id`),
  ADD KEY `activity_id` (`activity_id`),
  ADD KEY `ix_activity_checklists_id` (`id`);

--
-- Indices de la tabla `activity_checklist_items`
--
ALTER TABLE `activity_checklist_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `checklist_id` (`checklist_id`),
  ADD KEY `completed_by_id` (`completed_by_id`),
  ADD KEY `ix_activity_checklist_items_id` (`id`);

--
-- Indices de la tabla `activity_comments`
--
ALTER TABLE `activity_comments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `activity_id` (`activity_id`),
  ADD KEY `author_id` (`author_id`),
  ADD KEY `ix_activity_comments_id` (`id`);

--
-- Indices de la tabla `activity_labels`
--
ALTER TABLE `activity_labels`
  ADD PRIMARY KEY (`id`),
  ADD KEY `activity_id` (`activity_id`),
  ADD KEY `category_id` (`category_id`),
  ADD KEY `ix_activity_labels_id` (`id`);

--
-- Indices de la tabla `activity_tags`
--
ALTER TABLE `activity_tags`
  ADD PRIMARY KEY (`id`),
  ADD KEY `activity_id` (`activity_id`),
  ADD KEY `tag_id` (`tag_id`),
  ADD KEY `ix_activity_tags_id` (`id`);

--
-- Indices de la tabla `agent_memories`
--
ALTER TABLE `agent_memories`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_user_id` (`user_id`),
  ADD KEY `idx_session_id` (`session_id`(250)),
  ADD KEY `idx_memory_type` (`memory_type`),
  ADD KEY `idx_key` (`key`(250));

--
-- Indices de la tabla `analysis_activities`
--
ALTER TABLE `analysis_activities`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_analysis_activities_request_activity` (`request_id`,`activity_id`),
  ADD KEY `idx_analysis_activities_request_id` (`request_id`),
  ADD KEY `idx_analysis_activities_phase_id` (`phase_id`),
  ADD KEY `idx_analysis_activities_kanban_status` (`kanban_status`),
  ADD KEY `idx_analysis_activities_priority` (`priority`),
  ADD KEY `idx_analysis_activities_dates` (`start_date`,`end_date`);

--
-- Indices de la tabla `analysis_modules`
--
ALTER TABLE `analysis_modules`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_analysis_modules_request_module` (`request_id`,`module_name`),
  ADD KEY `idx_analysis_modules_status` (`module_status`),
  ADD KEY `idx_analysis_modules_created_at` (`created_at`);

--
-- Indices de la tabla `analysis_requests`
--
ALTER TABLE `analysis_requests`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_analysis_requests_request_id` (`request_id`),
  ADD KEY `idx_analysis_requests_project_id` (`project_id`),
  ADD KEY `idx_analysis_requests_status` (`status`),
  ADD KEY `idx_analysis_requests_created_at` (`created_at`),
  ADD KEY `idx_analysis_requests_project_name` (`project_name`);

--
-- Indices de la tabla `analysis_results`
--
ALTER TABLE `analysis_results`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_analysis_results_request_id` (`request_id`),
  ADD KEY `idx_analysis_results_verdict` (`verdict_decision`),
  ADD KEY `idx_analysis_results_created_at` (`created_at`);

--
-- Indices de la tabla `analysis_risks`
--
ALTER TABLE `analysis_risks`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_analysis_risks_request_risk` (`request_id`,`risk_id`),
  ADD KEY `idx_analysis_risks_category` (`category`),
  ADD KEY `idx_analysis_risks_probability` (`probability`),
  ADD KEY `idx_analysis_risks_impact` (`impact`);

--
-- Indices de la tabla `analytics_events`
--
ALTER TABLE `analytics_events`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_analytics_events_user_id` (`user_id`),
  ADD KEY `idx_analytics_events_type` (`event_type`),
  ADD KEY `idx_analytics_events_category` (`event_category`),
  ADD KEY `idx_analytics_events_created_at` (`created_at`);

--
-- Indices de la tabla `audit_logs`
--
ALTER TABLE `audit_logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `ix_audit_logs_id` (`id`);

--
-- Indices de la tabla `business_model_canvases`
--
ALTER TABLE `business_model_canvases`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `project_id` (`project_id`),
  ADD KEY `ix_business_model_canvases_id` (`id`);

--
-- Indices de la tabla `categories`
--
ALTER TABLE `categories`
  ADD PRIMARY KEY (`id`),
  ADD KEY `company_id` (`company_id`),
  ADD KEY `ix_categories_name` (`name`),
  ADD KEY `ix_categories_id` (`id`);

--
-- Indices de la tabla `companies`
--
ALTER TABLE `companies`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_companies_slug` (`slug`),
  ADD UNIQUE KEY `ix_companies_name` (`name`),
  ADD KEY `ix_companies_id` (`id`);

--
-- Indices de la tabla `conversation_flows`
--
ALTER TABLE `conversation_flows`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `flow_id` (`flow_id`),
  ADD KEY `idx_conversation_flows_flow_id` (`flow_id`),
  ADD KEY `idx_conversation_flows_active` (`is_active`);

--
-- Indices de la tabla `conversation_messages`
--
ALTER TABLE `conversation_messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_session_id` (`session_id`),
  ADD KEY `idx_message_type` (`message_type`),
  ADD KEY `idx_created_at` (`created_at`);

--
-- Indices de la tabla `conversation_sessions`
--
ALTER TABLE `conversation_sessions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `session_id` (`session_id`),
  ADD KEY `idx_session_id` (`session_id`),
  ADD KEY `idx_user_id` (`user_id`),
  ADD KEY `idx_project_id` (`project_id`),
  ADD KEY `idx_status` (`status`);

--
-- Indices de la tabla `conversation_states`
--
ALTER TABLE `conversation_states`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_conversation_states_session_id` (`session_id`),
  ADD KEY `idx_conversation_states_user_id` (`user_id`),
  ADD KEY `idx_conversation_states_current_state` (`current_state`),
  ADD KEY `idx_conversation_states_state_type` (`state_type`);

--
-- Indices de la tabla `conversation_threads`
--
ALTER TABLE `conversation_threads`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_conversation_threads_session_id` (`session_id`),
  ADD KEY `idx_conversation_threads_thread_id` (`thread_id`),
  ADD KEY `idx_conversation_threads_active` (`is_active`);

--
-- Indices de la tabla `data_sources`
--
ALTER TABLE `data_sources`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_data_sources_type` (`source_type`),
  ADD KEY `idx_data_sources_active` (`is_active`);

--
-- Indices de la tabla `document_generation_logs`
--
ALTER TABLE `document_generation_logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `project_id` (`project_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `ix_document_generation_logs_id` (`id`);

--
-- Indices de la tabla `document_templates`
--
ALTER TABLE `document_templates`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_document_templates_id` (`id`);

--
-- Indices de la tabla `educational_categories`
--
ALTER TABLE `educational_categories`
  ADD PRIMARY KEY (`id`),
  ADD KEY `parent_id` (`parent_id`),
  ADD KEY `ix_educational_categories_id` (`id`);

--
-- Indices de la tabla `educational_content`
--
ALTER TABLE `educational_content`
  ADD PRIMARY KEY (`id`),
  ADD KEY `created_by` (`created_by`),
  ADD KEY `moderated_by` (`moderated_by`),
  ADD KEY `ix_educational_content_id` (`id`);

--
-- Indices de la tabla `educational_tags`
--
ALTER TABLE `educational_tags`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`),
  ADD KEY `ix_educational_tags_id` (`id`);

--
-- Indices de la tabla `external_content_sources`
--
ALTER TABLE `external_content_sources`
  ADD PRIMARY KEY (`id`),
  ADD KEY `created_by` (`created_by`),
  ADD KEY `ix_external_content_sources_id` (`id`);

--
-- Indices de la tabla `generated_documents`
--
ALTER TABLE `generated_documents`
  ADD PRIMARY KEY (`id`),
  ADD KEY `project_id` (`project_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `ix_generated_documents_id` (`id`);

--
-- Indices de la tabla `learning_paths`
--
ALTER TABLE `learning_paths`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_learning_paths_user_id` (`user_id`),
  ADD KEY `idx_learning_paths_category` (`category`),
  ADD KEY `idx_learning_paths_active` (`is_active`);

--
-- Indices de la tabla `locations`
--
ALTER TABLE `locations`
  ADD PRIMARY KEY (`id`),
  ADD KEY `company_id` (`company_id`),
  ADD KEY `ix_locations_id` (`id`),
  ADD KEY `ix_locations_name` (`name`);

--
-- Indices de la tabla `official_documents`
--
ALTER TABLE `official_documents`
  ADD PRIMARY KEY (`id`),
  ADD KEY `approved_by` (`approved_by`),
  ADD KEY `created_by` (`created_by`),
  ADD KEY `ix_official_documents_id` (`id`);

--
-- Indices de la tabla `proactive_suggestions`
--
ALTER TABLE `proactive_suggestions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_user_id` (`user_id`),
  ADD KEY `idx_suggestion_type` (`suggestion_type`),
  ADD KEY `idx_category` (`category`),
  ADD KEY `idx_priority` (`priority`),
  ADD KEY `idx_is_read` (`is_read`),
  ADD KEY `idx_is_dismissed` (`is_dismissed`),
  ADD KEY `idx_created_at` (`created_at`);

--
-- Indices de la tabla `projects`
--
ALTER TABLE `projects`
  ADD PRIMARY KEY (`id`),
  ADD KEY `company_id` (`company_id`),
  ADD KEY `category_id` (`category_id`),
  ADD KEY `location_id` (`location_id`),
  ADD KEY `status_id` (`status_id`),
  ADD KEY `owner_id` (`owner_id`),
  ADD KEY `ix_projects_id` (`id`),
  ADD KEY `idx_projects_project_type` (`project_type`),
  ADD KEY `idx_projects_analysis_type` (`analysis_type`),
  ADD KEY `idx_projects_workflow_version` (`workflow_version`),
  ADD KEY `idx_projects_last_analysis_at` (`last_analysis_at`);

--
-- Indices de la tabla `project_activities`
--
ALTER TABLE `project_activities`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_project_activities_code_per_project` (`project_id`,`activity_code`),
  ADD KEY `assignee_id` (`assignee_id`),
  ADD KEY `project_id` (`project_id`),
  ADD KEY `ix_project_activities_id` (`id`),
  ADD KEY `idx_project_activities_phase` (`project_id`,`phase_id`),
  ADD KEY `idx_project_activities_kanban` (`project_id`,`kanban_status`),
  ADD KEY `idx_project_activities_source_request` (`source_request_id`);

--
-- Indices de la tabla `project_agent_output`
--
ALTER TABLE `project_agent_output`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_project_agent_output_project_id` (`project_id`),
  ADD UNIQUE KEY `uq_project_agent_output_request_id` (`request_id`),
  ADD KEY `ix_project_agent_output_project_id` (`project_id`),
  ADD KEY `ix_project_agent_output_updated_at` (`updated_at`),
  ADD KEY `idx_project_agent_output_status` (`status`);

--
-- Indices de la tabla `project_analisis_financiero`
--
ALTER TABLE `project_analisis_financiero`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_project_analisis_financiero_project_id` (`project_id`);

--
-- Indices de la tabla `project_analisis_riesgos`
--
ALTER TABLE `project_analisis_riesgos`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_project_analisis_riesgos_project_id` (`project_id`);

--
-- Indices de la tabla `project_analysis_module_runs`
--
ALTER TABLE `project_analysis_module_runs`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_project_analysis_module_runs_unique` (`run_id`,`module_name`),
  ADD KEY `idx_project_analysis_module_runs_request` (`request_id`),
  ADD KEY `idx_project_analysis_module_runs_project` (`project_id`),
  ADD KEY `idx_project_analysis_module_runs_status` (`module_status`);

--
-- Indices de la tabla `project_analysis_runs`
--
ALTER TABLE `project_analysis_runs`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_project_analysis_runs_request_id` (`request_id`),
  ADD KEY `idx_project_analysis_runs_project` (`project_id`),
  ADD KEY `idx_project_analysis_runs_status` (`run_status`),
  ADD KEY `idx_project_analysis_runs_started_at` (`started_at`),
  ADD KEY `fk_project_analysis_runs_created_by` (`created_by`);

--
-- Indices de la tabla `project_documents`
--
ALTER TABLE `project_documents`
  ADD PRIMARY KEY (`id`),
  ADD KEY `project_id` (`project_id`),
  ADD KEY `uploader_id` (`uploader_id`),
  ADD KEY `ix_project_documents_id` (`id`);

--
-- Indices de la tabla `project_estrategia_comercial`
--
ALTER TABLE `project_estrategia_comercial`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_project_estrategia_comercial_project_id` (`project_id`);

--
-- Indices de la tabla `project_riesgo`
--
ALTER TABLE `project_riesgo`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_project_riesgo_code_per_project` (`project_id`,`risk_code`),
  ADD KEY `ix_project_riesgo_project_id` (`project_id`),
  ADD KEY `idx_project_riesgo_source_request` (`source_request_id`);

--
-- Indices de la tabla `project_roadmap`
--
ALTER TABLE `project_roadmap`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_project_roadmap_project_id` (`project_id`);

--
-- Indices de la tabla `project_tags`
--
ALTER TABLE `project_tags`
  ADD PRIMARY KEY (`id`),
  ADD KEY `project_id` (`project_id`),
  ADD KEY `tag_id` (`tag_id`),
  ADD KEY `ix_project_tags_id` (`id`);

--
-- Indices de la tabla `project_veredicto`
--
ALTER TABLE `project_veredicto`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_project_veredicto_project_id` (`project_id`);

--
-- Indices de la tabla `recommendation_engine`
--
ALTER TABLE `recommendation_engine`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_recommendation_user_id` (`user_id`),
  ADD KEY `idx_recommendation_type` (`recommendation_type`),
  ADD KEY `idx_recommendation_active` (`is_active`);

--
-- Indices de la tabla `recommendation_engines`
--
ALTER TABLE `recommendation_engines`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indices de la tabla `state_transitions`
--
ALTER TABLE `state_transitions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_state_transitions_session_id` (`session_id`),
  ADD KEY `idx_state_transitions_from_state` (`from_state`),
  ADD KEY `idx_state_transitions_to_state` (`to_state`),
  ADD KEY `idx_state_transitions_created_at` (`created_at`);

--
-- Indices de la tabla `statuses`
--
ALTER TABLE `statuses`
  ADD PRIMARY KEY (`id`),
  ADD KEY `company_id` (`company_id`),
  ADD KEY `ix_statuses_name` (`name`),
  ADD KEY `ix_statuses_id` (`id`);

--
-- Indices de la tabla `suggestion_rules`
--
ALTER TABLE `suggestion_rules`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `rule_name` (`rule_name`),
  ADD KEY `idx_rule_name` (`rule_name`),
  ADD KEY `idx_rule_type` (`rule_type`),
  ADD KEY `idx_is_active` (`is_active`);

--
-- Indices de la tabla `tags`
--
ALTER TABLE `tags`
  ADD PRIMARY KEY (`id`),
  ADD KEY `company_id` (`company_id`),
  ADD KEY `ix_tags_name` (`name`),
  ADD KEY `ix_tags_id` (`id`);

--
-- Indices de la tabla `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_users_email` (`email`),
  ADD UNIQUE KEY `ix_users_username` (`username`),
  ADD KEY `company_id` (`company_id`),
  ADD KEY `ix_users_id` (`id`);

--
-- Indices de la tabla `user_analytics`
--
ALTER TABLE `user_analytics`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`),
  ADD KEY `idx_user_analytics_user_id` (`user_id`);

--
-- Indices de la tabla `user_context`
--
ALTER TABLE `user_context`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`),
  ADD KEY `idx_user_id` (`user_id`),
  ADD KEY `idx_business_domain` (`business_domain`),
  ADD KEY `idx_experience_level` (`experience_level`);

--
-- Indices de la tabla `user_contexts`
--
ALTER TABLE `user_contexts`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`),
  ADD KEY `current_project_id` (`current_project_id`),
  ADD KEY `ix_user_contexts_id` (`id`);

--
-- Indices de la tabla `user_suggestion_preferences`
--
ALTER TABLE `user_suggestion_preferences`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`),
  ADD KEY `idx_user_id` (`user_id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `activity_assignees`
--
ALTER TABLE `activity_assignees`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `activity_attachments`
--
ALTER TABLE `activity_attachments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `activity_checklists`
--
ALTER TABLE `activity_checklists`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `activity_checklist_items`
--
ALTER TABLE `activity_checklist_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `activity_comments`
--
ALTER TABLE `activity_comments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `activity_labels`
--
ALTER TABLE `activity_labels`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `activity_tags`
--
ALTER TABLE `activity_tags`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `agent_memories`
--
ALTER TABLE `agent_memories`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `analysis_activities`
--
ALTER TABLE `analysis_activities`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `analysis_modules`
--
ALTER TABLE `analysis_modules`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `analysis_requests`
--
ALTER TABLE `analysis_requests`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `analysis_results`
--
ALTER TABLE `analysis_results`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `analysis_risks`
--
ALTER TABLE `analysis_risks`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `analytics_events`
--
ALTER TABLE `analytics_events`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `audit_logs`
--
ALTER TABLE `audit_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `business_model_canvases`
--
ALTER TABLE `business_model_canvases`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `categories`
--
ALTER TABLE `categories`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `companies`
--
ALTER TABLE `companies`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `conversation_flows`
--
ALTER TABLE `conversation_flows`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `conversation_messages`
--
ALTER TABLE `conversation_messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `conversation_sessions`
--
ALTER TABLE `conversation_sessions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `conversation_states`
--
ALTER TABLE `conversation_states`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `conversation_threads`
--
ALTER TABLE `conversation_threads`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `data_sources`
--
ALTER TABLE `data_sources`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `document_generation_logs`
--
ALTER TABLE `document_generation_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `document_templates`
--
ALTER TABLE `document_templates`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `educational_categories`
--
ALTER TABLE `educational_categories`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `educational_content`
--
ALTER TABLE `educational_content`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `educational_tags`
--
ALTER TABLE `educational_tags`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `external_content_sources`
--
ALTER TABLE `external_content_sources`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `generated_documents`
--
ALTER TABLE `generated_documents`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `learning_paths`
--
ALTER TABLE `learning_paths`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `locations`
--
ALTER TABLE `locations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `official_documents`
--
ALTER TABLE `official_documents`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `proactive_suggestions`
--
ALTER TABLE `proactive_suggestions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `projects`
--
ALTER TABLE `projects`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `project_activities`
--
ALTER TABLE `project_activities`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `project_agent_output`
--
ALTER TABLE `project_agent_output`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `project_analisis_financiero`
--
ALTER TABLE `project_analisis_financiero`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `project_analisis_riesgos`
--
ALTER TABLE `project_analisis_riesgos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `project_analysis_module_runs`
--
ALTER TABLE `project_analysis_module_runs`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `project_analysis_runs`
--
ALTER TABLE `project_analysis_runs`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `project_documents`
--
ALTER TABLE `project_documents`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `project_estrategia_comercial`
--
ALTER TABLE `project_estrategia_comercial`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `project_riesgo`
--
ALTER TABLE `project_riesgo`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `project_roadmap`
--
ALTER TABLE `project_roadmap`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `project_tags`
--
ALTER TABLE `project_tags`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `project_veredicto`
--
ALTER TABLE `project_veredicto`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `recommendation_engine`
--
ALTER TABLE `recommendation_engine`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `recommendation_engines`
--
ALTER TABLE `recommendation_engines`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `state_transitions`
--
ALTER TABLE `state_transitions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `statuses`
--
ALTER TABLE `statuses`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `suggestion_rules`
--
ALTER TABLE `suggestion_rules`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `tags`
--
ALTER TABLE `tags`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `user_analytics`
--
ALTER TABLE `user_analytics`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `user_context`
--
ALTER TABLE `user_context`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `user_contexts`
--
ALTER TABLE `user_contexts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `user_suggestion_preferences`
--
ALTER TABLE `user_suggestion_preferences`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `analysis_activities`
--
ALTER TABLE `analysis_activities`
  ADD CONSTRAINT `fk_analysis_activities_request` FOREIGN KEY (`request_id`) REFERENCES `analysis_requests` (`request_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `analysis_modules`
--
ALTER TABLE `analysis_modules`
  ADD CONSTRAINT `fk_analysis_modules_request` FOREIGN KEY (`request_id`) REFERENCES `analysis_requests` (`request_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `analysis_results`
--
ALTER TABLE `analysis_results`
  ADD CONSTRAINT `fk_analysis_results_request` FOREIGN KEY (`request_id`) REFERENCES `analysis_requests` (`request_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `analysis_risks`
--
ALTER TABLE `analysis_risks`
  ADD CONSTRAINT `fk_analysis_risks_request` FOREIGN KEY (`request_id`) REFERENCES `analysis_requests` (`request_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `business_model_canvases`
--
ALTER TABLE `business_model_canvases`
  ADD CONSTRAINT `fk_bmc_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `document_generation_logs`
--
ALTER TABLE `document_generation_logs`
  ADD CONSTRAINT `fk_document_generation_logs_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_document_generation_logs_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Filtros para la tabla `generated_documents`
--
ALTER TABLE `generated_documents`
  ADD CONSTRAINT `fk_generated_documents_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_generated_documents_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Filtros para la tabla `projects`
--
ALTER TABLE `projects`
  ADD CONSTRAINT `fk_projects_category` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`),
  ADD CONSTRAINT `fk_projects_company` FOREIGN KEY (`company_id`) REFERENCES `companies` (`id`),
  ADD CONSTRAINT `fk_projects_location` FOREIGN KEY (`location_id`) REFERENCES `locations` (`id`),
  ADD CONSTRAINT `fk_projects_owner` FOREIGN KEY (`owner_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `fk_projects_status` FOREIGN KEY (`status_id`) REFERENCES `statuses` (`id`);

--
-- Filtros para la tabla `project_activities`
--
ALTER TABLE `project_activities`
  ADD CONSTRAINT `fk_project_activities_assignee` FOREIGN KEY (`assignee_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `fk_project_activities_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `project_agent_output`
--
ALTER TABLE `project_agent_output`
  ADD CONSTRAINT `fk_project_agent_output_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `project_analisis_financiero`
--
ALTER TABLE `project_analisis_financiero`
  ADD CONSTRAINT `fk_project_analisis_financiero_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `project_analisis_riesgos`
--
ALTER TABLE `project_analisis_riesgos`
  ADD CONSTRAINT `fk_project_analisis_riesgos_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `project_analysis_module_runs`
--
ALTER TABLE `project_analysis_module_runs`
  ADD CONSTRAINT `fk_project_analysis_module_runs_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_project_analysis_module_runs_run` FOREIGN KEY (`run_id`) REFERENCES `project_analysis_runs` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `project_analysis_runs`
--
ALTER TABLE `project_analysis_runs`
  ADD CONSTRAINT `fk_project_analysis_runs_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `fk_project_analysis_runs_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `project_documents`
--
ALTER TABLE `project_documents`
  ADD CONSTRAINT `fk_project_documents_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_project_documents_uploader` FOREIGN KEY (`uploader_id`) REFERENCES `users` (`id`);

--
-- Filtros para la tabla `project_estrategia_comercial`
--
ALTER TABLE `project_estrategia_comercial`
  ADD CONSTRAINT `fk_project_estrategia_comercial_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `project_riesgo`
--
ALTER TABLE `project_riesgo`
  ADD CONSTRAINT `fk_project_riesgo_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `project_roadmap`
--
ALTER TABLE `project_roadmap`
  ADD CONSTRAINT `fk_project_roadmap_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `project_tags`
--
ALTER TABLE `project_tags`
  ADD CONSTRAINT `fk_project_tags_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_project_tags_tag` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `project_veredicto`
--
ALTER TABLE `project_veredicto`
  ADD CONSTRAINT `fk_project_veredicto_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
