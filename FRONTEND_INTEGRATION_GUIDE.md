# ChainSight AI Frontend Integration Guide

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication Flow](#authentication-flow)
3. [API Endpoints Reference](#api-endpoints-reference)
4. [Frontend Architecture](#frontend-architecture)
5. [State Management](#state-management)
6. [Real-time Updates](#real-time-updates)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)

---

## 1. Getting Started

### Backend Configuration

**Base URL**: `http://127.0.0.1:8000`  
**API Version**: `v2`  
**API Base**: `http://127.0.0.1:8000/api/v2/`

### Required Headers

All authenticated requests must include:

```javascript
{
  "Authorization": "Bearer <access_token>",
  "X-Tenant-ID": "<tenant_id>",
  "Content-Type": "application/json"
}
```

### CORS Configuration

Backend is configured to accept requests from:
- `http://localhost:3000` (React/Next.js default)
- `http://localhost:3001`  
- `http://127.0.0.1:3000`

Custom headers allowed:
- `X-Tenant-ID` (for multi-tenancy)
- Standard authentication headers

---

## 2. Authentication Flow

### Frontend Implementation Example (React/Next.js)

```typescript
// api/auth.ts
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000/api/v2';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'admin' | 'manager' | 'user' | 'viewer';
  full_name: string;
}

export interface AuthResponse {
  user: User;
  tokens: {
    access: string;
    refresh: string;
  };
}

// Login function
export const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  const response = await axios.post(`${API_BASE}/users/login/`, credentials, {
    headers: {
      'X-Tenant-ID': '1', // Get from subdomain or config
    },
  });
  
  // Store tokens
  localStorage.setItem('access_token', response.data.tokens.access);
  localStorage.setItem('refresh_token', response.data.tokens.refresh);
  localStorage.setItem('user', JSON.stringify(response.data.user));
  
  return response.data;
};

// Register function
export const register = async (data: any): Promise<AuthResponse> => {
  const response = await axios.post(`${API_BASE}/users/register/`, data, {
    headers: {
      'X-Tenant-ID': '1',
    },
  });
  
  // Store tokens
  localStorage.setItem('access_token', response.data.tokens.access);
  localStorage.setItem('refresh_token', response.data.tokens.refresh);
  localStorage.setItem('user', JSON.stringify(response.data.user));
  
  return response.data;
};

// Get current user
export const getCurrentUser = async (): Promise<User> => {
  const token = localStorage.getItem('access_token');
  
  const response = await axios.get(`${API_BASE}/users/me/`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'X-Tenant-ID': '1',
    },
  });
  
  return response.data;
};

// Refresh token
export const refreshToken = async (): Promise<string> => {
  const refresh = localStorage.getItem('refresh_token');
  
  const response = await axios.post(`${API_BASE}/auth/token/refresh/`, {
    refresh,
  });
  
  const newAccessToken = response.data.access;
  localStorage.setItem('access_token', newAccessToken);
  
  return newAccessToken;
};

// Logout
export const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
};
```

### Axios Interceptor Setup

```typescript
// api/axiosConfig.ts
import axios from 'axios';
import { refreshToken, logout } from './auth';

const API_BASE = 'http://127.0.0.1:8000/api/v2';

const axiosInstance = axios.create({
  baseURL: API_BASE,
});

// Request interceptor
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    const tenantId = localStorage.getItem('tenant_id') || '1';
    
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    config.headers['X-Tenant-ID'] = tenantId;
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for token refresh
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If 401 and not already retried, try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const newAccessToken = await refreshToken();
        originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
        return axiosInstance(originalRequest);
      } catch (refreshError) {
        // Refresh failed, logout user
        logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default axiosInstance;
```

---

## 3. API Endpoints Reference

### Authentication

```typescript
// api/auth.ts
import axiosInstance from './axiosConfig';

// Login
POST /users/login/
Body: { email, password }
Response: { user, tokens: { access, refresh } }

// Register
POST /users/register/
Body: { email, password, password_confirm, first_name, last_name, role }
Response: { user, tokens }

// Get current user
GET /users/me/
Response: User object

// Change password
POST /users/change_password/
Body: { old_password, new_password, new_password_confirm }
Response: { message }

// Refresh token
POST /auth/token/refresh/
Body: { refresh }
Response: { access }
```

### Contracts

```typescript
// api/contracts.ts
import axiosInstance from './axiosConfig';

export interface Contract {
  id: string;
  original_filename: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress_percentage: number;
  risk_score?: number;
  compliance_score?: number;
  industry: string;
  created_at: string;
  analyzed_at?: string;
}

// Upload contract
export const uploadContract = async (file: File, data: any) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('industry', data.industry);
  formData.append('language', data.language || 'english');
  
  if (data.contract_type) formData.append('contract_type', data.contract_type);
  if (data.tags) formData.append('tags', JSON.stringify(data.tags));
  
  const response = await axiosInstance.post('/contracts/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

// List contracts
export const listContracts = async (params?: any) => {
  const response = await axiosInstance.get('/contracts/', { params });
  return response.data;
};

// Get contract details
export const getContract = async (id: string) => {
  const response = await axiosInstance.get(`/contracts/${id}/`);
  return response.data;
};

// Get analysis results
export const getContractResults = async (id: string) => {
  const response = await axiosInstance.get(`/contracts/${id}/results/`);
  return response.data;
};

// Export PDF
export const exportPDF = async (id: string) => {
  const response = await axiosInstance.post(`/contracts/${id}/export/pdf/`);
  return response.data;
};

// Export DOCX
export const exportDOCX = async (id: string) => {
  const response = await axiosInstance.post(`/contracts/${id}/export/docx/`);
  return response.data;
};

// Delete contract
export const deleteContract = async (id: string) => {
  await axiosInstance.delete(`/contracts/${id}/`);
};

// Re-analyze contract
export const reanalyzeContract = async (id: string) => {
  const response = await axiosInstance.post(`/contracts/${id}/reanalyze/`);
  return response.data;
};
```

### Dashboard

```typescript
// api/dashboard.ts
import axiosInstance from './axiosConfig';

export interface DashboardStats {
  contracts: {
    total: number;
    completed: number;
    pending: number;
    processing: number;
    recent_30_days: number;
    expiring_soon_90_days: number;
  };
  risk: {
    high_risk_count: number;
    average_risk_score: number;
  };
  users: {
    total: number;
    active: number;
  };
  tenant: {
    name: string;
    plan_type: string;
    max_contracts: number;
    usage_percentage: number;
  };
}

// Get dashboard stats
export const getDashboardStats = async (): Promise<DashboardStats> => {
  const response = await axiosInstance.get('/dashboard/');
  return response.data;
};

// Get contract trends
export const getContractTrends = async (period: number = 30) => {
  const response = await axiosInstance.get('/dashboard/trends/', {
    params: { period },
  });
  return response.data;
};

// Get risk distribution
export const getRiskDistribution = async () => {
  const response = await axiosInstance.get('/dashboard/risk-distribution/');
  return response.data;
};
```

### Counterparties

```typescript
// api/counterparties.ts
import axiosInstance from './axiosConfig';

export interface Counterparty {
  id: string;
  name: string;
  legal_name: string;
  entity_type: string;
  risk_score?: number;
  risk_level: string;
  is_verified: boolean;
  created_at: string;
}

// List counterparties
export const listCounterparties = async (params?: any) => {
  const response = await axiosInstance.get('/counterparties/', { params });
  return response.data;
};

// Get counterparty details
export const getCounterparty = async (id: string) => {
  const response = await axiosInstance.get(`/counterparties/${id}/`);
  return response.data;
};

// Create counterparty
export const createCounterparty = async (data: any) => {
  const response = await axiosInstance.post('/counterparties/', data);
  return response.data;
};

// Update counterparty
export const updateCounterparty = async (id: string, data: any) => {
  const response = await axiosInstance.patch(`/counterparties/${id}/`, data);
  return response.data;
};

// Verify counterparty
export const verifyCounterparty = async (id: string, source: string) => {
  const response = await axiosInstance.post(`/counterparties/${id}/verify/`, {
    source,
  });
  return response.data;
};
```

---

## 4. Frontend Architecture

### Recommended Structure (React/Next.js)

```
frontend/
├── src/
│   ├── api/               # API client functions
│   │   ├── axiosConfig.ts
│   │   ├── auth.ts
│   │   ├── contracts.ts
│   │   ├── dashboard.ts
│   │   └── counterparties.ts
│   ├── components/        # Reusable components
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   └── RegisterForm.tsx
│   │   ├── contracts/
│   │   │   ├── ContractList.tsx
│   │   │   ├── ContractUpload.tsx
│   │   │   ├── ContractDetails.tsx
│   │   │   └── ContractAnalysis.tsx
│   │   ├── dashboard/
│   │   │   ├── StatsCard.tsx
│   │   │   └── TrendsChart.tsx
│   │   └── common/
│   │       ├── Button.tsx
│   │       ├── Table.tsx
│   │       └── Modal.tsx
│   ├── hooks/             # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useContracts.ts
│   │   └── useDashboard.ts
│   ├── pages/             # Next.js pages
│   │   ├── login.tsx
│   │   ├── dashboard.tsx
│   │   ├── contracts/
│   │   │   ├── index.tsx
│   │   │   └── [id].tsx
│   │   └── counterparties/
│   │       └── index.tsx
│   ├── context/           # React context
│   │   └── AuthContext.tsx
│   ├── types/             # TypeScript types
│   │   ├── auth.ts
│   │   ├── contract.ts
│   │   └── dashboard.ts
│   └── utils/             # Utility functions
│       ├── formatters.ts
│       └── validators.ts
```

---

## 5. State Management

### Context API Example (React)

```typescript
// context/AuthContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '../api/auth';
import * as authAPI from '../api/auth';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (credentials: any) => Promise<void>;
  logout: () => void;
  register: (data: any) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in
    const checkAuth = async () => {
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        setUser(JSON.parse(storedUser));
      }
      setLoading(false);
    };
    
    checkAuth();
  }, []);

  const login = async (credentials: any) => {
    const response = await authAPI.login(credentials);
    setUser(response.user);
  };

  const logout = () => {
    authAPI.logout();
    setUser(null);
  };

  const register = async (data: any) => {
    const response = await authAPI.register(data);
    setUser(response.user);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

### Custom Hook Example

```typescript
// hooks/useContracts.ts
import { useState, useEffect } from 'react';
import * as contractsAPI from '../api/contracts';

export const useContracts = (filters?: any) => {
  const [contracts, setContracts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchContracts = async () => {
    try {
      setLoading(true);
      const data = await contractsAPI.listContracts(filters);
      setContracts(data.results);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchContracts();
  }, [filters]);

  const uploadContract = async (file: File, data: any) => {
    const result = await contractsAPI.uploadContract(file, data);
    fetchContracts(); // Refresh list
    return result;
  };

  const deleteContract = async (id: string) => {
    await contractsAPI.deleteContract(id);
    fetchContracts(); // Refresh list
  };

  return {
    contracts,
    loading,
    error,
    uploadContract,
    deleteContract,
    refresh: fetchContracts,
  };
};
```

---

## 6. Real-time Updates

### Polling for Contract Status

```typescript
// hooks/useContractStatus.ts
import { useState, useEffect } from 'react';
import * as contractsAPI from '../api/contracts';

export const useContractStatus = (contractId: string) => {
  const [contract, setContract] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let intervalId: NodeJS.Timeout;

    const checkStatus = async () => {
      try {
        const data = await contractsAPI.getContract(contractId);
        setContract(data);
        
        // Stop polling if completed or failed
        if (data.status === 'completed' || data.status === 'failed') {
          if (intervalId) clearInterval(intervalId);
        }
        
        setLoading(false);
      } catch (error) {
        console.error('Error checking status:', error);
        setLoading(false);
      }
    };

    // Initial check
    checkStatus();

    // Poll every 5 seconds if processing
    if (contract?.status === 'pending' || contract?.status === 'processing') {
      intervalId = setInterval(checkStatus, 5000);
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [contractId, contract?.status]);

  return { contract, loading };
};
```

---

## 7. Error Handling

### Centralized Error Handler

```typescript
// utils/errorHandler.ts
export interface APIError {
  detail?: string;
  code?: string;
  [key: string]: any;
}

export const handleAPIError = (error: any): string => {
  if (error.response) {
    // Server responded with error
    const data = error.response.data as APIError;
    
    if (data.detail) {
      return data.detail;
    }
    
    // Validation errors
    if (typeof data === 'object') {
      const firstKey = Object.keys(data)[0];
      if (Array.isArray(data[firstKey])) {
        return data[firstKey][0];
      }
    }
    
    return `Error: ${error.response.status}`;
  } else if (error.request) {
    // Request made but no response
    return 'Network error. Please check your connection.';
  } else {
    // Something else happened
    return error.message || 'An unexpected error occurred';
  }
};

// Usage in component
import { handleAPIError } from '../utils/errorHandler';

const handleLogin = async () => {
  try {
    await login(credentials);
  } catch (error) {
    const errorMessage = handleAPIError(error);
    setError(errorMessage);
  }
};
```

---

## 8. Best Practices

### Security

```typescript
// 1. Never expose sensitive data
// ❌ Bad
console.log('Token:', accessToken);

// ✅ Good
if (process.env.NODE_ENV === 'development') {
  console.log('Auth check...');
}

// 2. Use environment variables
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v2';

// 3. Validate user input
import { z } from 'zod';

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(12),
});
```

### Performance

```typescript
// 1. Use React.memo for expensive components
export const ContractList = React.memo(({ contracts }: Props) => {
  // ...
});

// 2. Debounce search inputs
import { useDebouncedCallback } from 'use-debounce';

const debouncedSearch = useDebouncedCallback((value) => {
  fetchContracts({ search: value });
}, 500);

// 3. Use pagination
const [page, setPage] = useState(1);
const { contracts } = useContracts({ page, page_size: 20 });
```

### UX Improvements

```typescript
// 1. Loading states
{loading ? <Spinner /> : <ContractList contracts={contracts} />}

// 2. Empty states
{contracts.length === 0 && (
  <EmptyState
    title="No contracts yet"
    description="Upload your first contract to get started"
    action={<Button onClick={openUploadModal}>Upload Contract</Button>}
  />
)}

// 3. Progress indicators for uploads
const [uploadProgress, setUploadProgress] = useState(0);

await axios.post('/contracts/upload/', formData, {
  onUploadProgress: (progressEvent) => {
    const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
    setUploadProgress(progress);
  },
});
```

---

## Quick Start Checklist

- [ ] Set up axios with interceptors
- [ ] Implement authentication context
- [ ] Create login/register pages
- [ ] Build contract list page with filters
- [ ] Add contract upload functionality
- [ ] Create contract details page with analysis results
- [ ] Build dashboard with statistics
- [ ] Implement error handling
- [ ] Add loading and empty states
- [ ] Test all CRUD operations
- [ ] Set up proper TypeScript types
- [ ] Configure CORS headers
- [ ] Test token refresh flow
- [ ] Add real-time status updates

---

## Support

**API Documentation**: http://127.0.0.1:8000/api/docs/  
**Email**: support@chainsight.ai  
**GitHub**: https://github.com/shamimkhaled/chainsight-ai

---

**Happy Building! 🚀**

