# 🖥️ AI Second Brain - Windows XP Edition

A nostalgic Windows XP-themed AI assistant with long-term memory, powered by Qdrant vector database and Google Gemini AI.

## 🚀 Production Ready

Both frontend and backend are configured for production deployment!

### Quick Deploy

**Backend → Railway** (NOT Vercel - needs persistent connections)
- Supports long-running ML models
- Persistent Qdrant connections
- File: `backend/Procfile` configured

**Frontend → Vercel**
- Optimized React build
- Environment variable support
- File: `vercel.json` configured

### 📖 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide with Railway, Render, Vercel
- **[QUICK_START.md](QUICK_START.md)** - 10-minute deployment walkthrough

### 🎯 What's Configured

✅ **Frontend**
- Environment-based API URL (`src/config.js`)
- Vercel deployment config (`vercel.json`)
- Production build optimized
- CORS handling

✅ **Backend**
- Railway Procfile with gunicorn
- Production requirements (`requirements-prod.txt`)
- Environment variable support
- CORS configured for production
- Python 3.10 runtime

✅ **Database**
- Qdrant Cloud connection ready
- SQLite for chat sessions
- Memory clear utility (`clear_memory.py`)

### 💰 Hosting Costs

**Free Tier**: $0-5/month
- Railway: $5 credits
- Vercel: Free
- Qdrant: 1GB free
- Gemini: 15 req/min free

### 🔑 Environment Variables Needed

**Backend (Railway)**
```
QDRANT_URL=https://your-cluster.gcp.cloud.qdrant.io
QDRANT_API_KEY=your-key
GEMINI_API_KEY=your-key
FLASK_ENV=production
FRONTEND_URL=https://your-app.vercel.app
```

**Frontend (Vercel)**
```
REACT_APP_API_URL=https://your-backend.railway.app
```

### 📁 Production Files

Created for you:
- `backend/Procfile` - Railway start command
- `backend/runtime.txt` - Python 3.10
- `backend/requirements-prod.txt` - Production dependencies
- `backend/vercel.json` - (Reference only - use Railway)
- `vercel.json` - Frontend deployment
- `src/config.js` - API URL configuration
- `.env.example` - Environment templates

### 🎮 Features

- 🤖 AI assistant with cross-session memory
- 📄 PDF, text file, and image (OCR) processing
- 💬 Chat session management
- 🔍 Semantic search with Qdrant
- 🎨 Authentic Windows XP interface
- 🧠 Vector embeddings with sentence-transformers

### 🚦 Next Steps

1. Read [DEPLOYMENT.md](DEPLOYMENT.md) for full guide
2. Set up Qdrant Cloud (free tier)
3. Get Gemini API key (free tier)
4. Deploy backend to Railway
5. Deploy frontend to Vercel
6. Add environment variables
7. Start chatting!

---

**⚠️ Important**: Do NOT deploy backend to Vercel. Use Railway or Render for persistent connections.

**📞 Need Help?** Check [DEPLOYMENT.md](DEPLOYMENT.md) for troubleshooting.
