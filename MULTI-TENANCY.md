# ChainSight AI Multi-Tenancy Guide

## What is Multi-Tenancy? 🤔

**Multi-tenancy** is like having multiple separate apartments in one building. Each tenant (organization) lives in their own apartment and can't see or access other tenants' spaces, even though they share the same building (server).

### Real-World Analogy
Imagine a big apartment building:
- **Building** = ChainSight AI server
- **Apartments** = Each organization's data space
- **Tenants** = Different companies using the software
- **Landlord** = ChainSight AI administrators

Each company sees only their own contracts, users, and data - complete privacy!

## How ChainSight AI Multi-Tenancy Works 🔧

### 1. **Tenant Model** - The Foundation
Every organization gets a `Tenant` record:

```python
class Tenant(models.Model):
    name = "Acme Corporation"        # Company name
    subdomain = "acme"               # Unique identifier (acme.chainsight.ai)
    plan_type = "professional"       # Free, Starter, Professional, Enterprise
    max_users = 500                  # User limit
    max_contracts = 50000           # Contract limit
    status = "active"                # Active, Suspended, Inactive
```

### 2. **User Isolation** - Users Belong to Tenants
Every user is linked to exactly one tenant:

```python
class User(models.Model):
    tenant = models.ForeignKey(Tenant)  # Links to their organization
    email = "john@acme.com"
    role = "manager"                    # Admin, Manager, User, Viewer
```

### 3. **Automatic Data Filtering** - Magic Happens Here
The system automatically filters data by tenant:

```python
# When John from Acme logs in, he only sees Acme's contracts
contracts = Contract.objects.filter(tenant=john.tenant)

# When Sarah from XYZ Corp logs in, she only sees XYZ's contracts
contracts = Contract.objects.filter(tenant=sarah.tenant)
```

## Step-by-Step: How Multi-Tenancy Works in Practice 📋

### Step 1: Organization Signs Up
```
Company: "TechStart Inc."
Subdomain: "techstart"
Plan: "Starter" (100 users, 10k contracts)
```

### Step 2: Tenant Record Created
```sql
INSERT INTO tenants (name, subdomain, plan_type, max_users)
VALUES ('TechStart Inc.', 'techstart', 'starter', 100);
```

### Step 3: First User Created
```sql
INSERT INTO users (tenant_id, email, role)
VALUES (1, 'admin@techstart.com', 'admin');
```

### Step 4: User Logs In
```
POST /api/v2/accounts/users/login/
X-Tenant-ID: 1
{
  "email": "admin@techstart.com",
  "password": "password123"
}
```

### Step 5: System Remembers Tenant Context
```python
# Middleware sets tenant context for all requests
request.tenant = Tenant.objects.get(id=1)  # TechStart Inc.
_thread_local.tenant = request.tenant
```

### Step 6: All Data Filtered Automatically
```python
# User uploads contract
contract = Contract.objects.create(
    tenant=request.tenant,  # Automatically set to TechStart
    uploaded_by=request.user,
    file_path="...",
    status="pending"
)

# User lists contracts - only sees TechStart's contracts
contracts = Contract.objects.filter(tenant=request.tenant)
```

## How Users Experience Multi-Tenancy 👥

### For a Regular User at TechStart Inc.

1. **Login**: User logs in with `user@techstart.com`
2. **Tenant Detection**: System identifies tenant via:
   - API Header: `X-Tenant-ID: 1`
   - Subdomain: `techstart.chainsight.ai`
   - User Context: User's tenant relationship

3. **Data Access**: User can only see:
   - Contracts uploaded by TechStart employees
   - Users who work at TechStart
   - Settings specific to TechStart

4. **Complete Isolation**: User cannot see:
   - Any data from other companies
   - Other companies' users
   - System-wide settings

## API Pipeline with Multi-Tenancy 🔄

### Request Flow

```
1. User Request → 2. Middleware → 3. View → 4. Database → 5. Response
       ↓              ↓              ↓           ↓              ↓
   X-Tenant-ID    Tenant Set     Filtered     Tenant Data    Filtered
   Header         in Context     Queries      Only         Response
```

### Example API Call

```http
POST /api/v2/contracts/upload/
Authorization: Bearer <jwt_token>
X-Tenant-ID: 1
Content-Type: multipart/form-data

# File: contract.pdf
# Industry: technology
```

