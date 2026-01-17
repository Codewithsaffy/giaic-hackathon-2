/**
 * Conversation State Management
 *
 * This module provides React context and hooks for managing conversation state
 * across the application.
 */

import { createContext, useContext, useReducer, ReactNode } from 'react';

// Define types
export interface Message {
  id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  sequence_number?: number;
}

export interface Conversation {
  id: number;
  user_id: string;
  title?: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export interface ConversationState {
  currentConversation: Conversation | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  availableConversations: Conversation[];
}

// Define actions
type Action =
  | { type: 'SET_CURRENT_CONVERSATION'; payload: Conversation }
  | { type: 'ADD_MESSAGE'; payload: Message }
  | { type: 'UPDATE_MESSAGE'; payload: Message }
  | { type: 'CLEAR_MESSAGES' }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_AVAILABLE_CONVERSATIONS'; payload: Conversation[] }
  | { type: 'ADD_CONVERSATION'; payload: Conversation }
  | { type: 'REMOVE_CONVERSATION'; payload: number }; // conversation id

// Initial state
const initialState: ConversationState = {
  currentConversation: null,
  messages: [],
  isLoading: false,
  error: null,
  availableConversations: [],
};

// Reducer function
const conversationReducer = (state: ConversationState, action: Action): ConversationState => {
  switch (action.type) {
    case 'SET_CURRENT_CONVERSATION':
      return {
        ...state,
        currentConversation: action.payload,
        messages: [], // Clear previous messages when switching conversations
      };

    case 'ADD_MESSAGE':
      return {
        ...state,
        messages: [...state.messages, action.payload],
      };

    case 'UPDATE_MESSAGE':
      return {
        ...state,
        messages: state.messages.map(msg =>
          msg.id === action.payload.id ? action.payload : msg
        ),
      };

    case 'CLEAR_MESSAGES':
      return {
        ...state,
        messages: [],
      };

    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };

    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
      };

    case 'SET_AVAILABLE_CONVERSATIONS':
      return {
        ...state,
        availableConversations: action.payload,
      };

    case 'ADD_CONVERSATION':
      return {
        ...state,
        availableConversations: [...state.availableConversations, action.payload],
      };

    case 'REMOVE_CONVERSATION':
      return {
        ...state,
        availableConversations: state.availableConversations.filter(
          conv => conv.id !== action.payload
        ),
        // If we're removing the current conversation, clear it
        currentConversation:
          state.currentConversation?.id === action.payload
            ? null
            : state.currentConversation,
      };

    default:
      return state;
  }
};

// Create context
const ConversationContext = createContext<{
  state: ConversationState;
  dispatch: React.Dispatch<Action>;
}>({
  state: initialState,
  dispatch: () => {},
});

// Provider component
export function ConversationProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(conversationReducer, initialState);

  return (
    <ConversationContext.Provider value={{ state, dispatch }}>
      {children}
    </ConversationContext.Provider>
  );
}

// Custom hook to use the conversation context
export function useConversation() {
  const context = useContext(ConversationContext);
  if (!context) {
    throw new Error('useConversation must be used within a ConversationProvider');
  }
  return context;
}

// Helper functions to dispatch actions
export function useConversationActions() {
  const { dispatch } = useConversation();

  return {
    setCurrentConversation: (conversation: Conversation) =>
      dispatch({ type: 'SET_CURRENT_CONVERSATION', payload: conversation }),

    addMessage: (message: Message) =>
      dispatch({ type: 'ADD_MESSAGE', payload: message }),

    updateMessage: (message: Message) =>
      dispatch({ type: 'UPDATE_MESSAGE', payload: message }),

    clearMessages: () =>
      dispatch({ type: 'CLEAR_MESSAGES' }),

    setLoading: (loading: boolean) =>
      dispatch({ type: 'SET_LOADING', payload: loading }),

    setError: (error: string | null) =>
      dispatch({ type: 'SET_ERROR', payload: error }),

    setAvailableConversations: (conversations: Conversation[]) =>
      dispatch({ type: 'SET_AVAILABLE_CONVERSATIONS', payload: conversations }),

    addConversation: (conversation: Conversation) =>
      dispatch({ type: 'ADD_CONVERSATION', payload: conversation }),

    removeConversation: (conversationId: number) =>
      dispatch({ type: 'REMOVE_CONVERSATION', payload: conversationId }),
  };
}