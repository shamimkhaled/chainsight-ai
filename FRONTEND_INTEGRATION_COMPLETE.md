# ChainSight AI - Frontend Integration Guide

**Version**: 1.0  
**Last Updated**: January 2024  
**Stack**: React/TypeScript/Next.js

---

## 📑 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [API Service Layer](#api-service-layer)
3. [Authentication & Authorization](#authentication--authorization)
4. [Document Upload & Management](#document-upload--management)
5. [RAG Chat Interface](#rag-chat-interface)
6. [Real-Time Features](#real-time-features)
7. [Tenant-Based Routing](#tenant-based-routing)
8. [State Management](#state-management)
9. [Complete Component Examples](#complete-component-examples)

---

## 🏗️ Architecture Overview

### Technology Stack

```
Frontend Stack:
├── React 18+ (UI library)
├── TypeScript (Type safety)
├── Next.js 14+ (Framework with App Router)
├── TailwindCSS (Styling)
├── shadcn/ui (Component library)
├── Tanstack Query (Data fetching & caching)
├── Zustand (State management)
├── Axios (HTTP client)
└── Socket.IO (Real-time)
```

### Project Structure

```
frontend/
├── app/                          # Next.js App Router
│   ├── (auth)/                  # Auth pages group
│   │   ├── login/
│   │   └── register/
│   ├── (dashboard)/             # Protected pages group
│   │   ├── contracts/
│   │   ├── chat/
│   │   ├── alerts/
│   │   └── integrations/
│   └── layout.tsx
├── components/
│   ├── ui/                      # shadcn/ui components
│   ├── contracts/
│   ├── chat/
│   └── shared/
├── lib/
│   ├── api/                     # API service layer
│   │   ├── client.ts
│   │   ├── auth.ts
│   │   ├── contracts.ts
│   │   ├── chat.ts
│   │   └── alerts.ts
│   ├── hooks/                   # Custom React hooks
│   ├── utils/
│   └── types/                   # TypeScript types
├── stores/                      # Zustand stores
│   ├── authStore.ts
│   ├── tenantStore.ts
│   └── contractStore.ts
└── public/
```

---

## 🔌 API Service Layer

### Base API Client

```typescript
// lib/api/client.ts
import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';
import { getAuthToken, getTenantId, refreshAuthToken } from './auth';

class APIClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
    
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor - Add auth & tenant headers
    this.client.interceptors.request.use(
      (config) => {
        const token = getAuthToken();
        const tenantId = getTenantId();

        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        if (tenantId) {
          config.headers['X-Tenant-ID'] = tenantId;
        }

        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor - Handle errors & token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

        // Handle 401 - Token expired
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const newToken = await refreshAuthToken();
            
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
            }

            return this.client(originalRequest);
          } catch (refreshError) {
            // Refresh failed - redirect to login
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        // Handle other errors
        return Promise.reject(error);
      }
    );
  }

  // Generic request methods
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.patch<T>(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config);
    return response.data;
  }

  // File upload with progress
  async uploadFile<T>(
    url: string,
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);

    const config: AxiosRequestConfig = {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    };

    const response = await this.client.post<T>(url, formData, config);
    return response.data;
  }
}

export const apiClient = new APIClient();
```

---

### TypeScript Type Definitions

```typescript
// lib/types/index.ts

// Auth types
export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'admin' | 'manager' | 'user' | 'viewer';
  is_active: boolean;
  tenant: Tenant;
  created_at: string;
}

export interface Tenant {
  id: string;
  name: string;
  subdomain: string;
  plan_type: 'free' | 'starter' | 'professional' | 'enterprise';
  settings: TenantSettings;
}

export interface TenantSettings {
  features?: {
    rag_chat?: boolean;
    ai_agents?: boolean;
    integrations?: boolean;
  };
  branding?: {
    logo_url?: string;
    primary_color?: string;
    secondary_color?: string;
  };
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
}

// Contract types
export interface Contract {
  id: string;
  original_filename: string;
  file_type: string;
  file_size: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  processing_stage: string;
  progress_percentage: number;
  contract_type: string;
  industry: string;
  language: string;
  contract_date: string | null;
  effective_date: string | null;
  expiry_date: string | null;
  contract_value: string | null;
  currency: string;
  risk_score: number | null;
  compliance_score: number | null;
  sentiment_score: number | null;
  counterparties: Counterparty[];
  is_archived: boolean;
  uploaded_by: {
    id: string;
    email: string;
    full_name: string;
  };
  analyzed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ContractDetail extends Contract {
  analysis?: ContractAnalysis;
  clauses?: Clause[];
}

export interface ContractAnalysis {
  overall_risk_score: number;
  critical_issues_count: number;
  missing_clauses_count: number;
  priority_level: 'low' | 'medium' | 'high' | 'critical';
  issues: Issue[];
}

export interface Clause {
  id: string;
  clause_number: string;
  clause_type: string;
  title: string;
  content: string;
  page_number: number | null;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  has_issues: boolean;
}

// Chat types
export interface ChatSession {
  id: string;
  title: string;
  is_active: boolean;
  last_message_at: string;
  message_count: number;
  contracts: Contract[];
  created_at: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  sources?: ChatSource[];
  tokens_used?: number;
  processing_time?: number;
  created_at: string;
}

export interface ChatSource {
  contract_id: string;
  contract_filename: string;
  clause_id?: string;
  clause_number?: string;
  page_number?: number;
  relevance_score: number;
}

// Pagination
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
```

---

### API Service Functions

```typescript
// lib/api/auth.ts
import { apiClient } from './client';
import { AuthResponse, User } from '../types';

const TOKEN_KEY = 'chainsight_access_token';
const REFRESH_TOKEN_KEY = 'chainsight_refresh_token';
const TENANT_KEY = 'chainsight_tenant_id';

export const authAPI = {
  // Login
  login: async (email: string, password: string): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/token/', {
      email,
      password,
    });
    
    // Store tokens
    localStorage.setItem(TOKEN_KEY, response.access);
    localStorage.setItem(REFRESH_TOKEN_KEY, response.refresh);
    localStorage.setItem(TENANT_KEY, response.user.tenant.id);
    
    return response;
  },

  // Logout
  logout: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(TENANT_KEY);
  },

  // Refresh token
  refreshToken: async (): Promise<string> => {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await apiClient.post<{ access: string; refresh: string }>(
      '/auth/token/refresh/',
      { refresh: refreshToken }
    );

    localStorage.setItem(TOKEN_KEY, response.access);
    localStorage.setItem(REFRESH_TOKEN_KEY, response.refresh);

    return response.access;
  },

  // Get current user
  getCurrentUser: async (): Promise<User> => {
    return apiClient.get<User>('/users/me/');
  },
};

// Helper functions
export const getAuthToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY);
};

export const getTenantId = (): string | null => {
  return localStorage.getItem(TENANT_KEY);
};

export const refreshAuthToken = (): Promise<string> => {
  return authAPI.refreshToken();
};

export const isAuthenticated = (): boolean => {
  return !!getAuthToken();
};
```

```typescript
// lib/api/contracts.ts
import { apiClient } from './client';
import { Contract, ContractDetail, PaginatedResponse } from '../types';

export const contractsAPI = {
  // List contracts
  list: async (params?: {
    page?: number;
    page_size?: number;
    search?: string;
    status?: string;
    ordering?: string;
  }): Promise<PaginatedResponse<Contract>> => {
    return apiClient.get<PaginatedResponse<Contract>>('/contracts/', {
      params,
    });
  },

  // Get contract details
  get: async (id: string): Promise<ContractDetail> => {
    return apiClient.get<ContractDetail>(`/contracts/${id}/`);
  },

  // Upload contract
  upload: async (
    file: File,
    metadata?: {
      contract_type?: string;
      industry?: string;
    },
    onProgress?: (progress: number) => void
  ): Promise<Contract> => {
    const formData = new FormData();
    formData.append('file', file);
    
    if (metadata?.contract_type) {
      formData.append('contract_type', metadata.contract_type);
    }
    if (metadata?.industry) {
      formData.append('industry', metadata.industry);
    }

    return apiClient.uploadFile<Contract>('/contracts/', file, onProgress);
  },

  // Analyze contract
  analyze: async (id: string): Promise<{ message: string; task_id: string }> => {
    return apiClient.post(`/contracts/${id}/analyze/`);
  },

  // Export contract
  export: async (
    id: string,
    format: 'pdf' | 'docx',
    includeAnalysis: boolean = true
  ): Promise<{ download_url: string; expires_at: string }> => {
    return apiClient.get(`/contracts/${id}/export/`, {
      params: {
        format,
        include_analysis: includeAnalysis,
      },
    });
  },

  // Archive contract
  archive: async (id: string): Promise<Contract> => {
    return apiClient.post(`/contracts/${id}/archive/`);
  },

  // Delete contract
  delete: async (id: string): Promise<void> => {
    return apiClient.delete(`/contracts/${id}/`);
  },
};
```

```typescript
// lib/api/chat.ts
import { apiClient } from './client';
import { ChatSession, ChatMessage, PaginatedResponse } from '../types';

export const chatAPI = {
  // List chat sessions
  listSessions: async (): Promise<PaginatedResponse<ChatSession>> => {
    return apiClient.get<PaginatedResponse<ChatSession>>('/chat/sessions/');
  },

  // Create chat session
  createSession: async (data: {
    title: string;
    contracts?: string[];
  }): Promise<ChatSession> => {
    return apiClient.post<ChatSession>('/chat/sessions/', data);
  },

  // Get session details
  getSession: async (id: string): Promise<ChatSession> => {
    return apiClient.get<ChatSession>(`/chat/sessions/${id}/`);
  },

  // Send message
  sendMessage: async (
    sessionId: string,
    content: string
  ): Promise<{
    user_message: ChatMessage;
    assistant_message: ChatMessage;
  }> => {
    return apiClient.post(`/chat/sessions/${sessionId}/message/`, {
      content,
    });
  },

  // Delete session
  deleteSession: async (id: string): Promise<void> => {
    return apiClient.delete(`/chat/sessions/${id}/`);
  },
};
```

---

## 🔐 Authentication & Authorization

### Auth Hook

```typescript
// lib/hooks/useAuth.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authAPI } from '../api/auth';
import { User } from '../types';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  fetchUser: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authAPI.login(email, password);
          set({
            user: response.user,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error: any) {
          set({
            error: error.response?.data?.message || 'Login failed',
            isLoading: false,
          });
          throw error;
        }
      },

      logout: () => {
        authAPI.logout();
        set({
          user: null,
          isAuthenticated: false,
          error: null,
        });
      },

      fetchUser: async () => {
        set({ isLoading: true });
        try {
          const user = await authAPI.getCurrentUser();
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'chainsight-auth',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
```

### Login Component

```typescript
// app/(auth)/login/page.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading, error, clearError } = useAuthStore();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();

    try {
      await login(email, password);
      router.push('/dashboard');
    } catch (error) {
      // Error is handled in store
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="w-full max-w-md space-y-8 rounded-lg bg-white p-8 shadow-lg">
        <div>
          <h2 className="text-center text-3xl font-bold">
            Sign in to ChainSight AI
          </h2>
        </div>

        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <Label htmlFor="email">Email address</Label>
              <Input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1"
              />
            </div>

            <div>
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1"
              />
            </div>
          </div>

          <Button
            type="submit"
            className="w-full"
            disabled={isLoading}
          >
            {isLoading ? 'Signing in...' : 'Sign in'}
          </Button>
        </form>
      </div>
    </div>
  );
}
```

### Protected Route Middleware

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('chainsight_access_token')?.value;
  const { pathname } = request.nextUrl;

  // Public routes
  const publicRoutes = ['/login', '/register', '/forgot-password'];
  const isPublicRoute = publicRoutes.some((route) => pathname.startsWith(route));

  // Redirect to login if not authenticated
  if (!token && !isPublicRoute) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // Redirect to dashboard if authenticated and trying to access auth pages
  if (token && isPublicRoute) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
```

---

## 📤 Document Upload & Management

### Contract Upload Component

```typescript
// components/contracts/ContractUpload.tsx
'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { contractsAPI } from '@/lib/api/contracts';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Upload, FileText, X } from 'lucide-react';
import { toast } from 'sonner';

export function ContractUpload() {
  const [uploadProgress, setUploadProgress] = useState(0);
  const queryClient = useQueryClient();

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      return contractsAPI.upload(
        file,
        { industry: 'manufacturing' },
        (progress) => setUploadProgress(progress)
      );
    },
    onSuccess: (data) => {
      toast.success(`Contract "${data.original_filename}" uploaded successfully`);
      queryClient.invalidateQueries({ queryKey: ['contracts'] });
      setUploadProgress(0);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Upload failed');
      setUploadProgress(0);
    },
  });

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      uploadMutation.mutate(acceptedFiles[0]);
    }
  }, [uploadMutation]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'image/*': ['.jpg', '.jpeg', '.png'],
    },
    maxSize: 50 * 1024 * 1024, // 50MB
    multiple: false,
  });

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
          transition-colors
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          ${uploadMutation.isPending ? 'pointer-events-none opacity-50' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <Upload className="mx-auto h-12 w-12 text-gray-400" />
        
        <div className="mt-4">
          <p className="text-lg font-medium">
            {isDragActive
              ? 'Drop the file here'
              : 'Drag & drop a contract here, or click to select'}
          </p>
          <p className="mt-2 text-sm text-gray-500">
            Supports PDF, DOCX, JPG, PNG (max 50MB)
          </p>
        </div>
      </div>

      {uploadMutation.isPending && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Uploading...</span>
            <span className="text-sm text-gray-500">{uploadProgress}%</span>
          </div>
          <Progress value={uploadProgress} />
        </div>
      )}
    </div>
  );
}
```

### Contract List Component

```typescript
// components/contracts/ContractList.tsx
'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { contractsAPI } from '@/lib/api/contracts';
import { Contract } from '@/lib/types';
import { ContractCard } from './ContractCard';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Search, Filter } from 'lucide-react';

