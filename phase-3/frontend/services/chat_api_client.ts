/**
 * Chat API Client
 *
 * This module provides a client interface for interacting with the backend chat API.
 * It handles communication with the MCP server for natural language todo management.
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { getCookie } from 'cookies-next';

// Define TypeScript interfaces for API requests and responses
export interface ChatRequest {
  user_id: string;
  conversation_id?: number;
  message: string;
  metadata?: Record<string, any>;
}

export interface ChatResponse {
  conversation_id: number;
  response: string;
  task_operations: Array<{
    operation_id: number;
    type: string;
    status: string;
    result?: any;
  }>;
  next_action?: string;
}

export interface ConversationListResponse {
  conversations: Array<{
    id: number;
    title: string;
    created_at: string;
    updated_at: string;
    is_active: boolean;
    message_count: number;
  }>;
  total_count: number;
}

export interface ConversationDetailResponse {
  conversation: {
    id: number;
    title: string;
    user_id: string;
    created_at: string;
    updated_at: string;
    is_active: boolean;
  };
  messages: Array<{
    id: number;
    role: string;
    content: string;
    timestamp: string;
    sequence_number: number;
  }>;
}

/**
 * ChatAPIClient Class
 *
 * Provides methods for interacting with the chat API endpoints
 */
class ChatAPIClient {
  private axiosClient: AxiosInstance;
  private baseUrl: string;

  constructor(baseURL?: string) {
    const envUrl = process.env.NEXT_PUBLIC_API_URL;
    this.baseUrl = baseURL || envUrl || 'http://127.0.0.1:8000';

    // Initialize axios client with base configuration
    this.axiosClient = axios.create({
      baseURL: this.baseUrl,
      timeout: 30000, // 30 second timeout
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include JWT token
    this.axiosClient.interceptors.request.use(
      (config) => {
        const token = getCookie('better-auth.session_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor for error handling
    this.axiosClient.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error);
        return Promise.reject(error);
      }
    );
  }

  /**
   * Send a chat message to the backend
   *
   * @param request Chat request containing user message and context
   * @returns Promise resolving to chat response
   */
  async sendMessage(request: ChatRequest): Promise<AxiosResponse<ChatResponse>> {
    try {
      const response = await this.axiosClient.post<ChatResponse>(
        `/api/${request.user_id}/chat`,
        {
          conversation_id: request.conversation_id,
          message: request.message,
          metadata: request.metadata
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.getAuthToken()}`
          }
        }
      );

      return response;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  /**
   * Get list of user's conversations
   *
   * @param userId The user ID to retrieve conversations for
   * @param limit Number of conversations to return (default: 20)
   * @param offset Number of conversations to skip (default: 0)
   * @returns Promise resolving to conversation list response
   */
  async getConversations(
    userId: string,
    limit: number = 20,
    offset: number = 0
  ): Promise<AxiosResponse<ConversationListResponse>> {
    try {
      const response = await this.axiosClient.get<ConversationListResponse>(
        `/api/${userId}/conversations`,
        {
          params: {
            limit,
            offset
          },
          headers: {
            'Authorization': `Bearer ${this.getAuthToken()}`
          }
        }
      );

      return response;
    } catch (error) {
      console.error('Error fetching conversations:', error);
      throw error;
    }
  }

  /**
   * Get details for a specific conversation
   *
   * @param userId The user ID
   * @param conversationId The conversation ID to retrieve
   * @returns Promise resolving to conversation detail response
   */
  async getConversationDetails(
    userId: string,
    conversationId: number
  ): Promise<AxiosResponse<ConversationDetailResponse>> {
    try {
      const response = await this.axiosClient.get<ConversationDetailResponse>(
        `/api/${userId}/conversations/${conversationId}`,
        {
          headers: {
            'Authorization': `Bearer ${this.getAuthToken()}`
          }
        }
      );

      return response;
    } catch (error) {
      console.error('Error fetching conversation details:', error);
      throw error;
    }
  }

  /**
   * Create a new conversation
   *
   * @param userId The user ID
   * @param title Optional title for the conversation
   * @returns Promise resolving to the new conversation
   */
  async createConversation(
    userId: string,
    title?: string
  ): Promise<AxiosResponse<{ id: number; title: string; created_at: string }>> {
    try {
      const response = await this.axiosClient.post(
        `/api/${userId}/conversations`,
        { title },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.getAuthToken()}`
          }
        }
      );

      return response;
    } catch (error) {
      console.error('Error creating conversation:', error);
      throw error;
    }
  }

  /**
   * Delete a conversation
   *
   * @param userId The user ID
   * @param conversationId The conversation ID to delete
   * @returns Promise resolving when deletion is complete
   */
  async deleteConversation(
    userId: string,
    conversationId: number
  ): Promise<AxiosResponse<void>> {
    try {
      const response = await this.axiosClient.delete(
        `/api/${userId}/conversations/${conversationId}`,
        {
          headers: {
            'Authorization': `Bearer ${this.getAuthToken()}`
          }
        }
      );

      return response;
    } catch (error) {
      console.error('Error deleting conversation:', error);
      throw error;
    }
  }

  /**
   * Get the authentication token from cookies
   *
   * @returns The auth token string or undefined
   */
  private getAuthToken(): string | undefined {
    const token = getCookie('better-auth.session_token');

    // Validate token exists and is not empty
    if (!token) {
      console.warn('No authentication token found in cookies');
      return undefined;
    }

    const tokenStr = token.toString().trim();
    if (!tokenStr) {
      console.warn('Authentication token is empty');
      return undefined;
    }

    // Basic validation to ensure token looks like a JWT or session token
    if (tokenStr.length < 10) {
      console.warn('Authentication token appears to be invalid (too short)');
      return undefined;
    }

    return tokenStr;
  }

  /**
   * Test connectivity to the API
   *
   * @returns Promise resolving to true if API is accessible
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.axiosClient.get('/health');
      return response.status === 200;
    } catch (error) {
      console.error('API health check failed:', error);
      return false;
    }
  }
}

// Create singleton instance
const chatApiClient = new ChatAPIClient();

// Export the client instance and types
export { chatApiClient };

// Also export as default for convenience
export default chatApiClient;