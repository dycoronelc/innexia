import pymysql
import os
from datetime import datetime

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'innovai',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def create_data_analysis_tables():
    """Crear tablas para análisis de datos y recomendaciones personalizadas"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("Creando tablas de análisis de datos...")
        
        # Tabla user_analytics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_analytics (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                login_frequency FLOAT DEFAULT 0.0,
                session_duration FLOAT DEFAULT 0.0,
                project_completion_rate FLOAT DEFAULT 0.0,
                activity_completion_rate FLOAT DEFAULT 0.0,
                content_consumption_rate FLOAT DEFAULT 0.0,
                learning_progress JSON,
                preferred_content_types JSON,
                project_success_rate FLOAT DEFAULT 0.0,
                business_model_complexity FLOAT DEFAULT 0.0,
                market_research_depth FLOAT DEFAULT 0.0,
                chatbot_usage_frequency FLOAT DEFAULT 0.0,
                feature_usage_patterns JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_analytics_user_id (user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Tabla recommendation_engine
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendation_engine (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                recommendation_type VARCHAR(50) NOT NULL,
                category VARCHAR(100),
                priority INT DEFAULT 1,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                reasoning TEXT,
                expected_impact FLOAT,
                data_sources JSON,
                confidence_score FLOAT DEFAULT 0.0,
                action_url VARCHAR(500),
                action_type VARCHAR(50),
                is_active BOOLEAN DEFAULT TRUE,
                is_read BOOLEAN DEFAULT FALSE,
                is_applied BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_recommendation_user_id (user_id),
                INDEX idx_recommendation_type (recommendation_type),
                INDEX idx_recommendation_active (is_active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Tabla data_sources
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_sources (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                source_type VARCHAR(50) NOT NULL,
                description TEXT,
                collection_frequency VARCHAR(50) DEFAULT 'daily',
                is_active BOOLEAN DEFAULT TRUE,
                last_collection TIMESTAMP NULL,
                data_schema JSON,
                collection_parameters JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_data_sources_type (source_type),
                INDEX idx_data_sources_active (is_active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Tabla analytics_events
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics_events (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                event_type VARCHAR(100) NOT NULL,
                event_category VARCHAR(50),
                event_data JSON,
                metadata JSON,
                session_id VARCHAR(100),
                project_id INT,
                activity_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
                FOREIGN KEY (activity_id) REFERENCES project_activities(id) ON DELETE SET NULL,
                INDEX idx_analytics_events_user_id (user_id),
                INDEX idx_analytics_events_type (event_type),
                INDEX idx_analytics_events_category (event_category),
                INDEX idx_analytics_events_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Tabla learning_paths
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_paths (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                category VARCHAR(100),
                difficulty_level VARCHAR(20) DEFAULT 'beginner',
                current_step INT DEFAULT 0,
                total_steps INT DEFAULT 0,
                completion_percentage FLOAT DEFAULT 0.0,
                content_items JSON,
                prerequisites JSON,
                is_active BOOLEAN DEFAULT TRUE,
                is_completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                completed_at TIMESTAMP NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_learning_paths_user_id (user_id),
                INDEX idx_learning_paths_category (category),
                INDEX idx_learning_paths_active (is_active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Insertar fuentes de datos por defecto
        print("Insertando fuentes de datos por defecto...")
        
        default_data_sources = [
            {
                'name': 'User Login Events',
                'source_type': 'interaction',
                'description': 'Tracks user login frequency and session duration',
                'collection_frequency': 'daily',
                'data_schema': {'event_type': 'string', 'timestamp': 'datetime', 'session_id': 'string'},
                'collection_parameters': {'track_session_duration': True}
            },
            {
                'name': 'Project Completion Metrics',
                'source_type': 'project',
                'description': 'Tracks project creation, completion, and success rates',
                'collection_frequency': 'weekly',
                'data_schema': {'project_id': 'integer', 'status': 'string', 'completion_date': 'datetime'},
                'collection_parameters': {'include_activities': True}
            },
            {
                'name': 'Activity Performance',
                'source_type': 'activity',
                'description': 'Tracks activity completion rates and performance',
                'collection_frequency': 'daily',
                'data_schema': {'activity_id': 'integer', 'status': 'string', 'completion_time': 'datetime'},
                'collection_parameters': {'track_time_spent': True}
            },
            {
                'name': 'Content Consumption',
                'source_type': 'learning',
                'description': 'Tracks educational content consumption patterns',
                'collection_frequency': 'daily',
                'data_schema': {'content_id': 'integer', 'content_type': 'string', 'view_duration': 'integer'},
                'collection_parameters': {'track_completion': True}
            },
            {
                'name': 'Chatbot Interactions',
                'source_type': 'interaction',
                'description': 'Tracks chatbot usage patterns and effectiveness',
                'collection_frequency': 'daily',
                'data_schema': {'interaction_type': 'string', 'message_count': 'integer', 'satisfaction': 'integer'},
                'collection_parameters': {'track_satisfaction': True}
            },
            {
                'name': 'Business Model Canvas Analysis',
                'source_type': 'project',
                'description': 'Analyzes BMC complexity and completeness',
                'collection_frequency': 'weekly',
                'data_schema': {'bmc_id': 'integer', 'completeness_score': 'float', 'complexity_score': 'float'},
                'collection_parameters': {'analyze_completeness': True}
            }
        ]
        
        for source in default_data_sources:
            cursor.execute("""
                INSERT IGNORE INTO data_sources 
                (name, source_type, description, collection_frequency, data_schema, collection_parameters)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                source['name'],
                source['source_type'],
                source['description'],
                source['collection_frequency'],
                str(source['data_schema']),
                str(source['collection_parameters'])
            ))
        
        connection.commit()
        print("✅ Tablas de análisis de datos creadas exitosamente")
        print(f"✅ {len(default_data_sources)} fuentes de datos por defecto insertadas")
        
    except Exception as e:
        print(f"❌ Error creando tablas de análisis de datos: {e}")
        if connection:
            connection.rollback()
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    create_data_analysis_tables()

