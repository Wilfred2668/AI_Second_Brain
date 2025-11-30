# 🚀 Production Deployment Checklist

## Quick Setup Steps

### ✅ 1. Database Setup (Supabase)

**Already Done:**
- ✅ Supabase project created
- ✅ API keys configured in `.env`

**To Do:**
- [ ] Run SQL schema in Supabase SQL Editor:
  1. Open [Supabase Dashboard](https://app.supabase.com/)
  2. Go to SQL Editor
  3. Copy content from `backend/supabase_schema.sql`
  4. Execute query
  5. Verify tables created: `chat_sessions`, `messages`

### ✅ 2. File Storage Setup (Supabase Storage)

**To Do:**
- [ ] Create storage bucket:
  1. Open [Supabase Dashboard](https://app.supabase.com/) → Storage
  2. Click "New Bucket"
  3. Name: `knowledge-base`
  4. Public: ✅ **Enable**
  5. Click "Create Bucket"

📘 **Detailed guide:** `backend/SUPABASE_STORAGE_SETUP.md`

### ✅ 3. Vector Database (Qdrant Cloud)

**Already Done:**
- ✅ Qdrant cluster created
- ✅ Collection: `memories`
- ✅ API keys configured

**No action needed** ✅

### ✅ 4. AI Model (Google Gemini)

**Already Done:**
- ✅ API key obtained
- ✅ Model: Gemini 2.0 Flash
- ✅ Configured in `.env`

**No action needed** ✅

---

## Deploy Backend (Railway)

### Option A: Via Railway Dashboard

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Configure:
   - **Root Directory:** `winXP/backend`
   - **Build Command:** (auto-detected from `Procfile`)
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 2`

6. Add environment variables (copy from `backend/.env`):
   ```
   SUPABASE_URL=https://ahhkjfisxgtjcufqxkff.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   QDRANT_URL=https://f69114dd-2247-478a-be48-78aeab2811a0.europe-west3-0.gcp.cloud.qdrant.io
   QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   GEMINI_API_KEY=AIzaSyDbqPytq3qe7I71KWNmYgKhhEO8Xta9MKo
   COLLECTION_NAME=memories
   VECTOR_SIZE=384
   FLASK_ENV=production
   FRONTEND_URL=https://your-app.vercel.app
   ```

7. Click "Deploy"
8. **Copy your Railway URL** (e.g., `https://your-app.railway.app`)

### Option B: Via Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
cd winXP/backend
railway init

# Add environment variables
railway variables set SUPABASE_URL="https://ahhkjfisxgtjcufqxkff.supabase.co"
railway variables set SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
railway variables set QDRANT_URL="https://f69114dd-2247-478a-be48-78aeab2811a0.europe-west3-0.gcp.cloud.qdrant.io"
railway variables set QDRANT_API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
railway variables set GEMINI_API_KEY="AIzaSyDbqPytq3qe7I71KWNmYgKhhEO8Xta9MKo"
railway variables set COLLECTION_NAME="memories"
railway variables set VECTOR_SIZE="384"
railway variables set FLASK_ENV="production"
railway variables set FRONTEND_URL="https://your-app.vercel.app"

# Deploy
railway up
```

---

## Deploy Frontend (Vercel)

### Option A: Via Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. Configure:
   - **Root Directory:** `winXP`
   - **Framework Preset:** Create React App
   - **Build Command:** `npm run build`
   - **Output Directory:** `build`

5. Add environment variable:
   ```
   REACT_APP_API_URL=https://your-app.railway.app
   ```
   (Use the Railway URL from previous step)

6. Click "Deploy"
7. **Copy your Vercel URL** (e.g., `https://your-app.vercel.app`)

### Option B: Via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from winXP directory
cd winXP
vercel

# Follow prompts:
# - Link to existing project? No
# - What's your project name? ai-second-brain
# - In which directory is your code located? ./
# - Auto-detected Project Settings: Yes

# Add environment variable
vercel env add REACT_APP_API_URL
# Enter: https://your-app.railway.app

# Deploy to production
vercel --prod
```

---

## Update CORS Configuration

After deploying, update `FRONTEND_URL` in Railway:

1. Go to Railway dashboard
2. Select your backend project
3. Variables → `FRONTEND_URL`
4. Update to your Vercel URL: `https://your-app.vercel.app`
5. Save changes (Railway will redeploy automatically)

---

## Test Production Deployment

### Backend Health Check:
```bash
curl https://your-app.railway.app/api/health
```

Expected response:
```json
{"status": "ok", "service": "file-server"}
```

### Test Chat:
```bash
curl -X POST https://your-app.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello!",
    "session_id": "test-123"
  }'
```

### Test File Upload:
```bash
curl -X POST https://your-app.railway.app/api/upload \
  -F "file=@test.txt"
```

Expected response:
```json
{
  "success": true,
  "filename": "test.txt",
  "url": "https://...supabase.co/storage/.../files/test.txt",
  "processed": true
}
```

### Frontend:
1. Open `https://your-app.vercel.app`
2. Click Clippy → Start chatting
3. Try uploading a file
4. Check desktop for file icons
5. Ask Clippy about uploaded content

---

## Environment Variables Reference

### Backend (Railway)
| Variable | Value | Purpose |
|----------|-------|---------|
| `SUPABASE_URL` | `https://ahhkjfisxgtjcufqxkff.supabase.co` | Database connection |
| `SUPABASE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` | Database API key |
| `QDRANT_URL` | `https://f69114dd-2247...gcp.cloud.qdrant.io` | Vector database |
| `QDRANT_API_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` | Qdrant auth |
| `GEMINI_API_KEY` | `AIzaSyDbqPytq3qe7I71KWNmYgKhhEO8Xta9MKo` | AI model |
| `COLLECTION_NAME` | `memories` | Vector collection |
| `VECTOR_SIZE` | `384` | Embedding dimension |
| `FLASK_ENV` | `production` | Environment mode |
| `FRONTEND_URL` | `https://your-app.vercel.app` | CORS origin |

### Frontend (Vercel)
| Variable | Value | Purpose |
|----------|-------|---------|
| `REACT_APP_API_URL` | `https://your-app.railway.app` | Backend API endpoint |

---

## Verification Checklist

### ✅ Supabase
- [ ] SQL schema executed (tables created)
- [ ] Storage bucket `knowledge-base` created
- [ ] Bucket set to public
- [ ] Storage policies configured (optional)

### ✅ Railway (Backend)
- [ ] Project deployed
- [ ] All environment variables set
- [ ] Health check endpoint responds
- [ ] Chat endpoint working
- [ ] File upload endpoint working

### ✅ Vercel (Frontend)
- [ ] Project deployed
- [ ] Environment variable `REACT_APP_API_URL` set
- [ ] Frontend loads successfully
- [ ] Can connect to backend API
- [ ] CORS working (no console errors)

### ✅ Integration Tests
- [ ] Chat sessions persist (check Supabase)
- [ ] Files upload to Supabase Storage
- [ ] Files display on desktop
- [ ] Files auto-process to Qdrant
- [ ] Clippy can answer questions about uploaded files
- [ ] Long-term memory working across sessions

---

## Common Issues & Solutions

### Issue: CORS errors in frontend
**Solution:** Update `FRONTEND_URL` in Railway to match your Vercel URL

### Issue: "Bucket not found" error
**Solution:** Create `knowledge-base` bucket in Supabase Storage

### Issue: Files not processing to Qdrant
**Solution:** Check Qdrant API key and connection in Railway logs

### Issue: Backend timeout on Railway
**Solution:** Increase timeout in Procfile: `--timeout 180`

### Issue: Database connection failed
**Solution:** Verify `SUPABASE_URL` and `SUPABASE_KEY` in Railway variables

---

## Monitoring & Logs

### Railway Logs:
```bash
railway logs
```

Or view in Railway dashboard → Deployments → Logs

### Vercel Logs:
View in Vercel dashboard → Deployments → [deployment] → Logs

### Supabase Logs:
View in Supabase dashboard → Database → Logs

---

## Cost Estimate

| Service | Tier | Cost |
|---------|------|------|
| Supabase | Free | $0/month |
| Qdrant Cloud | Free | $0/month |
| Gemini API | Pay-as-go | ~$0.10/1000 requests |
| Railway | Hobby | $5/month |
| Vercel | Hobby | $0/month |
| **Total** | | **~$5/month** |

---

## Next Steps After Deployment

1. **Custom Domain** (Optional):
   - Add custom domain in Vercel settings
   - Update `FRONTEND_URL` in Railway

2. **Analytics** (Optional):
   - Add Google Analytics to frontend
   - Track usage in Railway/Vercel dashboards

3. **Backups**:
   - Supabase: Automatic backups included
   - Qdrant: Download snapshots from dashboard

4. **Scaling**:
   - Railway: Increase workers in Procfile
   - Vercel: Automatic scaling
   - Qdrant: Upgrade to paid tier for more vectors

---

## Documentation Reference

- 📘 **File Storage Setup:** `backend/SUPABASE_STORAGE_SETUP.md`
- 📘 **Database Setup:** `backend/SUPABASE_SETUP.md`
- 📘 **Full Deployment Guide:** `DEPLOYMENT.md`
- 📘 **Quick Start:** `QUICK_START.md`
- 📘 **Storage Summary:** `FILE_STORAGE_SUMMARY.md`

---

**Ready to deploy?** Start with Step 1 above! 🚀
