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

def create_conversation_state_tables():
    """Crear tablas para gestión avanzada de estado de conversaciones"""
    connection = None
    try:
        # Primero conectamos sin especificar la base de datos
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Crear la base de datos si no existe
        cursor.execute("CREATE DATABASE IF NOT EXISTS innovai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("✅ Base de datos 'innovai' creada/verificada")
        
        # Usar la base de datos
        cursor.execute("USE innovai")
        
        print("Creando tablas de gestión avanzada de estado de conversaciones...")
        
        # Tabla conversation_states
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_states (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(100) NOT NULL,
                user_id INT NOT NULL,
                current_state VARCHAR(100) NOT NULL,
                state_type ENUM('active', 'paused', 'completed', 'abandoned', 'transitioning') DEFAULT 'active',
                state_data JSON,
                primary_context VARCHAR(100),
                secondary_contexts JSON,
                context_stack JSON,
                current_intent VARCHAR(100),
                intent_type ENUM('primary', 'secondary', 'contextual', 'fallback') DEFAULT 'primary',
                intent_confidence FLOAT DEFAULT 0.0,
                intent_history JSON,
                flow_id VARCHAR(100),
                flow_step INT DEFAULT 0,
                flow_data JSON,
                flow_history JSON,
                short_term_memory JSON,
                long_term_memory JSON,
                memory_priority JSON,
                active_threads JSON,
                thread_priorities JSON,
                thread_contexts JSON,
                previous_state VARCHAR(100),
                transition_reason VARCHAR(200),
                transition_data JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_conversation_states_session_id (session_id),
                INDEX idx_conversation_states_user_id (user_id),
                INDEX idx_conversation_states_current_state (current_state),
                INDEX idx_conversation_states_state_type (state_type)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Tabla conversation_flows
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_flows (
                id INT AUTO_INCREMENT PRIMARY KEY,
                flow_id VARCHAR(100) UNIQUE NOT NULL,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                flow_type VARCHAR(50) DEFAULT 'linear',
                flow_steps JSON,
                flow_rules JSON,
                flow_conditions JSON,
                is_active BOOLEAN DEFAULT TRUE,
                version VARCHAR(20) DEFAULT '1.0',
                priority INT DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_conversation_flows_flow_id (flow_id),
                INDEX idx_conversation_flows_active (is_active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Tabla state_transitions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS state_transitions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(100) NOT NULL,
                from_state VARCHAR(100) NOT NULL,
                to_state VARCHAR(100) NOT NULL,
                transition_type VARCHAR(50) DEFAULT 'automatic',
                transition_reason VARCHAR(200),
                context_data JSON,
                intent_data JSON,
                flow_data JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_state_transitions_session_id (session_id),
                INDEX idx_state_transitions_from_state (from_state),
                INDEX idx_state_transitions_to_state (to_state),
                INDEX idx_state_transitions_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Tabla conversation_threads
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_threads (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(100) NOT NULL,
                thread_id VARCHAR(100) NOT NULL,
                thread_type VARCHAR(50) DEFAULT 'main',
                thread_context VARCHAR(100),
                thread_data JSON,
                is_active BOOLEAN DEFAULT TRUE,
                priority INT DEFAULT 1,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                parent_thread_id VARCHAR(100),
                related_threads JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_conversation_threads_session_id (session_id),
                INDEX idx_conversation_threads_thread_id (thread_id),
                INDEX idx_conversation_threads_active (is_active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Insertar flujos de conversación por defecto
        print("Insertando flujos de conversación por defecto...")
        
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
        
        connection.commit()
        print("✅ Tablas de gestión avanzada de estado de conversaciones creadas exitosamente")
        print(f"✅ {len(default_flows)} flujos de conversación por defecto insertados")
        
    except Exception as e:
        print(f"❌ Error creando tablas de gestión avanzada de estado de conversaciones: {e}")
        if connection:
            connection.rollback()
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    create_conversation_state_tables()


