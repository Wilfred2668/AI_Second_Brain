# AI Second Brain - Production Deployment Guide

## Overview
This is a Windows XP-themed AI assistant with long-term memory powered by Qdrant vector database and Google Gemini AI.

## Architecture
- **Frontend**: React (Windows XP theme) - Deploy to Vercel
- **Backend**: Flask + Qdrant + Gemini - Deploy to Railway/Render (NOT Vercel - needs persistent connections)
- **Vector DB**: Qdrant Cloud (managed service)
- **AI Model**: Google Gemini 2.0 Flash

---

## 🚀 Deployment Instructions

### Backend Deployment (Railway - RECOMMENDED)

**Why Railway instead of Vercel?**
- Backend needs persistent connections for Qdrant and embedding models
- Vercel has 10-second timeout for serverless functions
- Railway provides persistent containers perfect for ML workloads

#### Option 1: Deploy to Railway (Recommended)

1. **Sign up at [Railway.app](https://railway.app)**

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account and select this repository
   - Set root directory to `/winXP/backend`

3. **Configure Environment Variables**
   ```
   QDRANT_URL=https://your-cluster.gcp.cloud.qdrant.io
   QDRANT_API_KEY=your-qdrant-api-key
   GEMINI_API_KEY=your-gemini-api-key
   COLLECTION_NAME=memories
   VECTOR_SIZE=384
   FLASK_ENV=production
   FRONTEND_URL=https://your-frontend.vercel.app
   ```

4. **Add Start Command**
   ```bash
   gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120
   ```

5. **Deploy**
   - Railway will auto-deploy on git push
   - Copy your backend URL (e.g., `https://your-app.railway.app`)

#### Option 2: Deploy to Render

1. **Sign up at [Render.com](https://render.com)**

2. **Create New Web Service**
   - Connect GitHub repository
   - Root Directory: `winXP/backend`
   - Build Command: `pip install -r requirements-prod.txt`
   - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120`

3. **Add Environment Variables** (same as Railway)

4. **Choose Plan**: Free tier available (spins down after inactivity)

---

### Frontend Deployment (Vercel)

1. **Sign up at [Vercel.com](https://vercel.com)**

2. **Import Project**
   - Click "Add New" → "Project"
   - Import your GitHub repository
   - Root Directory: `winXP`

3. **Configure Build Settings**
   - Framework Preset: Create React App
   - Build Command: `npm run build`
   - Output Directory: `build`

4. **Add Environment Variable**
   ```
   REACT_APP_API_URL=https://your-backend.railway.app
   ```
   (Use your Railway backend URL from above)

5. **Deploy**
   - Click "Deploy"
   - Vercel will auto-deploy on git push to main branch

---

### Qdrant Cloud Setup

1. **Sign up at [Qdrant Cloud](https://cloud.qdrant.io)**

2. **Create Cluster**
   - Free tier: 1GB storage
   - Choose region (e.g., GCP Europe West)

3. **Get Credentials**
   - Copy Cluster URL: `https://xxxxx.gcp.cloud.qdrant.io`
   - Copy API Key from dashboard

4. **Initialize Collection**
   - Run `clear_memory.py` after first backend deployment to create collection
   - Or backend will auto-create on first run

---

### Google Gemini API Setup

1. **Get API Key**
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create new API key
   - Copy key for environment variables

2. **Enable Gemini 2.0 Flash**
   - Free tier: 15 requests/minute
   - Paid tier: Higher limits

---

## 📁 File Structure

```
winXP/
├── src/                    # React frontend
│   ├── components/
│   │   └── Clippy/        # AI assistant UI
│   └── config.js          # API URL configuration
├── backend/               # Flask backend
│   ├── app.py            # Main application
│   ├── clear_memory.py   # Database reset utility
│   ├── requirements.txt  # Dependencies
│   ├── requirements-prod.txt  # Production dependencies
│   └── vercel.json       # (Not used - use Railway)
├── public/
│   └── downloads/        # Knowledge base files (PDFs, text, images)
└── vercel.json           # Frontend deployment config
```

---

## 🔧 Local Development

### Backend
```bash
cd winXP/backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env  # Edit with your keys
python app.py
```

### Frontend
```bash
cd winXP
npm install
# Create .env file
echo "REACT_APP_API_URL=http://localhost:8001" > .env
npm start
```

---

## 🧹 Clear Memory Database

```bash
cd winXP/backend
python clear_memory.py
```
Deletes all:
- Vector embeddings in Qdrant
- Chat sessions in SQLite
- Conversation history

---

## 📊 Features

✅ Windows XP themed interface  
✅ AI assistant with long-term memory  
✅ PDF, text file, and image OCR processing  
✅ Cross-session conversation memory  
✅ Chat session management  
✅ Semantic search with Qdrant  
✅ Google Gemini 2.0 Flash integration  

---

## 🔐 Security Notes

- Never commit `.env` files with real API keys
- Use environment variables in production
- Set proper CORS origins in production
- Qdrant Cloud handles encryption at rest
- Use HTTPS for all production endpoints

---

## 💰 Cost Estimates (Free Tiers)

- **Railway**: $5/month free credits (enough for hobby projects)
- **Vercel**: Free for personal projects
- **Qdrant Cloud**: 1GB free forever
- **Google Gemini**: 15 requests/minute free

**Total**: Can run for FREE or ~$5/month

---

## 🐛 Troubleshooting

### Backend won't start
- Check environment variables are set
- Verify Qdrant credentials
- Ensure Python 3.8+ installed

### Frontend can't connect to backend
- Verify `REACT_APP_API_URL` is set correctly
- Check backend is running and accessible
- Verify CORS is configured properly

### Memory not persisting
- Check Qdrant connection
- Verify collection is created
- Run `clear_memory.py` and restart

### Out of memory on Railway
- Reduce `CHUNK_SIZE` in app.py
- Use lighter embedding model
- Upgrade Railway plan

---

## 📝 Environment Variables Summary

### Backend (Railway/Render)
```
QDRANT_URL=
QDRANT_API_KEY=
GEMINI_API_KEY=
COLLECTION_NAME=memories
VECTOR_SIZE=384
FLASK_ENV=production
FRONTEND_URL=https://your-frontend.vercel.app
```

### Frontend (Vercel)
```
REACT_APP_API_URL=https://your-backend.railway.app
```

---

## 📞 Support

For issues, check:
1. Backend logs on Railway/Render
2. Browser console for frontend errors
3. Qdrant Cloud dashboard for database status
4. Google AI Studio for API quota

---

## 🎉 You're Ready!

1. Deploy backend to Railway
2. Deploy frontend to Vercel  
3. Set up Qdrant Cloud
4. Get Gemini API key
5. Configure environment variables
6. Upload files to knowledge base
7. Start chatting!