export function ContractList() {
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState<string>('');
  const [page, setPage] = useState(1);

  const { data, isLoading, error } = useQuery({
    queryKey: ['contracts', { search, status, page }],
    queryFn: () => contractsAPI.list({ search, status, page, page_size: 20 }),
  });

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex gap-4">
        <div className="flex-1">
          <Input
            placeholder="Search contracts..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            icon={<Search className="h-4 w-4" />}
          />
        </div>
        
        <Select
          value={status}
          onValueChange={setStatus}
          placeholder="All statuses"
        >
          <option value="">All statuses</option>
          <option value="pending">Pending</option>
          <option value="processing">Processing</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
        </Select>
      </div>

      {/* Contract Grid */}
      {isLoading ? (
        <div>Loading...</div>
      ) : error ? (
        <div>Error loading contracts</div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data?.results.map((contract) => (
              <ContractCard key={contract.id} contract={contract} />
            ))}
          </div>

          {/* Pagination */}
          <div className="flex justify-between items-center">
            <p className="text-sm text-gray-500">
              Showing {data?.results.length} of {data?.count} contracts
            </p>
            
            <div className="flex gap-2">
              <Button
                variant="outline"
                disabled={!data?.previous}
                onClick={() => setPage(page - 1)}
              >
                Previous
              </Button>
              <Button
                variant="outline"
                disabled={!data?.next}
                onClick={() => setPage(page + 1)}
              >
                Next
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
```

---

## 💬 RAG Chat Interface

### Chat Component with Streaming

```typescript
// components/chat/ChatInterface.tsx
'use client';

import { useState, useRef, useEffect } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { chatAPI } from '@/lib/api/chat';
import { ChatMessage as ChatMessageType } from '@/lib/types';
import { ChatMessage } from './ChatMessage';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Send } from 'lucide-react';

interface ChatInterfaceProps {
  sessionId: string;
}

export function ChatInterface({ sessionId }: ChatInterfaceProps) {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Fetch session messages
  const { data: session } = useQuery({
    queryKey: ['chat-session', sessionId],
    queryFn: () => chatAPI.getSession(sessionId),
  });

  useEffect(() => {
    if (session) {
      setMessages(session.messages || []);
    }
  }, [session]);

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: async (content: string) => {
      // Add user message immediately (optimistic update)
      const userMessage: ChatMessageType = {
        id: `temp-${Date.now()}`,
        role: 'user',
        content,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);

      // Send to API
      return chatAPI.sendMessage(sessionId, content);
    },
    onSuccess: (data) => {
      // Replace temp message with real one and add assistant response
      setMessages((prev) => {
        const withoutTemp = prev.filter((m) => !m.id.startsWith('temp-'));
        return [...withoutTemp, data.user_message, data.assistant_message];
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      sendMessageMutation.mutate(message);
      setMessage('');
    }
  };

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t p-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask a question about your contracts..."
            className="flex-1"
            rows={2}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
          />
          <Button
            type="submit"
            disabled={!message.trim() || sendMessageMutation.isPending}
          >
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </div>
  );
}
```

### Chat Message Component

```typescript
// components/chat/ChatMessage.tsx
import { ChatMessage as ChatMessageType } from '@/lib/types';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { FileText, User } from 'lucide-react';

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar */}
      <Avatar>
        <AvatarFallback>
          {isUser ? <User className="h-4 w-4" /> : <span>AI</span>}
        </AvatarFallback>
      </Avatar>

      {/* Message Content */}
      <div className={`flex-1 ${isUser ? 'text-right' : 'text-left'}`}>
        <div
          className={`
            inline-block rounded-lg px-4 py-2 max-w-[80%]
            ${isUser 
              ? 'bg-blue-500 text-white' 
              : 'bg-gray-100 text-gray-900'
            }
          `}
        >
          <p className="whitespace-pre-wrap">{message.content}</p>
        </div>

        {/* Sources (for assistant messages) */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-2 space-y-1">
            <p className="text-xs text-gray-500 font-medium">Sources:</p>
            {message.sources.map((source, idx) => (
              <div
                key={idx}
                className="inline-flex items-center gap-1 bg-gray-100 rounded px-2 py-1 mr-2"
              >
                <FileText className="h-3 w-3" />
                <span className="text-xs">
                  {source.contract_filename} - {source.clause_number}
                </span>
                <Badge variant="secondary" className="text-xs">
                  {Math.round(source.relevance_score * 100)}%
                </Badge>
              </div>
            ))}
          </div>
        )}

        {/* Timestamp */}
        <p className="text-xs text-gray-500 mt-1">
          {new Date(message.created_at).toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}
