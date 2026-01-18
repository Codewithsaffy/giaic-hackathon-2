/**
 * Conversation API Client
 *
 * This module provides a client interface for interacting with the backend conversation API.
 * It handles communication with the server for managing conversation data and history.
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { getCookie } from 'cookies-next';

// Define TypeScript interfaces for API requests and responses
export interface ConversationCreateRequest {
  user_id: string;
  title?: string;
}

export interface ConversationResponse {
  id: number;
  user_id: string;
  title?: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export interface ConversationListResponse {
  conversations: ConversationResponse[];
  total_count: number;
}

export interface MessageResponse {
  id: number;
  role: string;
  content: string;
  timestamp: string;
  sequence_number?: number;
}

export interface ConversationDetailResponse {
  conversation: ConversationResponse;
  messages: MessageResponse[];
}

export interface PaginationParams {
  limit?: number;
  offset?: number;
}

/**
 * ConversationAPIClient Class
 *
 * Provides methods for interacting with the conversation API endpoints
 */
class ConversationAPIClient {
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
   * Create a new conversation
   *
   * @param request ConversationCreateRequest containing user_id and optional title
   * @returns Promise resolving to created conversation
   */
  async createConversation(
    request: ConversationCreateRequest
  ): Promise<AxiosResponse<ConversationResponse>> {
    try {
      const response = await this.axiosClient.post<ConversationResponse>(
        `/api/conversations`,
        {
          user_id: request.user_id,
          title: request.title
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
      console.error('Error creating conversation:', error);
      throw error;
    }
  }

  /**
   * Get a specific conversation with its messages
   *
   * @param conversationId The ID of the conversation to retrieve
   * @param userId The user ID for authorization
   * @returns Promise resolving to conversation detail response
   */
  async getConversation(
    conversationId: number,
    userId: string
  ): Promise<AxiosResponse<ConversationDetailResponse>> {
    try {
      const response = await this.axiosClient.get<ConversationDetailResponse>(
        `/api/conversations/${conversationId}`,
        {
          params: {
            user_id: userId
          },
          headers: {
            'Authorization': `Bearer ${this.getAuthToken()}`
          }
        }
      );

      return response;
    } catch (error) {
      console.error('Error fetching conversation:', error);
      throw error;
    }
  }

  /**
   * List user's conversations
   *
   * @param userId The user ID to retrieve conversations for
   * @param pagination Optional pagination parameters
   * @returns Promise resolving to conversation list response
   */
  async listConversations(
    userId: string,
    pagination?: PaginationParams
  ): Promise<AxiosResponse<ConversationListResponse>> {
    try {
      const { limit = 20, offset = 0 } = pagination || {};

      const response = await this.axiosClient.get<ConversationListResponse>(
        `/api/conversations`,
        {
          params: {
            user_id: userId,
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
   * Update conversation title
   *
   * @param conversationId The ID of the conversation to update
   * @param userId The user ID for authorization
   * @param title The new title for the conversation
   * @returns Promise resolving to updated conversation
   */
  async updateConversationTitle(
    conversationId: number,
    userId: string,
    title: string
  ): Promise<AxiosResponse<ConversationResponse>> {
    try {
      const response = await this.axiosClient.put<ConversationResponse>(
        `/api/conversations/${conversationId}/title`,
        {},
        {
          params: {
            user_id: userId,
            title: title
          },
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.getAuthToken()}`
          }
        }
      );

      return response;
    } catch (error) {
      console.error('Error updating conversation title:', error);
      throw error;
    }
  }

  /**
   * Delete a conversation
   *
   * @param conversationId The ID of the conversation to delete
   * @param userId The user ID for authorization
   * @returns Promise resolving when deletion is complete
   */
  async deleteConversation(
    conversationId: number,
    userId: string
  ): Promise<AxiosResponse<void>> {
    try {
      const response = await this.axiosClient.delete(
        `/api/conversations/${conversationId}`,
        {
          params: {
            user_id: userId
          },
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
   * Get messages for a conversation
   *
   * @param conversationId The ID of the conversation
   * @param userId The user ID for authorization
   * @param pagination Optional pagination parameters
   * @returns Promise resolving to array of messages
   */
  async getConversationMessages(
    conversationId: number,
    userId: string,
    pagination?: PaginationParams
  ): Promise<AxiosResponse<MessageResponse[]>> {
    try {
      const { limit = 50, offset = 0 } = pagination || {};

      const response = await this.axiosClient.get<MessageResponse[]>(
        `/api/conversations/${conversationId}/messages`,
        {
          params: {
            user_id: userId,
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
      console.error('Error fetching conversation messages:', error);
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
   * Test connectivity to the conversation API
   *
   * @returns Promise resolving to true if API is accessible
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.axiosClient.get('/api/conversations/health');
      return response.status === 200;
    } catch (error) {
      console.error('Conversation API health check failed:', error);
      return false;
    }
  }
}

// Create singleton instance
const conversationApiClient = new ConversationAPIClient();

// Export the client instance and types
export { conversationApiClient };

// Also export as default for convenience
export default conversationApiClient;