**What happens internally:**

1. **Middleware Checks**: `X-Tenant-ID: 1` header present
2. **Tenant Lookup**: Finds "TechStart Inc." tenant
3. **Context Set**: `request.tenant = techstart_tenant`
4. **File Upload**: File goes to `s3://chainsight/tenant_1/contracts/`
5. **Database Save**: Contract linked to tenant_1
6. **Response**: Only tenant_1 data returned

## Managing Multi-Tenancy as Admin 👑

### Creating New Organizations

```python
# Create new tenant
tenant = Tenant.objects.create(
    name="New Company Inc.",
    subdomain="newcompany",
    plan_type="starter"
)

# Create admin user
admin = User.objects.create_user(
    email="admin@newcompany.com",
    password="securepass123",
    tenant=tenant,
    role="admin"
)
```

### Switching Between Tenants

```python
# API requests specify tenant via header
headers = {
    'Authorization': f'Bearer {token}',
    'X-Tenant-ID': '2'  # Switch to different tenant
}
```

### Tenant Management Commands

```bash
# Create tenant programmatically
python manage.py shell -c "
from apps.tenants.models import Tenant
Tenant.objects.create(name='ABC Corp', subdomain='abc', plan_type='professional')
"

# List all tenants
python manage.py shell -c "
from apps.tenants.models import Tenant
for t in Tenant.objects.all():
    print(f'{t.name} ({t.subdomain}) - {t.plan_type}')
"
```

## Security & Data Isolation 🛡️

### Row-Level Security
- **Database Level**: All queries automatically filtered by tenant
- **API Level**: Middleware enforces tenant context
- **File Storage**: Files stored in tenant-specific S3 folders

### Permission System
```python
class IsTenantMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.tenant == request.user.tenant
```

### Data Leakage Prevention
- Users cannot query other tenants' data
- Files are stored in isolated S3 buckets
- API responses filtered by tenant context
- Audit logs track all tenant activities

## Common Multi-Tenancy Patterns 🎯

### 1. **Tenant-Specific Settings**
```python
# Each tenant can have custom settings
tenant.settings = {
    'theme': 'dark',
    'language': 'en',
    'notifications': True
}
```

### 2. **Plan-Based Features**
```python
if request.tenant.plan_type == 'enterprise':
    # Enable advanced features
    allow_custom_integrations = True
```

### 3. **Resource Quotas**
```python
# Check limits before allowing actions
if Contract.objects.filter(tenant=request.tenant).count() >= request.tenant.max_contracts:
    raise PermissionDenied("Contract limit exceeded")
```

## Troubleshooting Multi-Tenancy Issues 🔧

### Problem: User Can't See Data
**Solution**: Check `X-Tenant-ID` header is correct

### Problem: Wrong Tenant Data
**Solution**: Verify middleware is setting tenant context properly

### Problem: Permission Denied
**Solution**: Ensure user belongs to the correct tenant

### Problem: Data Leakage
**Solution**: Check all queries include `tenant` filtering

## Best Practices 📚

### For Developers
1. **Always filter by tenant** in queries
2. **Use tenant context** from request
3. **Test with multiple tenants** during development
4. **Audit data access** patterns

### For Administrators
1. **Monitor tenant usage** against limits
2. **Regular security audits** of tenant isolation
3. **Plan upgrades** based on usage patterns
4. **Backup tenant data** separately

### For Users
1. **Use correct subdomain** for web access
2. **Include X-Tenant-ID** in API calls
3. **Report data visibility issues** immediately

## Migration to Multi-Tenancy 📦

If converting from single-tenant to multi-tenant:

1. **Create tenant records** for existing organizations
2. **Add tenant_id** to all existing data
3. **Update user accounts** with tenant relationships
4. **Migrate file storage** to tenant-specific folders
5. **Update API clients** to include tenant headers

## Summary 🎯

ChainSight AI's multi-tenancy ensures:
- **Complete data isolation** between organizations
- **Scalable architecture** for multiple clients
- **Secure API access** with tenant context
- **Easy management** of organizations and users
- **Plan-based features** and resource limits

Each organization gets their own secure, isolated environment while sharing the same powerful contract analysis platform! 🚀