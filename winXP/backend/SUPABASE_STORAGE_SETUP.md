# Supabase Storage Setup Guide

This guide will help you set up Supabase Storage for file uploads in your AI Second Brain application.

## Why Supabase Storage?

When deploying to cloud platforms like Vercel (serverless) or Railway (ephemeral containers), local file storage doesn't work:
- **Vercel**: No persistent file system (serverless functions)
- **Railway**: Files are lost when container restarts (ephemeral storage)

**Solution**: Supabase Storage provides cloud-hosted file storage with:
- ✅ Persistent storage across deployments
- ✅ Public URLs for file access
- ✅ CDN distribution for fast access
- ✅ Built-in authentication and access control

## Step 1: Create Storage Bucket

1. Go to your Supabase dashboard: https://app.supabase.com/
2. Select your project: `ahhkjfisxgtjcufqxkff`
3. Navigate to **Storage** in the left sidebar
4. Click **New Bucket**
5. Enter the following details:
   - **Name**: `knowledge-base`
   - **Public bucket**: ✅ **Enable** (for public file access)
   - **File size limit**: 50 MB (or as needed)
6. Click **Create Bucket**

## Step 2: Set Bucket Policies

The bucket is now public, but you need to configure access policies:

1. Click on the `knowledge-base` bucket
2. Go to **Policies** tab
3. Click **New Policy**
4. Create a policy for **SELECT** (read access):
   ```sql
   -- Policy name: Public Read Access
   CREATE POLICY "Public Read Access"
   ON storage.objects FOR SELECT
   USING (bucket_id = 'knowledge-base');
   ```

5. Create a policy for **INSERT** (upload access):
   ```sql
   -- Policy name: Public Upload Access
   CREATE POLICY "Public Upload Access"
   ON storage.objects FOR INSERT
   WITH CHECK (bucket_id = 'knowledge-base');
   ```

6. Create a policy for **UPDATE** (update access):
   ```sql
   -- Policy name: Public Update Access
   CREATE POLICY "Public Update Access"
   ON storage.objects FOR UPDATE
   USING (bucket_id = 'knowledge-base');
   ```

7. Create a policy for **DELETE** (delete access):
   ```sql
   -- Policy name: Public Delete Access
   CREATE POLICY "Public Delete Access"
   ON storage.objects FOR DELETE
   USING (bucket_id = 'knowledge-base');
   ```

## Step 3: Verify Configuration

1. Your backend `.env` should already have:
   ```env
   SUPABASE_URL=https://ahhkjfisxgtjcufqxkff.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

2. The bucket name in `app.py` is set to:
   ```python
   STORAGE_BUCKET = 'knowledge-base'
   ```

## Step 4: Test File Upload

### Using the UI:
1. Start your backend: `python app.py`
2. Open your frontend
3. Click on the desktop
4. Try uploading a file
5. File should appear on the desktop

### Using curl:
```bash
curl -X POST http://localhost:8001/api/upload \
  -F "file=@test.txt"
```

Expected response:
```json
{
  "success": true,
  "filename": "test.txt",
  "type": "text",
  "url": "https://ahhkjfisxgtjcufqxkff.supabase.co/storage/v1/object/public/knowledge-base/files/test.txt",
  "storage_path": "files/test.txt",
  "processed": true
}
```

## Step 5: Verify Files in Dashboard

1. Go to Supabase Dashboard → Storage → `knowledge-base`
2. You should see a `files/` folder
3. Inside you'll find your uploaded files
4. Click on any file to see its public URL

## How It Works

### Upload Flow:
```
User uploads file
    ↓
Backend receives file
    ↓
Upload to Supabase Storage (files/filename)
    ↓
Get public URL
    ↓
Save temporarily for processing
    ↓
Process to Qdrant (PDF/Image/Text)
    ↓
Return file URL to frontend
    ↓
Desktop displays file
```

### File Retrieval:
```
Frontend requests /api/files
    ↓
Backend lists files from Supabase Storage
    ↓
Returns array with file URLs
    ↓
Desktop displays file icons
    ↓
User clicks file → opens from public URL
```

## API Endpoints

### Upload File
```http
POST /api/upload
Content-Type: multipart/form-data

file: <file>
```

Response:
```json
{
  "success": true,
  "filename": "example.pdf",
  "type": "pdf",
  "url": "https://..../storage/.../files/example.pdf",
  "storage_path": "files/example.pdf",
  "processed": true
}
```

### List Files
```http
GET /api/files
```

Response:
```json
[
  {
    "name": "example.pdf",
    "path": "https://..../storage/.../files/example.pdf",
    "url": "https://..../storage/.../files/example.pdf",
    "size": 12345,
    "type": "pdf",
    "mime": "application/pdf",
    "icon": "/icons/pdf.png",
    "updated_at": "2024-01-30T12:00:00Z",
    "storage_path": "files/example.pdf"
  }
]
```

### Download File
```http
GET /api/download/<filename>
```

Serves the file from Supabase Storage.

## Troubleshooting

### Error: "Bucket not found"
- Ensure you created the `knowledge-base` bucket
- Check bucket name matches `STORAGE_BUCKET` in `app.py`

### Error: "Permission denied"
- Create storage policies (Step 2)
- Ensure bucket is set to **Public**

### Error: "Invalid API key"
- Verify `SUPABASE_KEY` in `.env`
- Use the **anon/public** key, not the service role key

### Files not appearing on desktop
- Check browser console for errors
- Verify `/api/files` returns file list
- Check CORS settings in backend

### Auto-processing not working
- Files are uploaded to Storage first
- Then downloaded temporarily for processing
- Check Qdrant connection and API key
- Review backend logs for processing errors

## Security Notes

### Public Bucket
- Files are accessible via public URLs
- Anyone with the URL can access the file
- Don't upload sensitive documents

### Restricting Access (Optional)
If you need authentication:

1. Set bucket to **Private**
2. Use Supabase Auth for user authentication
3. Update policies to check `auth.uid()`
4. Generate signed URLs with expiration:
   ```python
   signed_url = supabase.storage.from_(STORAGE_BUCKET).create_signed_url(
       path='files/example.pdf',
       expires_in=3600  # 1 hour
   )
   ```

## Production Deployment

When deploying to Railway:

1. Ensure `.env` has Supabase credentials
2. Railway will use the same Supabase Storage bucket
3. All uploaded files persist in Supabase (not Railway container)
4. Files accessible from any deployment (dev/staging/prod)

## File Size Limits

- Default: 50 MB per file
- Can be increased in Supabase Dashboard → Storage → Bucket Settings
- Consider chunked uploads for very large files

## CDN and Performance

Supabase Storage uses CDN for fast global access:
- Files are cached at edge locations
- Automatic image optimization available
- Use `transform` options for image resizing

Example:
```python
public_url = supabase.storage.from_(STORAGE_BUCKET).get_public_url(
    storage_path,
    transform={'width': 800, 'height': 600}
)
```

## Next Steps

✅ Storage bucket created
✅ Files uploading to cloud
✅ Desktop displays files from Supabase

Now you're ready to deploy:
1. Push code to GitHub
2. Deploy backend to Railway
3. Deploy frontend to Vercel
4. Test file upload in production

See `DEPLOYMENT.md` for full deployment guide.
