# Instagram Automation Pro - Backend

A production-ready FastAPI backend for automating Instagram interactions with rules-based automation, real-time webhooks, and comprehensive analytics.

## 🚀 Features

- **JWT Authentication** - Secure user authentication with token-based access
- **MongoDB Integration** - Scalable NoSQL database with Motor async driver
- **Rules Engine** - Create complex automation rules (comments, DMs, follows)
- **Activity Logging** - Complete audit trail of all automation actions
- **Statistics & Analytics** - Real-time and historical performance metrics
- **Instagram Integration** - Connect and manage multiple Instagram accounts
- **Webhooks Support** - Real-time updates from Instagram
- **Error Handling** - Comprehensive error handling with detailed error responses
- **CORS Support** - Production-ready CORS configuration
- **Rate Limiting** - Built-in rate limiting to prevent abuse
- **Logging** - Structured logging with customizable levels

## 📋 Requirements

- Python 3.8+
- MongoDB 4.4+
- pip or conda

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Aakashpatel1818/insta-automation-Backend-.git
cd insta-automation-Backend-
```

### 2. Create Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# OR using conda
conda create -n insta-automation python=3.10
conda activate insta-automation
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy template
cp .env.template .env

# Edit with your configuration
nano .env
```

**Key Configuration Variables:**

```env
# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
ENVIRONMENT=development
DEBUG=True

# Database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=instagram_automation

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS - Update for your frontend domain
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
CORS_CREDENTIALS=true

# Instagram API
INSTAGRAM_ACCESS_TOKEN=your_token_here
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_account_id
```

### 5. Setup MongoDB

**Option A: Local MongoDB**

```bash
# Install MongoDB (macOS with Homebrew)
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community

# Verify connection
mongosh --eval "db.version()"
```

**Option B: MongoDB Atlas (Cloud)**

1. Create account at [mongodb.com/cloud](https://www.mongodb.com/cloud)
2. Create a cluster
3. Get connection string
4. Update `MONGODB_URL` in `.env`

### 6. Run the Server

```bash
# Development (with auto-reload)
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Server will be available at: `http://localhost:8000`

**API Documentation:**
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

## 📚 API Endpoints

### Authentication

```bash
# Register
POST /api/auth/register
{
  "email": "user@example.com",
  "username": "john_doe",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}

# Login
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

# Get Current User
POST /api/auth/me
Headers: Authorization: Bearer {token}

# Change Password
POST /api/auth/change-password
Headers: Authorization: Bearer {token}
{
  "current_password": "OldPass123!",
  "new_password": "NewPass123!"
}
```

### Rules Management

```bash
# List Rules
GET /api/rules?skip=0&limit=10&is_active=true

# Create Rule
POST /api/rules
{
  "name": "Welcome DM",
  "rule_type": "dm",
  "trigger_keywords": ["hello", "hi"],
  "action_message": "Thanks for reaching out!",
  "is_case_sensitive": false
}

# Get Rule
GET /api/rules/{rule_id}

# Update Rule
PUT /api/rules/{rule_id}

# Delete Rule
DELETE /api/rules/{rule_id}

# Toggle Rule
POST /api/rules/{rule_id}/toggle
```

### Logs & Analytics

```bash
# List Logs
GET /api/logs?skip=0&limit=20&log_type=comment&status=success&days=7

# Get Summary Stats
GET /api/logs/stats/summary

# Get Daily Stats
GET /api/logs/stats/daily?days=30

# Clear Old Logs
DELETE /api/logs?days_old=30
```

### Instagram Integration

```bash
# Get Connected Accounts
GET /api/instagram/accounts

# Connect Account
POST /api/instagram/connect
{
  "access_token": "instagram_token",
  "instagram_id": "account_id"
}

# Disconnect Account
DELETE /api/instagram/accounts/{account_id}

# Sync Data
POST /api/instagram/sync/{account_id}
```

## 🗄️ Database Schema

### Collections

**users**
```javascript
{
  _id: ObjectId,
  email: String,
  username: String,
  hashed_password: String,
  first_name: String,
  last_name: String,
  is_active: Boolean,
  is_verified: Boolean,
  subscription_tier: String,
  created_at: Date,
  updated_at: Date,
  last_login: Date
}
```

**rules**
```javascript
{
  _id: ObjectId,
  user_id: String,
  name: String,
  rule_type: String,
  trigger_keywords: [String],
  action_message: String,
  is_active: Boolean,
  is_case_sensitive: Boolean,
  priority: Number,
  success_count: Number,
  failure_count: Number,
  created_at: Date,
  updated_at: Date
}
```

**logs**
```javascript
{
  _id: ObjectId,
  user_id: String,
  rule_id: String,
  log_type: String,
  status: String,
  message: String,
  target_username: String,
  created_at: Date
}
```

## 🚨 Error Handling

All errors follow this format:

```json
{
  "status": "error",
  "error_type": "validation_error",
  "detail": "Invalid email format",
  "status_code": 422,
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format",
      "type": "value_error.email"
    }
  ],
  "timestamp": "2026-01-04T13:00:00"
}
```

## 🔐 Security

- **JWT Tokens**: Short-lived tokens with configurable expiration
- **Password Hashing**: Bcrypt with salt for secure password storage
- **CORS Protection**: Configurable allowed origins
- **Rate Limiting**: Prevent abuse with request throttling
- **Input Validation**: Pydantic models for data validation
- **Error Handling**: No sensitive information in error messages

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### Logs Location

```bash
# Development
logs/app.log

# Production
/var/log/instagram-automation/app.log
```

## 🐳 Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t insta-automation-backend .
docker run -p 8000:8000 --env-file .env insta-automation-backend
```

## 🌍 Production Deployment

### Environment Setup

```env
ENVIRONMENT=production
DEBUG=False
SERVER_HOST=0.0.0.0
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
JWT_SECRET_KEY=<generate-random-256-bit-key>
MONGODB_URL=mongodb+srv://user:password@cluster.mongodb.net
```

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker app.main:app
```

### Using systemd

Create `/etc/systemd/system/instagram-automation.service`:

```ini
[Unit]
Description=Instagram Automation Pro Backend
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/instagram-automation-backend
Environment="PATH=/opt/instagram-automation-backend/venv/bin"
ExecStart=/opt/instagram-automation-backend/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app.main:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=process
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 🧪 Testing

```bash
# Install testing dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

## 📝 Project Structure

```
insta-automation-Backend-/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── rules.py
│   │       ├── logs.py
│   │       ├── instagram.py
│   │       └── webhooks.py
│   ├── core/
│   │   ├── config.py
│   │   ├── cors_config.py
│   │   ├── env_config.py
│   │   ├── security.py
│   │   └── logging_config.py
│   ├── db/
│   │   └── models.py
│   └── main.py
├── requirements.txt
├── .env.template
├── README.md
└── docker-compose.yml
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 📧 Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/Aakashpatel1818/insta-automation-Backend-/issues)
- Email: support@example.com

## 🙏 Acknowledgments

- FastAPI for the amazing async framework
- Motor for MongoDB async support
- Pydantic for data validation