```

---

## 🔔 Real-Time Features

### WebSocket Setup (Socket.IO)

```typescript
// lib/socket.ts
import { io, Socket } from 'socket.io-client';
import { getAuthToken, getTenantId } from './api/auth';

class SocketClient {
  private socket: Socket | null = null;

  connect() {
    if (this.socket?.connected) return this.socket;

    const token = getAuthToken();
    const tenantId = getTenantId();

    this.socket = io(process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000', {
      auth: {
        token,
      },
      query: {
        tenant_id: tenantId,
      },
    });

    this.socket.on('connect', () => {
      console.log('Socket connected');
    });

    this.socket.on('disconnect', () => {
      console.log('Socket disconnected');
    });

    return this.socket;
  }

  disconnect() {
    this.socket?.disconnect();
    this.socket = null;
  }

  on(event: string, callback: (...args: any[]) => void) {
    this.socket?.on(event, callback);
  }

  off(event: string, callback?: (...args: any[]) => void) {
    this.socket?.off(event, callback);
  }

  emit(event: string, data: any) {
    this.socket?.emit(event, data);
  }
}

export const socketClient = new SocketClient();
```

### Real-Time Notifications

```typescript
// components/notifications/NotificationListener.tsx
'use client';

import { useEffect } from 'react';
import { socketClient } from '@/lib/socket';
import { toast } from 'sonner';
import { useQueryClient } from '@tanstack/react-query';

