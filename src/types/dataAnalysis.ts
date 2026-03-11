// Tipos para análisis de datos - Archivo separado para evitar problemas de exportación
export interface UserAnalytics {
  id: number;
  user_id: number;
  login_frequency: number;
  session_duration: number;
  project_completion_rate: number;
  activity_completion_rate: number;
  content_consumption_rate: number;
  learning_progress: any;
  preferred_content_types: string[];
  project_success_rate: number;
  business_model_complexity: number;
  market_research_depth: number;
  chatbot_usage_frequency: number;
  feature_usage_patterns: any;
  created_at: string;
  updated_at?: string;
}

export interface RecommendationEngine {
  id: number;
  user_id: number;
  recommendation_type: string;
  category?: string;
  priority: number;
  title: string;
  description?: string;
  reasoning?: string;
  expected_impact?: number;
  data_sources?: string[];
  confidence_score?: number;
  action_url?: string;
  action_type?: string;
  is_active: boolean;
  is_read: boolean;
  is_applied: boolean;
  created_at: string;
  expires_at?: string;
}

export interface AnalyticsEvent {
  id: number;
  user_id: number;
  event_type: string;
  event_category?: string;
  event_data?: any;
  metadata_info?: any;
  session_id?: string;
  project_id?: number;
  activity_id?: number;
  created_at: string;
}

export interface LearningPath {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  category?: string;
  difficulty_level: string;
  current_step: number;
  total_steps: number;
  completion_percentage: number;
  content_items?: any[];
  prerequisites?: string[];
  is_active: boolean;
  is_completed: boolean;
  created_at: string;
  updated_at?: string;
  completed_at?: string;
}

export interface UserInsights {
  user_id: number;
  behavior_patterns: any;
  learning_preferences: any;
  business_metrics: any;
  improvement_areas: string[];
  strengths: string[];
  generated_at: string;
}

export interface LearningProgress {
  user_id: number;
  overall_progress: number;
  category_progress: Record<string, number>;
  next_recommendations: string[];
  estimated_completion?: string;
  generated_at: string;
}

// Tipo compuesto que depende de los tipos base
export interface DashboardData {
  analytics: UserAnalytics;
  insights: UserInsights;
  learning_progress: LearningProgress;
  top_recommendations: RecommendationEngine[];
  last_updated: string;
}

