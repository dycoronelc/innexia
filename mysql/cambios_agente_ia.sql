-- ============================================================================
-- Migración: Datos del Agente IA (n8n) - Compatible con estructura salidaAgente.json
-- Fecha: 2026-03
-- Descripción: Tabla para almacenar la salida completa del agente de IA que
--              se integrará vía n8n (BMC, estrategia comercial, roadmap,
--              análisis financiero, riesgos, veredicto y plan de actividades).
-- ============================================================================

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET NAMES utf8mb4;

-- --------------------------------------------------------
-- Tabla: project_agent_output
-- Una fila por proyecto con la última salida del agente.
-- Si el proyecto se crea desde cero con el agente, primero se crea el
-- proyecto y luego se inserta aquí.
-- --------------------------------------------------------

DROP TABLE IF EXISTS `project_agent_output`;
CREATE TABLE `project_agent_output` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_id` int NOT NULL,
  `metadata` json DEFAULT NULL COMMENT 'timestamp, workflow_version, modelo_usado',
  `conversacion` json DEFAULT NULL COMMENT 'mensajes_totales, idea_negocio_original, historial_completo',
-- Columna business_model_canvas: copia en JSON de lo que envió el agente (auditoría).
-- La visualización y edición del BMC usan la tabla business_model_canvases; al guardar
-- salida del agente se sincronizan los datos del JSON a esa tabla. Ver docs/AGENT_BMC_SYNC.md.
  `business_model_canvas` json DEFAULT NULL COMMENT 'Copia original del agente; BMC editable en business_model_canvases',
  `estrategia_comercial` json DEFAULT NULL COMMENT 'analisis_mercado, estrategia_precios, estrategia_marketing, estrategia_ventas',
  `roadmap_estrategico` json DEFAULT NULL COMMENT 'fases, hitos, recursos_necesarios, cronograma_total_meses',
  `analisis_financiero` json DEFAULT NULL COMMENT 'inversion_inicial, proyecciones_3_anos, metricas_clave, viabilidad_financiera',
  `analisis_riesgos` json DEFAULT NULL COMMENT 'riesgos_identificados, nivel_riesgo_general, recomendaciones',
  `veredicto_final` json DEFAULT NULL COMMENT 'decision, puntuacion_general, fortalezas, debilidades, recomendacion_estrategica, siguiente_paso',
  `plan_actividades` json DEFAULT NULL COMMENT 'generado, actividades[], resumen',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_project_agent_output_project_id` (`project_id`),
  KEY `ix_project_agent_output_project_id` (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Salida del agente IA (n8n) por proyecto';

-- Opcional: si en el futuro projects pasa a InnoDB, descomentar:
-- ALTER TABLE project_agent_output ADD CONSTRAINT fk_project_agent_output_project
--   FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE ON UPDATE CASCADE;

-- --------------------------------------------------------
-- Índice para consultas por fecha de actualización
-- --------------------------------------------------------
CREATE INDEX `ix_project_agent_output_updated_at` ON `project_agent_output` (`updated_at`);

COMMIT;
