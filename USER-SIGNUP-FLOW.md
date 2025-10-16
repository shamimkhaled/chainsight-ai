# ChainSight AI User Signup & Multi-Tenancy Flow

## Overview 🎯
This guide explains how user signup works in ChainSight AI's multi-tenant architecture, including the complete flow from signup to daily usage.

## User Signup Process 📝

### Step 1: Company Registration (Admin/Owner)
When a company first signs up for ChainSight AI:

```http
POST /api/v2/accounts/users/register/
Content-Type: application/json

{
  "email": "admin@newcompany.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "John",
  "last_name": "Admin",
  "role": "admin",
  "company_name": "New Company Inc.",
  "subdomain": "newcompany"
}
```

**What happens internally:**

1. **Check if tenant exists**:
   ```python
   tenant = Tenant.objects.filter(subdomain=subdomain).first()
   if not tenant:
       # Create new tenant
       tenant = Tenant.objects.create(
           name=company_name,
           subdomain=subdomain,
           plan_type='free'  # Default plan
       )
   ```

2. **Create admin user**:
   ```python
   user = User.objects.create_user(
       email=email,
       password=password,
       tenant=tenant,  # Link to tenant
       role='admin',
       first_name=first_name,
       last_name=last_name
   )
   ```

3. **Generate tokens**:
   ```python
   refresh = RefreshToken.for_user(user)
   return {
       'user': UserSerializer(user).data,
       'tokens': {
           'refresh': str(refresh),
           'access': str(refresh.access_token),
       },
       'tenant': {
           'id': tenant.id,
           'name': tenant.name,
           'subdomain': tenant.subdomain
       }
   }
   ```

### Step 2: Frontend Receives Response
```json
{
  "user": {
    "id": "uuid",
    "email": "admin@newcompany.com",
    "first_name": "John",
    "last_name": "Admin",
    "role": "admin",
    "tenant": {
      "id": 1,
      "name": "New Company Inc.",
      "subdomain": "newcompany"
    }
  },
  "tokens": {
    "refresh": "eyJ0eXAi...",
    "access": "eyJ0eXAi..."
  },
  "tenant": {
    "id": 1,
    "name": "New Company Inc.",
    "subdomain": "newcompany"
  }
}
```

### Step 3: Frontend Stores Tenant Context
```javascript
// Store in localStorage/sessionStorage
localStorage.setItem('access_token', response.tokens.access);
localStorage.setItem('refresh_token', response.tokens.refresh);
localStorage.setItem('tenant_id', response.tenant.id);
localStorage.setItem('tenant_subdomain', response.tenant.subdomain);
localStorage.setItem('user', JSON.stringify(response.user));
```

## How Frontend Handles Multi-Tenancy 🔄

### Dynamic Tenant Context in API Calls

#### 1. **HTTP Interceptor Setup**
```javascript
// Axios interceptor for automatic tenant header
axios.interceptors.request.use((config) => {
  const tenantId = localStorage.getItem('tenant_id');
  const token = localStorage.getItem('access_token');

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  if (tenantId) {
    config.headers['X-Tenant-ID'] = tenantId;
  }

  return config;
});
```

#### 2. **All API Calls Include Tenant Header**
```javascript
// Contract upload
const uploadContract = async (file, metadata) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('industry', metadata.industry);
  formData.append('language', metadata.language);

  // X-Tenant-ID automatically added by interceptor
  return await axios.post('/api/v2/contracts/upload/', formData);
};

// List contracts
const getContracts = async () => {
  // X-Tenant-ID automatically added by interceptor
  return await axios.get('/api/v2/contracts/');
};
```

#### 3. **Tenant Context in React/Vue/Angular**
```javascript
// React Context/Provider
const TenantContext = React.createContext();

const TenantProvider = ({ children }) => {
  const [tenant, setTenant] = useState(() => {
    return {
      id: localStorage.getItem('tenant_id'),
      subdomain: localStorage.getItem('tenant_subdomain'),
      name: localStorage.getItem('tenant_name')
    };
  });

  return (
    <TenantContext.Provider value={{ tenant, setTenant }}>
      {children}
    </TenantContext.Provider>
  );
};

// Usage in components
const ContractList = () => {
  const { tenant } = useContext(TenantContext);

  useEffect(() => {
    // All API calls automatically include tenant context
    fetchContracts();
  }, [tenant.id]);

  return (
    <div>
      <h2>Contracts for {tenant.name}</h2>
      {/* Contract list */}
    </div>
  );
};
```