export function NotificationListener() {
  const queryClient = useQueryClient();

  useEffect(() => {
    const socket = socketClient.connect();

    // Listen for contract processing updates
    socket.on('contract:status', (data) => {
      toast.info(`Contract "${data.filename}": ${data.status}`);
      queryClient.invalidateQueries({ queryKey: ['contracts', data.id] });
    });

    // Listen for new alerts
    socket.on('alert:new', (data) => {
      toast.error(`New Alert: ${data.title}`, {
        description: data.message,
        action: {
          label: 'View',
          onClick: () => window.location.href = `/alerts/${data.id}`,
        },
      });
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    });

    // Listen for new comments/mentions
    socket.on('comment:mention', (data) => {
      toast(`${data.author} mentioned you in a comment`, {
        description: data.content_preview,
      });
    });

    return () => {
      socketClient.disconnect();
    };
  }, [queryClient]);

  return null;
}
```

---

## 🏢 Tenant-Based Routing

### Subdomain Detection

```typescript
// lib/utils/subdomain.ts
export function getSubdomain(hostname: string): string | null {
  // Remove port if present
  const host = hostname.split(':')[0];
  
  // Split by dots
  const parts = host.split('.');
  
  // If localhost or IP, no subdomain
  if (parts.length <= 1 || parts[0] === 'localhost') {
    return null;
  }
  
  // Return first part as subdomain
  return parts[0];
}

