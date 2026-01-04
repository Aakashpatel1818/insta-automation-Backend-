# Complete Setup Guide - Instagram Automation Pro

Step-by-step guide to get the entire application running locally.

## 👩‍💻 Prerequisites

- **Node.js** 16+ and npm 8+
- **Python** 3.8+ with pip
- **MongoDB** 4.4+ (local or cloud)
- **Git** for version control
- A code editor (VS Code recommended)

## 🚀 Quick Start (5 minutes)

### Backend

```bash
# Clone and setup
git clone https://github.com/Aakashpatel1818/insta-automation-Backend-.git
cd insta-automation-Backend-

# Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install and run
pip install -r requirements.txt
cp .env.template .env  # Edit with your config
uvicorn app.main:app --reload
```

Backend ready at: `http://localhost:8000/api/docs`

### Frontend

```bash
# Clone and setup
git clone https://github.com/Aakashpatel1818/insta-automation-Frontend.git
cd insta-automation-Frontend

# Install and run
npm install
cp .env.example .env.local
npm run dev
```

Frontend ready at: `http://localhost:5173`

## 📚 Detailed Setup

### 1. Backend Setup

#### 1.1 Clone Repository

```bash
git clone https://github.com/Aakashpatel1818/insta-automation-Backend-.git
cd insta-automation-Backend-
```

#### 1.2 Create Virtual Environment

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate

# Or with conda
conda create -n insta-automation python=3.10
conda activate insta-automation
```

#### 1.3 Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 1.4 Setup MongoDB

**Option A: Local MongoDB (macOS)**

```bash
# Install
brew tap mongodb/brew
brew install mongodb-community@6.0

# Start service
brew services start mongodb-community@6.0

# Verify (should return version)
mongosh --eval "db.version()"
```

**Option B: Local MongoDB (Windows)**

1. Download from [mongodb.com/try/download](https://www.mongodb.com/try/download/community)
2. Run installer
3. MongoDB starts automatically on port 27017
4. Verify: `mongosh --eval "db.version()"`

**Option C: MongoDB Atlas (Cloud - Recommended for Production)**

1. Go to [mongodb.com/cloud](https://www.mongodb.com/cloud)
2. Create free account
3. Create new project and cluster
4. Add IP whitelist (or `0.0.0.0/0` for development)
5. Create database user
6. Copy connection string
7. Update `MONGODB_URL` in `.env`

#### 1.5 Configure Environment

```bash
cp .env.template .env
```

Edit `.env` with your settings:

```env
# Development settings
ENVIRONMENT=development
DEBUG=True
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=instagram_automation

# JWT (Change this in production!)
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
CORS_CREDENTIALS=true

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

#### 1.6 Run Backend

```bash
# Development (with auto-reload)
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Check if running:**
```bash
curl http://localhost:8000/health
```

**Access documentation:**
- Swagger: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### 2. Frontend Setup

#### 2.1 Clone Repository

```bash
git clone https://github.com/Aakashpatel1818/insta-automation-Frontend.git
cd insta-automation-Frontend
```

#### 2.2 Install Dependencies

```bash
npm install
# or
yarn install
# or
pnpm install
```

#### 2.3 Configure Environment

```bash
cp .env.example .env.local
```

Edit `.env.local`:

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=Instagram Automation Pro
VITE_APP_VERSION=1.0.0
```

#### 2.4 Run Frontend

```bash
# Development
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

**Check if running:**
- Open http://localhost:5173 in browser

## 💡 Testing the Setup

### 1. Register New Account

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPassword123!"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'
```

You'll get back a token.

### 3. Use Token

```bash
# Get current user (replace TOKEN with actual token)
curl -X POST http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer TOKEN"
```

### 4. Test in Frontend

1. Navigate to http://localhost:5173/register
2. Create account with same credentials
3. You should be redirected to dashboard
4. Should see statistics (mock data initially)

## 💨 Troubleshooting

### Backend Issues

**Error: `Cannot connect to MongoDB`**

```bash
# Check MongoDB is running
mongosh --eval "db.version()"

# If not running:
brew services start mongodb-community@6.0  # macOS
# Windows: MongoDB should auto-start or check Services app
```

**Error: `Module not found`**

```bash
# Reinstall dependencies
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Error: `Port 8000 already in use`**

```bash
# Kill process using port 8000
lsof -ti:8000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :8000   # Windows
```

### Frontend Issues

**Error: `VITE_API_BASE_URL is not defined`**

```bash
# Make sure .env.local exists
cp .env.example .env.local

# Clear cache and restart
rm -rf node_modules/.vite
npm run dev
```

**Error: `Port 5173 already in use`**

```bash
# Use different port
VITE_PORT=5174 npm run dev
```

**Error: `API calls failing with CORS error`**

1. Check backend is running
2. Verify `ALLOWED_ORIGINS` in backend `.env`
3. Verify `VITE_API_BASE_URL` in frontend `.env.local`
4. Restart both services

### Database Issues

**MongoDB Atlas Connection String**

```
mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority
```

Make sure:
- Username and password are URL-encoded
- IP is whitelisted in Atlas
- Database name is in connection string

## 📋 Project Structure

```
project/
├── insta-automation-Backend-/
│   ├── app/
│   │   ├── api/routes/
│   │   ├── core/
│   │   ├── db/
│   │   └── main.py
│   ├── requirements.txt
│   ├── .env.template
│   └── README.md
│
├── insta-automation-Frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── utils/
│   │   └── types/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── README.md
│
└── SETUP.md (this file)
```

## 🌍 Next Steps

1. **Understand the Architecture**
   - Read backend [README.md](./insta-automation-Backend-/README.md)
   - Read frontend [README.md](./insta-automation-Frontend/README.md)

2. **Explore the Code**
   - Backend: Review routes in `app/api/routes/`
   - Frontend: Review components in `src/components/`

3. **Set Up IDE**
   - VS Code recommended
   - Install: Python, Thunder Client (API testing)
   - Backend: Python extensions
   - Frontend: ES7+ React/Redux/React-Native snippets

4. **Database Integration**
   - Implement MongoDB operations in routes (marked with TODO)
   - Use Motor for async database operations

5. **Instagram API Setup**
   - Get [Instagram Business Account](https://www.instagram.com/business/)
   - Set up [Instagram Graph API](https://developers.facebook.com/docs/instagram-graph-api/)
   - Add credentials to `.env`

## 👋 Getting Help

- **Docs**: Check README files in each directory
- **Issues**: Use GitHub Issues for bugs
- **Discussions**: Use GitHub Discussions for questions
- **Common Issues**: See Troubleshooting section above

## 💋 Tips

- Use `thunder-client` VS Code extension for API testing
- Use `MongoDB Compass` for database visualization
- Keep `npm run dev` and `uvicorn` running in separate terminals
- Use `curl` or Postman to test API endpoints
- Check browser console for frontend errors
- Check terminal logs for backend errors

Happy coding! 🌟
