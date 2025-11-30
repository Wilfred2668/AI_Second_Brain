# Quick Start - Production Deployment

## ⚠️ IMPORTANT: Backend Deployment Location

**DO NOT deploy backend to Vercel!**

The backend requires:
- Long-running processes (embedding models)
- Persistent connections to Qdrant
- ML model loading (sentence-transformers)

**✅ Use Railway or Render instead** (see DEPLOYMENT.md for full guide)

---

## Quick Deploy Steps

### 1. Backend → Railway (5 minutes)

```bash
# Push to GitHub first
git add .
git commit -m "Production ready"
git push
```

1. Go to [railway.app](https://railway.app)
2. Create new project from GitHub
3. Set root directory: `winXP/backend`
4. Add environment variables (see .env.example)
5. Start command: `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120`
6. Copy your Railway URL

### 2. Frontend → Vercel (3 minutes)

1. Go to [vercel.com](https://vercel.com)
2. Import GitHub repository
3. Root directory: `winXP`
4. Add environment variable:
   ```
   REACT_APP_API_URL=https://your-backend.railway.app
   ```
5. Deploy!

### 3. Set up Supabase Database & Storage (4 minutes)

1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Copy URL and API key from Settings → API
4. Run SQL from `backend/supabase_schema.sql` in SQL Editor
5. Create Storage bucket named `knowledge-base`:
   - Go to Storage → New Bucket
   - Name: `knowledge-base`
   - Public bucket: ✅ Enable
6. Add credentials to Railway environment variables

📘 See `backend/SUPABASE_STORAGE_SETUP.md` for detailed setup

### 4. Set up Qdrant Cloud (2 minutes)

1. Sign up at [cloud.qdrant.io](https://cloud.qdrant.io)
2. Create free cluster
3. Copy URL and API key
4. Add to Railway environment variables

### 5. Get Gemini API Key (1 minute)

1. Visit [aistudio.google.com](https://aistudio.google.com/app/apikey)
2. Create API key
3. Add to Railway environment variables

---

## Environment Variables

### Railway (Backend)
```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-anon-key
QDRANT_URL=https://xxxxx.gcp.cloud.qdrant.io
QDRANT_API_KEY=your-key
GEMINI_API_KEY=your-key
COLLECTION_NAME=memories
VECTOR_SIZE=384
FLASK_ENV=production
FRONTEND_URL=https://your-app.vercel.app
```

### Vercel (Frontend)
```
REACT_APP_API_URL=https://your-app.railway.app
```

---

## Files Created for Production

✅ `winXP/vercel.json` - Frontend deployment config  
✅ `winXP/backend/Procfile` - Railway/Render start command  
✅ `winXP/backend/runtime.txt` - Python version  
✅ `winXP/backend/requirements-prod.txt` - Production dependencies  
✅ `winXP/src/config.js` - API URL configuration  
✅ `DEPLOYMENT.md` - Full deployment guide  

---

## Cost: $0-5/month

- Railway: $5 free credits/month
- Vercel: Free forever
- Qdrant: 1GB free
- Gemini: 15 req/min free

---

## Need Help?

Read full guide: `DEPLOYMENT.md`