## Complete User Journey Example 🚀

### Scenario: New Company Onboarding

#### 1. **Company Owner Visits Website**
- Goes to `chainsight.ai/signup`
- Fills out company information

#### 2. **Signup Form Submission**
```javascript
const handleSignup = async (formData) => {
  try {
    const response = await axios.post('/api/v2/accounts/users/register/', {
      email: formData.email,
      password: formData.password,
      password_confirm: formData.password,
      first_name: formData.firstName,
      last_name: formData.lastName,
      role: 'admin',
      company_name: formData.companyName,
      subdomain: formData.subdomain
    });

    // Store tenant context
    localStorage.setItem('tenant_id', response.data.tenant.id);
    localStorage.setItem('tenant_subdomain', response.data.tenant.subdomain);
    localStorage.setItem('access_token', response.data.tokens.access);
    localStorage.setItem('refresh_token', response.data.tokens.refresh);

    // Redirect to dashboard
    navigate('/dashboard');

  } catch (error) {
    console.error('Signup failed:', error);
  }
};
```

#### 3. **Dashboard Loads with Tenant Context**
```javascript
const Dashboard = () => {
  const [contracts, setContracts] = useState([]);
  const [tenant] = useState(() => ({
    id: localStorage.getItem('tenant_id'),
    name: localStorage.getItem('tenant_name')
  }));

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // All these calls automatically include X-Tenant-ID header
      const [contractsRes, usersRes] = await Promise.all([
        axios.get('/api/v2/contracts/'),
        axios.get('/api/v2/accounts/users/')
      ]);

      setContracts(contractsRes.data.results);
      // Data is automatically filtered by tenant
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    }
  };

  return (
    <div>
      <h1>Welcome to {tenant.name}</h1>
      <ContractList contracts={contracts} />
    </div>
  );
};
```

#### 4. **Adding Team Members**
```javascript
const inviteUser = async (email, role) => {
  try {
    // This creates user in the same tenant
    await axios.post('/api/v2/accounts/users/', {
      email,
      role,
      // tenant is automatically set from X-Tenant-ID header
    });

    // Send invitation email...
  } catch (error) {
    console.error('Failed to invite user:', error);
  }
};
```

## Multi-Tenant Frontend Architecture 🏗️

### 1. **Tenant-Aware API Client**
```javascript
class ApiClient {
  constructor() {
    this.tenantId = localStorage.getItem('tenant_id');
    this.baseURL = process.env.REACT_APP_API_URL;

    this.client = axios.create({
      baseURL: this.baseURL,
      headers: {
        'X-Tenant-ID': this.tenantId
      }
    });

    // Auto-refresh tokens
    this.client.interceptors.response.use(
      response => response,
      this.handleTokenRefresh
    );
  }

  // All methods automatically include tenant context
  async getContracts() {
    return this.client.get('/api/v2/contracts/');
  }

  async uploadContract(file, metadata) {
    const formData = new FormData();
    formData.append('file', file);
    Object.keys(metadata).forEach(key => {
      formData.append(key, metadata[key]);
    });

    return this.client.post('/api/v2/contracts/upload/', formData);
  }
}
```

### 2. **Tenant Switcher Component**
```javascript
const TenantSwitcher = () => {
  const [tenants, setTenants] = useState([]);
  const { tenant, setTenant } = useContext(TenantContext);

  useEffect(() => {
    // Load user's accessible tenants
    loadUserTenants();
  }, []);

  const switchTenant = (newTenantId) => {
    localStorage.setItem('tenant_id', newTenantId);
    setTenant(tenants.find(t => t.id === newTenantId));

    // Reload page or update context
    window.location.reload();
  };

  return (
    <select
      value={tenant.id}
      onChange={(e) => switchTenant(e.target.value)}
    >
      {tenants.map(t => (
        <option key={t.id} value={t.id}>
          {t.name}
        </option>
      ))}
    </select>
  );
};
```

### 3. **Route Protection with Tenant Context**
```javascript
const PrivateRoute = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [tenant, setTenant] = useState(null);

  useEffect(() => {
    checkAuthAndTenant();
  }, []);

  const checkAuthAndTenant = async () => {
    const token = localStorage.getItem('access_token');
    const tenantId = localStorage.getItem('tenant_id');

    if (!token || !tenantId) {
      navigate('/login');
      return;
    }

    try {
      // Verify token and tenant access
      const response = await axios.get('/api/v2/accounts/users/me/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Tenant-ID': tenantId
        }
      });

      setIsAuthenticated(true);
      setTenant(response.data.tenant);
    } catch (error) {
      // Token invalid or tenant access denied
      localStorage.clear();
      navigate('/login');
    }
  };

  if (!isAuthenticated) {
    return <LoadingSpinner />;
  }

  return (
    <TenantContext.Provider value={{ tenant }}>
      {children}
    </TenantContext.Provider>
  );
};
```

