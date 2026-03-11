import pymysql
import json
from datetime import datetime

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def consolidate_databases():
    """Consolidar todas las tablas en la base de datos bmc"""
    connection = None
    try:
        # Conectar a la base de datos bmc
        connection = pymysql.connect(**DB_CONFIG, database='bmc')
        cursor = connection.cursor()
        
        print("🔄 Consolidando bases de datos...")
        print("📊 Migrando tablas del agente inteligente a la base de datos 'bmc'")
        
        # 1. Tabla agent_memories (ya existe en bmc, verificar estructura)
        print("\n1. Verificando tabla agent_memories...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_memories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                session_id VARCHAR(255) NOT NULL,
                memory_type VARCHAR(50) NOT NULL,
                `key` VARCHAR(255) NOT NULL,
                value JSON NOT NULL,
                importance INT DEFAULT 1,
                expires_at DATETIME DEFAULT NULL,
                created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_user_id (user_id),
                INDEX idx_session_id (session_id(250)),
                INDEX idx_memory_type (memory_type),
                INDEX idx_key (`key`(250))
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # 2. Tabla conversation_sessions
        print("2. Creando tabla conversation_sessions...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL UNIQUE,
                user_id INT NOT NULL,
                project_id INT DEFAULT NULL,
                session_type VARCHAR(50) DEFAULT 'general',
                status VARCHAR(20) DEFAULT 'active',
                context_data JSON DEFAULT NULL,
                metadata JSON DEFAULT NULL,
                created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                last_activity TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_session_id (session_id),
                INDEX idx_user_id (user_id),
                INDEX idx_project_id (project_id),
                INDEX idx_status (status)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # 3. Tabla conversation_messages
        print("3. Creando tabla conversation_messages...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                message_type ENUM('user', 'agent', 'system') NOT NULL,
                content TEXT NOT NULL,
                intent VARCHAR(100) DEFAULT NULL,
                confidence FLOAT DEFAULT NULL,
                context_data JSON DEFAULT NULL,
                metadata JSON DEFAULT NULL,
                created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_session_id (session_id),
                INDEX idx_message_type (message_type),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # 4. Tabla user_context
        print("4. Creando tabla user_context...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_context (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL UNIQUE,
                business_domain VARCHAR(100) DEFAULT NULL,
                experience_level VARCHAR(20) DEFAULT 'beginner',
                interests JSON DEFAULT NULL,
                learning_goals JSON DEFAULT NULL,
                preferred_content_types JSON DEFAULT NULL,
                communication_style VARCHAR(50) DEFAULT 'formal',
                time_zone VARCHAR(50) DEFAULT 'UTC',
                language_preference VARCHAR(10) DEFAULT 'es',
                created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_user_id (user_id),
                INDEX idx_business_domain (business_domain),
                INDEX idx_experience_level (experience_level)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # 5. Tabla proactive_suggestions (ya existe en bmc, verificar estructura)
        print("5. Verificando tabla proactive_suggestions...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS proactive_suggestions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                suggestion_type VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                priority INT DEFAULT 1,
                category VARCHAR(100) DEFAULT NULL,
                context_data JSON DEFAULT NULL,
                action_url VARCHAR(500) DEFAULT NULL,
                action_text VARCHAR(100) DEFAULT NULL,
                is_read TINYINT(1) DEFAULT 0,
                is_dismissed TINYINT(1) DEFAULT 0,
                expires_at DATETIME DEFAULT NULL,
                created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                read_at DATETIME DEFAULT NULL,
                dismissed_at DATETIME DEFAULT NULL,
                INDEX idx_user_id (user_id),
                INDEX idx_suggestion_type (suggestion_type),
                INDEX idx_category (category),
                INDEX idx_priority (priority),
                INDEX idx_is_read (is_read),
                INDEX idx_is_dismissed (is_dismissed),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # 6. Tabla suggestion_rules (ya existe en bmc, verificar estructura)
        print("6. Verificando tabla suggestion_rules...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suggestion_rules (
                id INT AUTO_INCREMENT PRIMARY KEY,
                rule_name VARCHAR(100) NOT NULL UNIQUE,
                rule_type VARCHAR(50) NOT NULL,
                conditions JSON NOT NULL,
                suggestion_template JSON NOT NULL,
                is_active TINYINT(1) DEFAULT 1,
                priority INT DEFAULT 5,
                created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_rule_name (rule_name),
                INDEX idx_rule_type (rule_type),
                INDEX idx_is_active (is_active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # 7. Tabla user_suggestion_preferences (ya existe en bmc, verificar estructura)
        print("7. Verificando tabla user_suggestion_preferences...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_suggestion_preferences (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL UNIQUE,
                notification_frequency VARCHAR(20) DEFAULT 'daily',
                preferred_categories JSON DEFAULT NULL,
                max_suggestions_per_day INT DEFAULT 10,
                quiet_hours_start VARCHAR(5) DEFAULT '22:00',
                quiet_hours_end VARCHAR(5) DEFAULT '08:00',
                timezone VARCHAR(50) DEFAULT 'UTC',
                created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_user_id (user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # 8. Tabla user_analytics
        print("8. Creando tabla user_analytics...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_analytics (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL UNIQUE,
                login_frequency FLOAT DEFAULT 0,
                session_duration FLOAT DEFAULT 0,
                project_completion_rate FLOAT DEFAULT 0,
                activity_completion_rate FLOAT DEFAULT 0,
                content_consumption_rate FLOAT DEFAULT 0,
                learning_progress JSON DEFAULT NULL,
                preferred_content_types JSON DEFAULT NULL,
                project_success_rate FLOAT DEFAULT 0,
                business_model_complexity FLOAT DEFAULT 0,
                market_research_depth FLOAT DEFAULT 0,
                chatbot_usage_frequency FLOAT DEFAULT 0,
                feature_usage_patterns JSON DEFAULT NULL,
                created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_user_analytics_user_id (user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # 9. Tabla recommendation_engine
        print("9. Creando tabla recommendation_engine...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendation_engine (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                recommendation_type VARCHAR(50) NOT NULL,
                category VARCHAR(100) DEFAULT NULL,
                priority INT DEFAULT 1,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                reasoning TEXT,
                expected_impact FLOAT DEFAULT NULL,
                data_sources JSON DEFAULT NULL,
                confidence_score FLOAT DEFAULT 0,
                action_url VARCHAR(500) DEFAULT NULL,
                action_type VARCHAR(50) DEFAULT NULL,
                is_active TINYINT(1) DEFAULT 1,
                is_read TINYINT(1) DEFAULT 0,
                is_applied TINYINT(1) DEFAULT 0,
                created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NULL DEFAULT NULL,
                INDEX idx_recommendation_user_id (user_id),
                INDEX idx_recommendation_type (recommendation_type),
                INDEX idx_recommendation_active (is_active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # 10. Tabla data_sources
        print("10. Creando tabla data_sources...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_sources (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                source_type VARCHAR(50) NOT NULL,
                description TEXT,
                collection_frequency VARCHAR(50) DEFAULT 'daily',
                is_active TINYINT(1) DEFAULT 1,
                last_collection TIMESTAMP NULL DEFAULT NULL,
                data_schema JSON DEFAULT NULL,
                collection_parameters JSON DEFAULT NULL,
                created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_data_sources_type (source_type),
                INDEX idx_data_sources_active (is_active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # 11. Tabla analytics_events
        print("11. Creando tabla analytics_events...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics_events (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                event_type VARCHAR(100) NOT NULL,
                event_category VARCHAR(50) DEFAULT NULL,
                event_data JSON DEFAULT NULL,
                metadata JSON DEFAULT NULL,
                session_id VARCHAR(100) DEFAULT NULL,
                project_id INT DEFAULT NULL,
                activity_id INT DEFAULT NULL,
                created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_analytics_events_user_id (user_id),
                INDEX idx_analytics_events_type (event_type),
                INDEX idx_analytics_events_category (event_category),
                INDEX idx_analytics_events_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # 12. Tabla learning_paths
        print("12. Creando tabla learning_paths...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_paths (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                category VARCHAR(100) DEFAULT NULL,
                difficulty_level VARCHAR(20) DEFAULT 'beginner',
                current_step INT DEFAULT 0,
                total_steps INT DEFAULT 0,
                completion_percentage FLOAT DEFAULT 0,
                content_items JSON DEFAULT NULL,
                prerequisites JSON DEFAULT NULL,
                is_active TINYINT(1) DEFAULT 1,
                is_completed TINYINT(1) DEFAULT 0,
                created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                completed_at TIMESTAMP NULL DEFAULT NULL,
                INDEX idx_learning_paths_user_id (user_id),
                INDEX idx_learning_paths_category (category),
                INDEX idx_learning_paths_active (is_active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # 13. Tabla conversation_states
        print("13. Creando tabla conversation_states...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_states (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(100) NOT NULL,
                user_id INT NOT NULL,
                current_state VARCHAR(100) NOT NULL,
                state_type ENUM('active', 'paused', 'completed', 'abandoned', 'transitioning') DEFAULT 'active',
                state_data JSON DEFAULT NULL,
                primary_context VARCHAR(100) DEFAULT NULL,
                secondary_contexts JSON DEFAULT NULL,
                context_stack JSON DEFAULT NULL,
                current_intent VARCHAR(100) DEFAULT NULL,
                intent_type ENUM('primary', 'secondary', 'contextual', 'fallback') DEFAULT 'primary',
                intent_confidence FLOAT DEFAULT 0,
                intent_history JSON DEFAULT NULL,
                flow_id VARCHAR(100) DEFAULT NULL,
                flow_step INT DEFAULT 0,
                flow_data JSON DEFAULT NULL,
                flow_history JSON DEFAULT NULL,
                short_term_memory JSON DEFAULT NULL,
                long_term_memory JSON DEFAULT NULL,
                memory_priority JSON DEFAULT NULL,
                active_threads JSON DEFAULT NULL,
                thread_priorities JSON DEFAULT NULL,
                thread_contexts JSON DEFAULT NULL,
                previous_state VARCHAR(100) DEFAULT NULL,
                transition_reason VARCHAR(200) DEFAULT NULL,
                transition_data JSON DEFAULT NULL,
                created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                last_activity TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_conversation_states_session_id (session_id),
                INDEX idx_conversation_states_user_id (user_id),
                INDEX idx_conversation_states_current_state (current_state),
                INDEX idx_conversation_states_state_type (state_type)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # 14. Tabla conversation_flows
        print("14. Creando tabla conversation_flows...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_flows (
                id INT AUTO_INCREMENT PRIMARY KEY,
                flow_id VARCHAR(100) NOT NULL UNIQUE,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                flow_type VARCHAR(50) DEFAULT 'linear',
                flow_steps JSON DEFAULT NULL,
                flow_rules JSON DEFAULT NULL,
                flow_conditions JSON DEFAULT NULL,
                is_active TINYINT(1) DEFAULT 1,
                version VARCHAR(20) DEFAULT '1.0',
                priority INT DEFAULT 1,
                created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_conversation_flows_flow_id (flow_id),
                INDEX idx_conversation_flows_active (is_active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # 15. Tabla state_transitions
        print("15. Creando tabla state_transitions...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS state_transitions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(100) NOT NULL,
                from_state VARCHAR(100) NOT NULL,
                to_state VARCHAR(100) NOT NULL,
                transition_type VARCHAR(50) DEFAULT 'automatic',
                transition_reason VARCHAR(200) DEFAULT NULL,
                context_data JSON DEFAULT NULL,
                intent_data JSON DEFAULT NULL,
                flow_data JSON DEFAULT NULL,
                created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_state_transitions_session_id (session_id),
                INDEX idx_state_transitions_from_state (from_state),
                INDEX idx_state_transitions_to_state (to_state),
                INDEX idx_state_transitions_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # 16. Tabla conversation_threads
        print("16. Creando tabla conversation_threads...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_threads (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(100) NOT NULL,
                thread_id VARCHAR(100) NOT NULL,
                thread_type VARCHAR(50) DEFAULT 'main',
                thread_context VARCHAR(100) DEFAULT NULL,
                thread_data JSON DEFAULT NULL,
                is_active TINYINT(1) DEFAULT 1,
                priority INT DEFAULT 1,
                last_activity TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                parent_thread_id VARCHAR(100) DEFAULT NULL,
                related_threads JSON DEFAULT NULL,
                created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_conversation_threads_session_id (session_id),
                INDEX idx_conversation_threads_thread_id (thread_id),
                INDEX idx_conversation_threads_active (is_active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Insertar datos por defecto
        print("\n📝 Insertando datos por defecto...")
        
        # Insertar reglas de sugerencias por defecto
        default_rules = [
            {
                'rule_name': 'new_user_welcome',
                'rule_type': 'welcome',
                'conditions': {'user_type': 'new', 'login_count': {'$lt': 3}},
                'suggestion_template': {
                    'title': '¡Bienvenido a InnovAI!',
                    'description': 'Comienza explorando las funcionalidades básicas',
                    'action_text': 'Explorar',
                    'action_url': '/dashboard'
                }
            },
            {
                'rule_name': 'incomplete_bmc',
                'rule_type': 'completion',
                'conditions': {'has_bmc': True, 'bmc_completion': {'$lt': 0.8}},
                'suggestion_template': {
                    'title': 'Completa tu Business Model Canvas',
                    'description': 'Tienes secciones pendientes en tu BMC',
                    'action_text': 'Completar BMC',
                    'action_url': '/bmc'
                }
            },
            {
                'rule_name': 'learning_recommendation',
                'rule_type': 'learning',
                'conditions': {'last_learning_activity': {'$lt': '7d'}},
                'suggestion_template': {
                    'title': 'Contenido educativo recomendado',
                    'description': 'Descubre nuevos recursos para mejorar tus habilidades',
                    'action_text': 'Explorar contenido',
                    'action_url': '/learn'
                }
            }
        ]
        
        for rule in default_rules:
            cursor.execute("""
                INSERT IGNORE INTO suggestion_rules 
                (rule_name, rule_type, conditions, suggestion_template)
                VALUES (%s, %s, %s, %s)
            """, (
                rule['rule_name'],
                rule['rule_type'],
                json.dumps(rule['conditions']),
                json.dumps(rule['suggestion_template'])
            ))
        
        # Insertar flujos de conversación por defecto
        default_flows = [
            {
                'flow_id': 'bmc_generation',
                'name': 'Generación de Business Model Canvas',
                'description': 'Flujo para generar un BMC completo mediante conversación guiada',
                'flow_type': 'linear',
                'flow_steps': [
                    {'step': 1, 'action': 'gather_business_info', 'description': 'Recopilar información básica del negocio'},
                    {'step': 2, 'action': 'define_value_proposition', 'description': 'Definir la propuesta de valor'},
                    {'step': 3, 'action': 'identify_customers', 'description': 'Identificar segmentos de clientes'},
                    {'step': 4, 'action': 'define_channels', 'description': 'Definir canales de distribución'},
                    {'step': 5, 'action': 'identify_resources', 'description': 'Identificar recursos clave'},
                    {'step': 6, 'action': 'define_activities', 'description': 'Definir actividades clave'},
                    {'step': 7, 'action': 'identify_partners', 'description': 'Identificar socios clave'},
                    {'step': 8, 'action': 'define_revenue', 'description': 'Definir fuentes de ingresos'},
                    {'step': 9, 'action': 'define_costs', 'description': 'Definir estructura de costos'}
                ],
                'flow_rules': {'allow_backtrack': True, 'max_steps': 9},
                'flow_conditions': {'requires_completion': True}
            },
            {
                'flow_id': 'business_plan_creation',
                'name': 'Creación de Plan de Negocio',
                'description': 'Flujo para crear un plan de negocio completo',
                'flow_type': 'branching',
                'flow_steps': [
                    {'step': 1, 'action': 'executive_summary', 'description': 'Resumen ejecutivo'},
                    {'step': 2, 'action': 'market_analysis', 'description': 'Análisis de mercado'},
                    {'step': 3, 'action': 'business_strategy', 'description': 'Estrategia de negocio'},
                    {'step': 4, 'action': 'financial_planning', 'description': 'Planificación financiera'},
                    {'step': 5, 'action': 'implementation_plan', 'description': 'Plan de implementación'}
                ],
                'flow_rules': {'allow_branching': True, 'max_steps': 5},
                'flow_conditions': {'requires_validation': True}
            },
            {
                'flow_id': 'learning_assessment',
                'name': 'Evaluación de Aprendizaje',
                'description': 'Flujo para evaluar el progreso de aprendizaje del usuario',
                'flow_type': 'adaptive',
                'flow_steps': [
                    {'step': 1, 'action': 'assess_current_knowledge', 'description': 'Evaluar conocimiento actual'},
                    {'step': 2, 'action': 'identify_gaps', 'description': 'Identificar brechas de conocimiento'},
                    {'step': 3, 'action': 'recommend_content', 'description': 'Recomendar contenido educativo'},
                    {'step': 4, 'action': 'track_progress', 'description': 'Seguir progreso'},
                    {'step': 5, 'action': 'adjust_recommendations', 'description': 'Ajustar recomendaciones'}
                ],
                'flow_rules': {'adaptive': True, 'personalized': True},
                'flow_conditions': {'continuous_learning': True}
            }
        ]
        
        for flow in default_flows:
            cursor.execute("""
                INSERT IGNORE INTO conversation_flows 
                (flow_id, name, description, flow_type, flow_steps, flow_rules, flow_conditions)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                flow['flow_id'],
                flow['name'],
                flow['description'],
                flow['flow_type'],
                json.dumps(flow['flow_steps']),
                json.dumps(flow['flow_rules']),
                json.dumps(flow['flow_conditions'])
            ))
        
        # Insertar fuentes de datos por defecto
        default_data_sources = [
            {
                'name': 'User Activity',
                'source_type': 'user_behavior',
                'description': 'Datos de actividad del usuario en la plataforma',
                'collection_frequency': 'real_time',
                'data_schema': {'user_id': 'int', 'action': 'string', 'timestamp': 'datetime'}
            },
            {
                'name': 'Learning Progress',
                'source_type': 'learning_analytics',
                'description': 'Progreso en contenido educativo',
                'collection_frequency': 'daily',
                'data_schema': {'user_id': 'int', 'content_id': 'int', 'progress': 'float'}
            },
            {
                'name': 'Project Analytics',
                'source_type': 'project_metrics',
                'description': 'Métricas de proyectos y actividades',
                'collection_frequency': 'daily',
                'data_schema': {'project_id': 'int', 'completion_rate': 'float', 'status': 'string'}
            }
        ]
        
        for source in default_data_sources:
            cursor.execute("""
                INSERT IGNORE INTO data_sources 
                (name, source_type, description, collection_frequency, data_schema)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                source['name'],
                source['source_type'],
                source['description'],
                source['collection_frequency'],
                json.dumps(source['data_schema'])
            ))
        
        connection.commit()
        print("✅ Consolidación completada exitosamente!")
        print(f"✅ {len(default_rules)} reglas de sugerencias insertadas")
        print(f"✅ {len(default_flows)} flujos de conversación insertados")
        print(f"✅ {len(default_data_sources)} fuentes de datos insertadas")
        print("\n🎉 Todas las tablas del agente inteligente están ahora en la base de datos 'bmc'")
        
    except Exception as e:
        print(f"❌ Error durante la consolidación: {e}")
        if connection:
            connection.rollback()
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    consolidate_databases()
