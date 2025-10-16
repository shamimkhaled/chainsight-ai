# ChainSight AI Waitlist & Demo Booking Features

## Overview 🎯
ChainSight AI now includes comprehensive waitlist and demo booking features to help grow the user base and convert interested prospects into customers.

## Features Added ✅

### 1. **Waitlist Management** 📝
- **Public signup** for interested users before full launch
- **Interest tracking** (low, medium, high priority)
- **Lead qualification** and status management
- **Referral source tracking**
- **Email/SMS opt-in management**

### 2. **Demo Booking System** 📅
- **Public demo requests** with flexible scheduling
- **Automated availability** showing next 7 days
- **Admin scheduling** with calendar integration
- **Follow-up management** and status tracking
- **Meeting link management**

## Database Models 🗄️

### WaitlistEntry Model
```python
class WaitlistEntry(TimeStampedModel):
    """
    Waitlist for interested users before full launch
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=50, blank=True)

    # Interest level
    INTEREST_CHOICES = [
        ('low', 'Just curious'),
        ('medium', 'Planning to use soon'),
        ('high', 'Need this urgently'),
    ]
    interest_level = models.CharField(max_length=20, choices=INTEREST_CHOICES, default='medium')

    # Source tracking
    referral_source = models.CharField(max_length=100, blank=True)
    signup_source = models.CharField(max_length=100, default='website')

    # Status management
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('converted', 'Converted'),
        ('unsubscribed', 'Unsubscribed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Communication preferences
    email_opt_in = models.BooleanField(default=True)
    sms_opt_in = models.BooleanField(default=False)

    # Tracking metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
```

### DemoRequest Model
```python
class DemoRequest(TimeStampedModel):
    """
    Demo booking requests from potential customers
    """
    # Contact information
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=50, blank=True)

    # Scheduling preferences
    preferred_date = models.DateField(null=True, blank=True)
    preferred_time = models.TimeField(null=True, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')

    # Company details
    company_size = models.CharField(max_length=50, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    current_solution = models.CharField(max_length=200, blank=True)

    # Specific interests
    interests = models.JSONField(default=list, blank=True)  # Array of interests

    # Additional requirements
    special_requirements = models.TextField(blank=True)
    attendees = models.IntegerField(default=1)

    # Status tracking
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Meeting details
    scheduled_date = models.DateTimeField(null=True, blank=True)
    meeting_link = models.URLField(blank=True)
    calendar_event_id = models.CharField(max_length=200, blank=True)

    # Follow-up management
    notes = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)

    # Communication
    email_opt_in = models.BooleanField(default=True)

    # Tracking metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referral_source = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
```

## API Endpoints 🚀

### Waitlist Endpoints

#### 1. **Join Waitlist** (Public)
```
POST /api/v2/accounts/waitlist/join/
Content-Type: application/json

{
  "email": "john@company.com",
  "first_name": "John",
  "last_name": "Smith",
  "company_name": "Tech Corp",
  "job_title": "CTO",
  "phone": "+1-555-0123",
  "interest_level": "high",
  "referral_source": "google"
}

Response (201):
{
  "message": "Successfully joined the waitlist!",
  "position": 42,
  "entry": {
    "id": 1,
    "email": "john@company.com",
    "first_name": "John",
    "company_name": "Tech Corp",
    "interest_level": "high",
    "status": "pending",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

#### 2. **Get Waitlist Count** (Public)
```
GET /api/v2/accounts/waitlist/count/

Response (200):
{
  "total_count": 156,
  "message": "Join 156 others on the waitlist!"
}
```

#### 3. **Manage Waitlist Entries** (Admin Only)
```
GET /api/v2/accounts/waitlist/ - List all entries
GET /api/v2/accounts/waitlist/{id}/ - Get specific entry
PUT /api/v2/accounts/waitlist/{id}/ - Update entry status
DELETE /api/v2/accounts/waitlist/{id}/ - Remove entry
```

### Demo Booking Endpoints

#### 1. **Book a Demo** (Public)
```
POST /api/v2/accounts/demos/book/
Content-Type: application/json

{
  "email": "sarah@startup.com",
  "first_name": "Sarah",
  "last_name": "Johnson",
  "company_name": "AI Startup Inc.",
  "job_title": "CEO",
  "phone": "+1-555-0456",
  "preferred_date": "2024-01-20",
  "preferred_time": "14:00",
  "timezone": "America/New_York",
  "company_size": "11-50",
  "industry": "SaaS",
  "current_solution": "Manual contract review",
  "interests": ["contract_analysis", "risk_assessment"],
  "special_requirements": "Need integration with Salesforce",
  "attendees": 3
}

