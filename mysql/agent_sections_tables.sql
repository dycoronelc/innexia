-- ============================================================================
-- Tablas canónicas por sección del agente IA (estrategia, roadmap, análisis, riesgos, veredicto)
-- Fecha: 2026-03
-- Descripción: Igual que business_model_canvases para el BMC, cada sección del JSON
--              del agente tiene una tabla como fuente única para visualización y edición.
--              project_agent_output conserva el JSON crudo como auditoría; al guardar
--              salida del agente se sincroniza cada sección a su tabla.
-- ============================================================================

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET NAMES utf8mb4;

-- --------------------------------------------------------
-- Estrategia comercial (analisis_mercado, estrategia_precios, estrategia_marketing, estrategia_ventas)
-- --------------------------------------------------------
DROP TABLE IF EXISTS `project_estrategia_comercial`;
CREATE TABLE `project_estrategia_comercial` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_id` int NOT NULL,
  `analisis_mercado` json DEFAULT NULL,
  `estrategia_precios` json DEFAULT NULL,
  `estrategia_marketing` json DEFAULT NULL,
  `estrategia_ventas` json DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_project_estrategia_comercial_project_id` (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Estrategia comercial editable; sincronizada desde agente';

-- --------------------------------------------------------
-- Roadmap estratégico (fases, cronograma_total_meses)
-- --------------------------------------------------------
DROP TABLE IF EXISTS `project_roadmap`;
CREATE TABLE `project_roadmap` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_id` int NOT NULL,
  `cronograma_total_meses` int DEFAULT NULL,
  `fases` json DEFAULT NULL COMMENT 'Array de {fase, duracion_meses, hitos[], recursos_necesarios[]}',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_project_roadmap_project_id` (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Roadmap editable; sincronizado desde agente';

-- --------------------------------------------------------
-- Análisis financiero (inversion_inicial, proyecciones_3_anos, metricas_clave, viabilidad_financiera)
-- --------------------------------------------------------
DROP TABLE IF EXISTS `project_analisis_financiero`;
CREATE TABLE `project_analisis_financiero` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_id` int NOT NULL,
  `inversion_inicial` json DEFAULT NULL,
  `proyecciones_3_anos` json DEFAULT NULL,
  `metricas_clave` json DEFAULT NULL,
  `viabilidad_financiera` varchar(50) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_project_analisis_financiero_project_id` (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Análisis financiero editable; sincronizado desde agente';

-- --------------------------------------------------------
-- Riesgos: cabecera (nivel_riesgo_general, recomendaciones) + filas por riesgo
-- --------------------------------------------------------
DROP TABLE IF EXISTS `project_riesgo`;
DROP TABLE IF EXISTS `project_analisis_riesgos`;
CREATE TABLE `project_analisis_riesgos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_id` int NOT NULL,
  `nivel_riesgo_general` varchar(50) DEFAULT NULL,
  `recomendaciones` json DEFAULT NULL COMMENT 'Array de strings',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_project_analisis_riesgos_project_id` (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Cabecera de análisis de riesgos; riesgos en project_riesgo';

CREATE TABLE `project_riesgo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_id` int NOT NULL,
  `categoria` varchar(100) DEFAULT NULL,
  `riesgo` varchar(500) DEFAULT NULL,
  `probabilidad` varchar(50) DEFAULT NULL,
  `impacto` varchar(50) DEFAULT NULL,
  `mitigacion` text,
  `orden` int DEFAULT 0,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_project_riesgo_project_id` (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Riesgos identificados por proyecto; editable';

-- --------------------------------------------------------
-- Veredicto final (decision, puntuacion, fortalezas, debilidades, recomendacion, siguiente_paso)
-- --------------------------------------------------------
DROP TABLE IF EXISTS `project_veredicto`;
CREATE TABLE `project_veredicto` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_id` int NOT NULL,
  `decision` varchar(50) DEFAULT NULL,
  `puntuacion_general` decimal(4,2) DEFAULT NULL,
  `fortalezas` json DEFAULT NULL COMMENT 'Array de strings',
  `debilidades` json DEFAULT NULL COMMENT 'Array de strings',
  `recomendacion_estrategica` text,
  `siguiente_paso` text,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_project_veredicto_project_id` (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Veredicto editable; un futuro agente puede re-analizar y actualizar';

COMMIT;
