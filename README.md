# ChainSight AI - Django Backend

A comprehensive Django REST Framework backend for contract analysis and management, designed to scale to 500K+ users.

## Features

- **Multi-Tenant Architecture**: Complete tenant isolation with subdomain support
- **Contract Analysis**: AI-powered contract analysis using OpenAI GPT-4
- **Document Processing**: Support for PDF, DOCX, and other document formats
- **Real-time Alerts**: Configurable alert system for contract risks and compliance
- **Supplier Risk Management**: Comprehensive supplier monitoring and assessment
- **RAG Chat**: AI-powered chat interface for contract queries
- **Scalable Infrastructure**: Redis caching, PostgreSQL, MongoDB, Celery async tasks
- **Production Ready**: Docker, monitoring, security features

## Quick Start

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/shamimkhaled/chainsight-ai.git
   cd chainsight-ai
   ```

2. **Run the setup script**
   ```bash
   ./scripts/setup_dev.sh
   ```

3. **Start development services**
   ```bash
   # Terminal 1: Django server
   source venv/bin/activate
   python manage.py runserver

   # Terminal 2: Celery worker
   source venv/bin/activate
   celery -A config worker -l info

   # Terminal 3: Celery beat
   source venv/bin/activate
   celery -A config beat -l info
   ```

### Docker Setup

1. **Copy environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

## API Documentation

- **Base URL**: `http://localhost:8000/api/v2/`
- **Authentication**: JWT tokens
- **API Docs**: `http://localhost:8000/api/docs/`

### Authentication

```bash
# Get JWT token
curl -X POST http://localhost:8000/api/v2/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@chainsight.ai", "password": "admin123!"}'

# Use token in requests
curl -H "Authorization: Bearer <your-token>" \
  http://localhost:8000/api/v2/contracts/
```

### Key Endpoints

- `POST /api/v2/users/register/` - User registration
- `POST /api/v2/auth/token/` - Get JWT tokens
- `POST /api/v2/contracts/upload/` - Upload contract for analysis
- `GET /api/v2/contracts/{id}/results/` - Get analysis results
- `POST /api/v2/contracts/{id}/export/pdf/` - Export PDF report

## Project Structure

```
chainsight_backend/
├── config/                          # Django settings
│   ├── settings/
│   │   ├── base.py                 # Base settings
│   │   ├── development.py          # Dev settings
│   │   └── production.py           # Production settings
│   ├── urls.py
│   ├── celery.py
│   └── wsgi.py
├── apps/                           # Django applications
│   ├── core/                       # Core functionality
│   ├── tenants/                    # Multi-tenancy
│   ├── accounts/                   # User management
│   ├── contracts/                  # Contract management
│   ├── analysis/                   # Contract analysis
│   ├── counterparties/             # Counterparty management
│   ├── suppliers/                  # Supplier risk management
│   ├── chat/                       # RAG Chat AI
│   ├── alerts/                     # Notification & alerts
│   ├── integrations/               # ERP/CRM integrations
│   ├── repository/                 # Document repository
│   ├── compliance/                 # Compliance management
│   └── dashboard/                  # Dashboard & analytics
├── static/                         # Static files
├── media/                          # Media files
├── templates/                      # Django templates
├── scripts/                        # Utility scripts
├── tests/                          # Test suite
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration
├── docker-compose.yml              # Docker Compose
└── .env.example                    # Environment template
```

## Technology Stack

- **Backend**: Django 5.0, Django REST Framework
- **Database**: PostgreSQL (primary), MongoDB (analysis data)
- **Cache**: Redis
- **Message Queue**: RabbitMQ
- **Async Tasks**: Celery
- **AI/ML**: OpenAI GPT-4, Pinecone (vector DB)
- **File Storage**: AWS S3
- **Authentication**: JWT
- **Deployment**: Docker, Gunicorn

## Development

### Running Tests

```bash
# Run all tests
python manage.py test

# Run with coverage
pytest --cov=apps --cov-report=html
```

### Code Quality

```bash
# Run linting
flake8 apps/

# Run type checking
mypy apps/
```

### Database Management

```bash
# Create migrations
python manage.py makemigrations

# Run migrations
python manage.py migrate

# Seed data
python scripts/seed_data.py
```

## Production Deployment

### Environment Variables

Copy `.env.example` to `.env` and configure:

- Database credentials
- Redis/RabbitMQ URLs
- AWS S3 credentials
- OpenAI API key
- Email/SMS service credentials

### Docker Deployment

```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose up -d --scale celery_worker=4
```

### Monitoring

- **Celery Flower**: `http://localhost:5555`
- **Health Checks**: `/api/health/`
- **Metrics**: Prometheus integration
- **Logging**: Structured logging with rotation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Email: support@chainsight.ai
- Documentation: https://docs.chainsight.ai
- Issues: https://github.com/shamimkhaled/chainsight-ai/issues

---

**Built for scale. Designed for intelligence.** 🚀