Response (201):
{
  "message": "Demo request submitted successfully!",
  "request_id": 1,
  "status": "pending",
  "estimated_response": "We will contact you within 24 hours to schedule your demo.",
  "request": {
    "id": 1,
    "email": "sarah@startup.com",
    "first_name": "Sarah",
    "company_name": "AI Startup Inc.",
    "preferred_date": "2024-01-20",
    "preferred_time": "14:00",
    "status": "pending",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

#### 2. **Check Demo Availability** (Public)
```
GET /api/v2/accounts/demos/availability/

Response (200):
{
  "timezone": "UTC",
  "availability": [
    {
      "date": "2024-01-16",
      "slots": [
        {"time": "09:00", "available": true},
        {"time": "10:00", "available": true},
        {"time": "11:00", "available": false},
        {"time": "14:00", "available": true},
        {"time": "15:00", "available": true},
        {"time": "16:00", "available": true}
      ]
    }
  ],
  "note": "All times are in UTC. We will confirm your preferred time slot."
}
```

#### 3. **Schedule Demo** (Admin Only)
```
POST /api/v2/accounts/demos/{id}/schedule/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "scheduled_date": "2024-01-20T14:00:00Z",
  "meeting_link": "https://meet.google.com/abc-defg-hij"
}

Response (200):
{
  "message": "Demo scheduled successfully",
  "demo_request": {
    "id": 1,
    "status": "scheduled",
    "scheduled_date": "2024-01-20T14:00:00Z",
    "meeting_link": "https://meet.google.com/abc-defg-hij"
  }
}
```

#### 4. **Complete Demo** (Admin Only)
```
POST /api/v2/accounts/demos/{id}/complete/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "notes": "Great demo! Customer very interested in enterprise features."
}

Response (200):
{
  "message": "Demo marked as completed",
  "demo_request": {
    "id": 1,
    "status": "completed",
    "notes": "Great demo! Customer very interested in enterprise features."
  }
}
```

## Frontend Integration 🎨

### Waitlist Signup Component
```javascript
const WaitlistSignup = () => {
  const [formData, setFormData] = useState({
    email: '',
    first_name: '',
    last_name: '',
    company_name: '',
    job_title: '',
    interest_level: 'medium'
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/api/v2/accounts/waitlist/join/', formData);
      alert(`Thanks! You're #${response.data.position} on the waitlist!`);
    } catch (error) {
      alert('You are already on the waitlist!');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        placeholder="Work email"
        value={formData.email}
        onChange={(e) => setFormData({...formData, email: e.target.value})}
        required
      />
      <input
        type="text"
        placeholder="First name"
        value={formData.first_name}
        onChange={(e) => setFormData({...formData, first_name: e.target.value})}
      />
      <input
        type="text"
        placeholder="Company"
        value={formData.company_name}
        onChange={(e) => setFormData({...formData, company_name: e.target.value})}
      />
      <select
        value={formData.interest_level}
        onChange={(e) => setFormData({...formData, interest_level: e.target.value})}
      >
        <option value="low">Just curious</option>
        <option value="medium">Planning to use soon</option>
        <option value="high">Need this urgently</option>
      </select>
      <button type="submit">Join Waitlist</button>
    </form>
  );
};
```

### Demo Booking Component
```javascript
const DemoBooking = () => {
  const [availability, setAvailability] = useState([]);
  const [formData, setFormData] = useState({
    email: '',
    first_name: '',
    company_name: '',
    preferred_date: '',
    preferred_time: '',
    interests: []
  });

  useEffect(() => {
    loadAvailability();
  }, []);

  const loadAvailability = async () => {
    const response = await axios.get('/api/v2/accounts/demos/availability/');
    setAvailability(response.data.availability);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/api/v2/accounts/demos/book/', formData);
      alert('Demo request submitted! We will contact you within 24 hours.');
    } catch (error) {
      alert('Error submitting demo request');
    }
  };

  return (
    <div>
      <h2>Book a Demo</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Work email"
          value={formData.email}
          onChange={(e) => setFormData({...formData, email: e.target.value})}
          required
        />
        <input
          type="text"
          placeholder="First name"
          value={formData.first_name}
          onChange={(e) => setFormData({...formData, first_name: e.target.value})}
          required
        />
        <input
          type="text"
          placeholder="Company"
          value={formData.company_name}
          onChange={(e) => setFormData({...formData, company_name: e.target.value})}
        />

        <h3>Preferred Date & Time</h3>
        <select
          value={formData.preferred_date}
          onChange={(e) => setFormData({...formData, preferred_date: e.target.value})}
        >
          {availability.map(day => (
            <option key={day.date} value={day.date}>
              {new Date(day.date).toLocaleDateString()}
            </option>
          ))}
        </select>

        <select
          value={formData.preferred_time}
          onChange={(e) => setFormData({...formData, preferred_time: e.target.value})}
        >
          <option value="09:00">9:00 AM</option>
          <option value="10:00">10:00 AM</option>
          <option value="14:00">2:00 PM</option>
          <option value="15:00">3:00 PM</option>
          <option value="16:00">4:00 PM</option>
        </select>

        <h3>What are you interested in?</h3>
        {['contract_analysis', 'risk_assessment', 'compliance_monitoring'].map(interest => (
          <label key={interest}>
            <input
              type="checkbox"
              checked={formData.interests.includes(interest)}
              onChange={(e) => {
                const newInterests = e.target.checked
                  ? [...formData.interests, interest]
                  : formData.interests.filter(i => i !== interest);
                setFormData({...formData, interests: newInterests});
              }}
            />
            {interest.replace('_', ' ').toUpperCase()}
          </label>
        ))}

        <button type="submit">Book Demo</button>
      </form>
    </div>
  );
};
```

## Admin Dashboard 📊

### Waitlist Management
```javascript
const WaitlistAdmin = () => {
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    loadWaitlist();
  }, []);

  const loadWaitlist = async () => {
    const response = await axios.get('/api/v2/accounts/waitlist/');
    setEntries(response.data.results);
  };

  const updateStatus = async (id, status) => {
    await axios.patch(`/api/v2/accounts/waitlist/${id}/`, { status });
    loadWaitlist();
  };

  return (
    <div>
      <h2>Waitlist Management</h2>
      <table>
        <thead>
          <tr>
            <th>Email</th>
            <th>Company</th>
            <th>Interest</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {entries.map(entry => (
            <tr key={entry.id}>
              <td>{entry.email}</td>
              <td>{entry.company_name}</td>
              <td>{entry.interest_level}</td>
              <td>{entry.status}</td>
              <td>
                <select
                  value={entry.status}
                  onChange={(e) => updateStatus(entry.id, e.target.value)}
                >
                  <option value="pending">Pending</option>
                  <option value="contacted">Contacted</option>
                  <option value="qualified">Qualified</option>
                  <option value="converted">Converted</option>
                </select>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
```

### Demo Management
```javascript
const DemoAdmin = () => {
  const [demos, setDemos] = useState([]);

  useEffect(() => {
    loadDemos();
  }, []);

  const loadDemos = async () => {
    const response = await axios.get('/api/v2/accounts/demos/');
    setDemos(response.data.results);
  };

  const scheduleDemo = async (id, date, link) => {
    await axios.post(`/api/v2/accounts/demos/${id}/schedule/`, {
      scheduled_date: date,
      meeting_link: link
    });
    loadDemos();
  };

  return (
    <div>
      <h2>Demo Management</h2>
      {demos.map(demo => (
        <div key={demo.id} className="demo-card">
          <h3>{demo.first_name} {demo.last_name}</h3>
          <p>{demo.company_name} - {demo.email}</p>
          <p>Status: {demo.status}</p>
          <p>Requested: {demo.preferred_date} at {demo.preferred_time}</p>

          {demo.status === 'pending' && (
            <button onClick={() => scheduleDemo(demo.id, '2024-01-20T14:00:00Z', 'https://meet.google.com/abc')}>
              Schedule Demo
            </button>
          )}

          {demo.status === 'scheduled' && (
            <div>
              <p>Scheduled: {new Date(demo.scheduled_date).toLocaleString()}</p>
              <a href={demo.meeting_link} target="_blank">Meeting Link</a>
              <button onClick={() => completeDemo(demo.id)}>
                Mark Complete
              </button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
```

## Business Impact 💼

### Waitlist Benefits
- **Lead Generation**: Capture interested users before launch
- **Market Research**: Understand user needs and interests
- **Conversion Funnel**: Track from interest to customer
- **Email Marketing**: Build subscriber list for announcements

### Demo Benefits
- **Qualification**: Identify serious prospects
- **Product Education**: Showcase value proposition
- **Objection Handling**: Address concerns in real-time
- **Sales Acceleration**: Move prospects through pipeline faster

## Technical Implementation 🔧

### Database Migrations
```bash
# Generate migrations
python manage.py makemigrations accounts

# Apply migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
```

### API Testing with Postman
```json
// Waitlist signup
{
  "email": "test@example.com",
  "first_name": "Test",
  "company_name": "Test Corp",
  "interest_level": "high"
}

// Demo booking
{
  "email": "demo@example.com",
  "first_name": "Demo",
  "company_name": "Demo Corp",
  "preferred_date": "2024-01-20",
  "preferred_time": "14:00",
  "interests": ["contract_analysis"]
}
```

## Summary 🎯

ChainSight AI now includes:

### ✅ **Waitlist Features**
- Public signup with interest tracking
- Lead qualification and status management
- Referral source and conversion tracking
- Admin management dashboard

### ✅ **Demo Booking Features**
- Public demo requests with scheduling
- Automated availability checking
- Admin scheduling with calendar integration
- Follow-up and status tracking

### ✅ **API Endpoints**
- `POST /api/v2/accounts/waitlist/join/` - Join waitlist
- `GET /api/v2/accounts/waitlist/count/` - Get waitlist count
- `POST /api/v2/accounts/demos/book/` - Book demo
- `GET /api/v2/accounts/demos/availability/` - Check availability

### ✅ **Admin Features**
- Waitlist management with status updates
- Demo scheduling and completion tracking
- Lead qualification and follow-up management

These features help convert interested prospects into qualified leads and paying customers! 🚀