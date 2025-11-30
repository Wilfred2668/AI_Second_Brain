# 🔄 Database Migration: SQLite → Supabase

## ✅ Migration Complete!

The backend has been successfully migrated from SQLite to Supabase PostgreSQL.

---

## 📋 What to Do Now

### 1. Create Database Tables in Supabase

1. **Go to your Supabase Dashboard**
   - URL: https://supabase.com/dashboard/project/ahhkjfisxgtjcufqxkff
   - Navigate to **SQL Editor**

2. **Run the SQL Script**
   - Open the file: `backend/supabase_schema.sql`
   - Copy ALL the SQL code
   - Paste into Supabase SQL Editor
   - Click **RUN**

3. **Verify Tables Created**
   - Go to **Table Editor** in Supabase
   - You should see:
     - `chat_sessions` table
     - `messages` table

---

### 2. Update Your .env File

Your `.env` file should have:

```env
# Qdrant Configuration
QDRANT_URL=https://your-cluster.gcp.cloud.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key

# Google Gemini Configuration
GEMINI_API_KEY=your-gemini-api-key

# Supabase Configuration (Already configured for you!)
SUPABASE_URL=https://ahhkjfisxgtjcufqxkff.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFoaGtqZmlzeGd0amN1ZnF4a2ZmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ1MTU0OTAsImV4cCI6MjA4MDA5MTQ5MH0.Gc56hU7BEvWFHw5K13C9K9dO0WY1vedOSD51ef8Tsto

# Collection Configuration  
COLLECTION_NAME=memories
VECTOR_SIZE=384
```

---

### 3. Install New Dependencies

```bash
cd backend
pip install supabase postgrest
# Or reinstall all:
pip install -r requirements.txt
```

---

### 4. Start the Backend

```bash
python app.py
```

You should see:
```
✓ Supabase database connected successfully
✓ Qdrant collection already exists: memories
 * Running on http://127.0.0.1:8001
```

---

## 🎯 What Changed

### Removed
- ❌ SQLite (`sqlite3` module)
- ❌ Local `chat_sessions.db` file
- ❌ `get_db_path()` function

### Added
- ✅ Supabase client
- ✅ PostgreSQL database (cloud-hosted)
- ✅ Better scalability for production
- ✅ Real-time capabilities (future use)

---

## 📊 Database Schema

### Table: `chat_sessions`
| Column | Type | Description |
|--------|------|-------------|
| session_id | TEXT (PK) | Unique session identifier |
| title | TEXT | Chat session title |
| created_at | TIMESTAMPTZ | When created |
| updated_at | TIMESTAMPTZ | Last updated (auto-updates) |

### Table: `messages`
| Column | Type | Description |
|--------|------|-------------|
| id | BIGSERIAL (PK) | Auto-increment ID |
| session_id | TEXT (FK) | Links to chat_sessions |
| sender | TEXT | 'user' or 'bot' |
| message | TEXT | Message content |
| timestamp | TIMESTAMPTZ | When sent |

---

## 🔍 Verification

Test your setup:

```bash
# Check connection
curl http://localhost:8001/api/sessions

# Create a new session
curl -X POST http://localhost:8001/api/sessions/new \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Chat"}'
```

---

## 🚀 Production Benefits

- **Scalability**: PostgreSQL handles more connections
- **Reliability**: Supabase provides backups
- **Features**: Real-time subscriptions, Row Level Security
- **Monitoring**: Built-in dashboard and logs
- **Free Tier**: 500MB database, 2GB bandwidth/month

---

## 🐛 Troubleshooting

### "Table 'chat_sessions' does not exist"
→ Run `supabase_schema.sql` in Supabase SQL Editor

### "Connection refused"
→ Check SUPABASE_URL and SUPABASE_KEY in .env

### "pip install supabase" fails
→ Upgrade pip: `pip install --upgrade pip`

---

## 📝 Files Modified

- ✏️ `backend/app.py` - Replaced all SQLite with Supabase
- ✏️ `backend/requirements.txt` - Added supabase, postgrest
- ✏️ `backend/requirements-prod.txt` - Added supabase, postgrest
- ✏️ `backend/.env.example` - Added Supabase config
- 📄 `backend/supabase_schema.sql` - NEW: Database schema
- 📄 `backend/MIGRATION.md` - NEW: This file

---

## ✅ Ready!

Once you've:
1. ✅ Created tables in Supabase
2. ✅ Updated .env file
3. ✅ Installed dependencies
4. ✅ Started backend

Your app is now using Supabase! 🎉

---

**Note**: Old `chat_sessions.db` file is no longer used. You can delete it or keep it as a backup.