## Dynamic Tenant Passing in Frontend 🎭

### 1. **URL-Based Tenant Detection**
```javascript
// For subdomain routing: tenant1.chainsight.ai
const getTenantFromSubdomain = () => {
  const hostname = window.location.hostname;
  const subdomain = hostname.split('.')[0];

  if (subdomain !== 'www' && subdomain !== 'chainsight') {
    return subdomain;
  }
  return null;
};

// For path-based: chainsight.ai/tenant1/dashboard
const getTenantFromPath = () => {
  const path = window.location.pathname;
  const match = path.match(/^\/([^\/]+)/);
  return match ? match[1] : null;
};
```

### 2. **Automatic Tenant Resolution**
```javascript
const resolveTenant = async (tenantIdentifier) => {
  try {
    // Try subdomain first
    let tenant = await axios.get(`/api/public/tenants/subdomain/${tenantIdentifier}`);

    if (!tenant) {
      // Try by ID
      tenant = await axios.get(`/api/public/tenants/${tenantIdentifier}`);
    }

    if (tenant) {
      localStorage.setItem('tenant_id', tenant.id);
      localStorage.setItem('tenant_subdomain', tenant.subdomain);
      return tenant;
    }
  } catch (error) {
    console.error('Tenant resolution failed:', error);
  }
  return null;
};
```

### 3. **Login with Tenant Context**
```javascript
const loginWithTenant = async (email, password, tenantId = null) => {
  try {
    const headers = {};

    // If tenant specified, include in headers
    if (tenantId) {
      headers['X-Tenant-ID'] = tenantId;
    }

    const response = await axios.post('/api/v2/accounts/users/login/', {
      email,
      password
    }, { headers });

    // Store tenant context from response
    const { user, tokens, tenant } = response.data;

    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
    localStorage.setItem('tenant_id', tenant.id);
    localStorage.setItem('tenant_subdomain', tenant.subdomain);

    return { user, tenant };

  } catch (error) {
    // If login fails without tenant, try to find user's tenant
    if (error.response?.status === 401 && !tenantId) {
      const userTenant = await findUserTenant(email);
      if (userTenant) {
        return loginWithTenant(email, password, userTenant.id);
      }
    }
    throw error;
  }
};
```

### 4. **Cross-Tenant Navigation**
```javascript
const navigateToTenant = (targetTenantId) => {
  // Update local storage
  localStorage.setItem('tenant_id', targetTenantId);

  // Update axios default headers
  axios.defaults.headers.common['X-Tenant-ID'] = targetTenantId;

  // Reload or navigate to dashboard
  window.location.href = '/dashboard';
};
```

## Complete Signup Flow Diagram 📊

```
User Visits chainsight.ai/signup
           ↓
    Fills Company Info
           ↓
POST /api/v2/accounts/users/register/
    {
      company_name: "ABC Corp",
      subdomain: "abc",
      admin_email: "admin@abc.com",
      ...
    }
           ↓
Backend: Create Tenant + Admin User
           ↓
Response: { user, tokens, tenant }
           ↓
Frontend: Store Context
    localStorage.setItem('tenant_id', tenant.id)
    localStorage.setItem('access_token', tokens.access)
           ↓
Redirect to /dashboard
           ↓
All Future API Calls Include:
    Authorization: Bearer <token>
    X-Tenant-ID: <tenant_id>
           ↓
User sees only their tenant's data
```

## Summary 🎯

### **For Frontend Developers:**
1. **Always include `X-Tenant-ID`** in API headers
2. **Store tenant context** after login/signup
3. **Use interceptors** for automatic header injection
4. **Handle tenant switching** gracefully
5. **Validate tenant access** on protected routes

### **For Backend Developers:**
1. **Filter all queries** by `request.user.tenant`
2. **Use middleware** to set tenant context
3. **Validate tenant permissions** on all operations
4. **Return tenant info** in auth responses

### **For Users:**
1. **Signup creates tenant** automatically
2. **All data isolated** by tenant
3. **Seamless experience** within their organization
4. **Secure sharing** with team members only

The multi-tenant architecture ensures each company gets a completely isolated, secure environment while sharing the same powerful platform! 🚀