export function getTenantFromSubdomain(subdomain: string): string {
  // Map subdomain to tenant ID
  // In production, this would query the backend
  return subdomain;
}
```

### Multi-Tenant Layout

```typescript
// app/layout.tsx
import { headers } from 'next/headers';
import { getSubdomain, getTenantFromSubdomain } from '@/lib/utils/subdomain';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const headersList = headers();
  const hostname = headersList.get('host') || '';
  const subdomain = getSubdomain(hostname);
  
  // Fetch tenant branding based on subdomain
  // This would typically come from an API or database
  const tenantId = subdomain ? getTenantFromSubdomain(subdomain) : null;

  return (
    <html lang="en">
      <body>
        <TenantProvider tenantId={tenantId}>
          {children}
        </TenantProvider>
      </body>
    </html>
  );
}
```

---

## 🎨 Complete Component Examples

### Dashboard Overview

```typescript
// app/(dashboard)/dashboard/page.tsx
'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { FileText, AlertTriangle, TrendingUp, Clock } from 'lucide-react';

export default function DashboardPage() {
  const { data: overview } = useQuery({
    queryKey: ['dashboard-overview'],
    queryFn: () => apiClient.get('/dashboard/overview/'),
  });

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Total Contracts
            </CardTitle>
            <FileText className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {overview?.summary.total_contracts}
            </div>
            <p className="text-xs text-gray-500">
              {overview?.summary.active_contracts} active
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              High Risk Contracts
            </CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {overview?.summary.high_risk_contracts}
            </div>
            <p className="text-xs text-gray-500">
              Require attention
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Contract Value
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${(parseFloat(overview?.summary.total_contract_value) / 1000000).toFixed(1)}M
            </div>
            <p className="text-xs text-gray-500">
              Total portfolio
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Expiring Soon
            </CardTitle>
            <Clock className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {overview?.summary.expiring_soon}
            </div>
            <p className="text-xs text-gray-500">
              Next 90 days
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts, tables, etc. */}
    </div>
  );
}
```

---

## 🚀 Summary

This frontend integration guide provides:

✅ **Complete API Layer** - Axios client with interceptors  
✅ **Type Safety** - Full TypeScript definitions  
✅ **Authentication** - JWT with refresh token handling  
✅ **File Upload** - Progress tracking, drag & drop  
✅ **Real-Time** - Socket.IO for notifications  
✅ **State Management** - Zustand for global state  
✅ **Data Fetching** - Tanstack Query for caching  
✅ **Multi-Tenancy** - Subdomain-based routing  

**Next Steps**:
1. Install dependencies
2. Set up environment variables
3. Implement components
4. Test with backend API
5. Deploy to production

---

**Documentation Version**: 1.0  
**Last Updated**: January 2024  
**Support**: dev@chainsight.ai

