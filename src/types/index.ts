export interface User {
  id: string;
  username: string;
  email: string;
  fullName: string;
  role: 'admin' | 'user';
  createdAt: Date;
  active: boolean;
}

export interface ProjectDocument {
  id: string;
  name: string;
  originalName: string;
  fileType: string;
  fileSize: number;
  uploadedBy: string;
  uploadedAt: Date;
  description?: string;
  projectId: number;
}

export interface Project {
  id: number;
  name: string;
  description: string;
  category: string;
  tags: string[];
  location: string;
  status: 'active' | 'inactive' | 'completed';
  createdAt: Date;
  updatedAt: Date;
  businessModelCanvas?: BusinessModelCanvas;
  documents?: ProjectDocument[];
}

export interface BusinessModelCanvas {
  id: string;
  projectId: number;
  keyPartners: string[];
  keyActivities: string[];
  keyResources: string[];
  valuePropositions: string[];
  customerRelationships: string[];
  channels: string[];
  customerSegments: string[];
  costStructure: string[];
  revenueStreams: string[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Category {
  id: string;
  name: string;
  description: string;
  color: string;
  active: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface Tag {
  id: string;
  name: string;
  description: string;
  category: string;
  color: string;
  active: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface Location {
  id: string;
  name: string;
  description: string;
  country: string;
  region: string;
  timezone: string;
  active: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface ActivityComment {
  id: string;
  content: string;
  authorId: string;
  authorName: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface ActivityChecklist {
  id: string;
  title: string;
  items: ActivityChecklistItem[];
  createdAt: Date;
  updatedAt: Date;
}

export interface ActivityChecklistItem {
  id: string;
  content: string;
  completed: boolean;
  completedAt?: Date;
  completedBy?: string;
  createdAt: Date;
}

export interface ActivityAttachment {
  id: string;
  name: string;
  originalName: string;
  fileType: string;
  fileSize: number;
  url: string;
  uploadedBy: string;
  uploadedAt: Date;
  description?: string;
}

export interface ProjectActivity {
  id: string;
  title: string;
  description: string;
  status: 'todo' | 'in-progress' | 'review' | 'completed';
  priority: 'low' | 'medium' | 'high';
  assignee: string;
  assignees: string[]; // Múltiples responsables
  startDate: Date;
  dueDate: Date;
  createdAt: Date;
  updatedAt: Date;
  projectId: number;
  
  // Nuevas funcionalidades tipo Trello
  tags: string[]; // IDs de etiquetas
  comments: ActivityComment[];
  checklists: ActivityChecklist[];
  attachments: ActivityAttachment[];
  labels: string[]; // IDs de categorías como etiquetas visuales
}

export interface AuditLog {
  id: string;
  userId: string;
  action: string;
  entityType: string;
  entityId: string;
  details: string;
  timestamp: Date;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  fullName: string;
}

export interface AuthContextType {
  user: User | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

/** Salida del agente IA (n8n) - compatible con salidaAgente.json */
export interface ProjectAgentOutput {
  id: number;
  project_id: number;
  metadata?: Record<string, unknown>;
  conversacion?: Record<string, unknown>;
  business_model_canvas?: Record<string, unknown>;
  estrategia_comercial?: Record<string, unknown>;
  roadmap_estrategico?: Record<string, unknown>;
  analisis_financiero?: Record<string, unknown>;
  analisis_riesgos?: Record<string, unknown>;
  veredicto_final?: Record<string, unknown>;
  plan_actividades?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
}

