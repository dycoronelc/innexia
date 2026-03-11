// Exportar todos los servicios
export { AuthService } from './authService';
export { ChatbotService } from './chatbotService';
export { DataAnalysisService } from './dataAnalysisService';
export { ContentService } from './contentService';
export { UserService } from './userService';
export { ProjectService } from './projectService';
export { DocumentService } from './documentService';
export { NotificationService } from './notificationService';

// Exportar tipos comunes
export type { ApiResponse } from './api';

// Exportar tipos de autenticación
export type {
  LoginRequest,
  RegisterRequest,
  User,
  AuthResponse,
  PasswordResetRequest,
  PasswordResetConfirm
} from './authService';

// Exportar tipos del chatbot
export type {
  ChatMessage,
  ChatSession,
  ChatResponse,
  ChatContext,
  ChatHistory,
  ChatAnalytics,
  ChatFeedback,
  ChatIntent,
  ChatEntity,
  ChatAction
} from './chatbotService';

// Exportar tipos de análisis de datos
export type {
  UserAnalytics,
  RecommendationEngine,
  AnalyticsEvent,
  LearningPath,
  UserInsights,
  LearningProgress
} from './dataAnalysisService';

// Exportar tipos de contenido
export type {
  ContentItem,
  ContentCategory,
  LearningModule,
  UserContentProgress,
  ContentRecommendation,
  ContentSearchFilters
} from './contentService';

// Exportar tipos de usuario
export type {
  UserProfile,
  UserSettings,
  UserActivity,
  UserSession,
  UserSubscription,
  UserNotification
} from './userService';

// Exportar tipos de proyecto
export type {
  Project,
  ProjectActivity,
  ProjectDocument,
  ProjectTemplate,
  ProjectCollaborator,
  ProjectComment,
  ProjectMilestone
} from './projectService';

// Exportar tipos de documento
export type {
  Document,
  DocumentTemplate,
  DocumentVersion,
  DocumentComment,
  DocumentCollaborator,
  DocumentAnalytics,
  DocumentExport
} from './documentService';

// Exportar tipos de notificación
export type {
  Notification,
  NotificationTemplate,
  NotificationPreference,
  NotificationSchedule,
  NotificationChannel
} from './notificationService';

// Clase principal para gestionar todos los servicios
export class InnovAI {
  public auth: AuthService;
  public chatbot: ChatbotService;
  public dataAnalysis: DataAnalysisService;
  public content: ContentService;
  public user: UserService;
  public project: ProjectService;
  public document: DocumentService;
  public notification: NotificationService;

  constructor(token?: string) {
    const authToken = token || this.getStoredToken();
    
    this.auth = new AuthService();
    this.chatbot = new ChatbotService(authToken);
    this.dataAnalysis = new DataAnalysisService(authToken);
    this.content = new ContentService(authToken);
    this.user = new UserService(authToken);
    this.project = new ProjectService(authToken);
    this.document = new DocumentService(authToken);
    this.notification = new NotificationService(authToken);
  }

  private getStoredToken(): string {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('innovai_token') || '';
    }
    return '';
  }

  // Método para actualizar el token en todos los servicios
  public updateToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('innovai_token', token);
    }
    
    this.chatbot = new ChatbotService(token);
    this.dataAnalysis = new DataAnalysisService(token);
    this.content = new ContentService(token);
    this.user = new UserService(token);
    this.project = new ProjectService(token);
    this.document = new DocumentService(token);
    this.notification = new NotificationService(token);
  }

  // Método para limpiar el token
  public clearToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('innovai_token');
    }
    
    this.chatbot = new ChatbotService('');
    this.dataAnalysis = new DataAnalysisService('');
    this.content = new ContentService('');
    this.user = new UserService('');
    this.project = new ProjectService('');
    this.document = new DocumentService('');
    this.notification = new NotificationService('');
  }

  // Método para verificar si el usuario está autenticado
  public isAuthenticated(): boolean {
    const token = this.getStoredToken();
    return token.length > 0;
  }

  // Método para obtener el token actual
  public getCurrentToken(): string {
    return this.getStoredToken();
  }
}

