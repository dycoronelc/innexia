import { getApiBaseUrl } from './api';

export interface InterviewQuestion {
  id: string;
  question: string;
  field: string;
  type: string;
  options?: string[];
  required: boolean;
}

export interface InterviewProgress {
  current_question?: InterviewQuestion;
  progress_percentage: number;
  completed_fields: string[];
  remaining_fields: string[];
  is_complete: boolean;
}

export interface DocumentResponse {
  document_id: string;
  title: string;
  document_type: string;
  file_path?: string;
  generated_at: string;
  download_count: number;
}

class BusinessInterviewService {
  private baseUrl = `${getApiBaseUrl()}/api/business-interview`;

  private async makeRequest(endpoint: string, options: RequestInit = {}) {
    const token = localStorage.getItem('innexia_token');
    
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async startInterview(): Promise<InterviewProgress> {
    return this.makeRequest('/start', {
      method: 'POST',
    });
  }

  async answerQuestion(field: string, value: any): Promise<InterviewProgress> {
    return this.makeRequest('/answer', {
      method: 'POST',
      body: JSON.stringify({ field, value }),
    });
  }

  async completeInterview(businessData: Record<string, any>): Promise<{
    message: string;
    bmc_prompt: string;
    document_prompts: Record<string, string>;
    interview_summary: any;
    business_data: any;
  }> {
    return this.makeRequest('/complete', {
      method: 'POST',
      body: JSON.stringify({ business_data: businessData }),
    });
  }

  async generateDocuments(
    projectId: number,
    businessData: Record<string, any>,
    documentTypes?: string[]
  ): Promise<DocumentResponse[]> {
    return this.makeRequest('/generate-documents', {
      method: 'POST',
      body: JSON.stringify({
        project_id: projectId,
        business_data: businessData,
        document_types: documentTypes,
      }),
    });
  }

  async getProjectDocuments(projectId: number): Promise<DocumentResponse[]> {
    return this.makeRequest(`/documents/${projectId}`);
  }

  async downloadDocument(documentId: number): Promise<{
    title: string;
    content: string;
    document_type: string;
    generated_at: string;
  }> {
    return this.makeRequest(`/download/${documentId}`);
  }

  async getInterviewSummary(): Promise<any> {
    return this.makeRequest('/interview-summary');
  }

  // Métodos estáticos para compatibilidad
  static async startInterview(): Promise<InterviewProgress> {
    const service = new BusinessInterviewService();
    return service.startInterview();
  }

  static async answerQuestion(field: string, value: any): Promise<InterviewProgress> {
    const service = new BusinessInterviewService();
    return service.answerQuestion(field, value);
  }

  static async completeInterview(businessData: Record<string, any>) {
    const service = new BusinessInterviewService();
    return service.completeInterview(businessData);
  }

  static async generateDocuments(
    projectId: number,
    businessData: Record<string, any>,
    documentTypes?: string[]
  ): Promise<DocumentResponse[]> {
    const service = new BusinessInterviewService();
    return service.generateDocuments(projectId, businessData, documentTypes);
  }

  static async getProjectDocuments(projectId: number): Promise<DocumentResponse[]> {
    const service = new BusinessInterviewService();
    return service.getProjectDocuments(projectId);
  }

  static async downloadDocument(documentId: number) {
    const service = new BusinessInterviewService();
    return service.downloadDocument(documentId);
  }
}

export default BusinessInterviewService;

