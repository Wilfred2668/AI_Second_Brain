# Quick Start Guide - AI Second Brain

## Step 1: Install Dependencies

Open PowerShell in the backend directory and run:

```powershell
cd D:\Codes\hidev-quad\AI_Second_Brain\winXP\backend
.\venv\Scripts\activate
pip install -r requirements.txt
```

## Step 2: Update Qdrant URL

Edit the `.env` file and replace `YOUR_CLUSTER_URL` with your actual Qdrant Cloud cluster URL:

```
QDRANT_URL=https://your-actual-cluster.qdrant.io
```

## Step 3: Start Backend Server

```powershell
python app.py
```

You should see:
```
AI Second Brain Backend Starting...
✓ Qdrant collection already exists: memories
Server running on http://localhost:8001
```

## Step 4: Start Frontend

In a new terminal:

```powershell
cd D:\Codes\hidev-quad\AI_Second_Brain\winXP
npm start
```

## Step 5: Process Your Files

Open the browser and use Clippy to chat, or manually process files:

```powershell
# Process all files at once
curl -X POST http://localhost:8001/api/process_all_files
```

## Step 6: Chat with Clippy!

Click on the Clippy icon in the bottom-right corner and start chatting!

Try asking:
- "What files do I have?"
- "Tell me about the PDFs"
- "Summarize my notes"
- "What did we discuss before?"

## Architecture Overview

```
Frontend (React) ─────> Backend (Flask) ─────> Qdrant Cloud
                              │
                              └────> Gemini AI
```

## Features You Can Use

✅ **Smart File Search**: Ask about your files and get relevant answers
✅ **Memory**: All conversations are remembered
✅ **Context-Aware**: Clippy references specific files when answering
✅ **Automatic Updates**: Edit files and memories update automatically
✅ **Multi-Format**: PDFs, images (OCR), and text files

## Troubleshooting

**Backend won't start?**
- Make sure you've updated the QDRANT_URL in `.env`
- Check that all dependencies are installed
- Verify Python 3.8+ is being used

**Clippy says "can't connect"?**
- Make sure backend is running on port 8001
- Check for CORS errors in browser console
- Verify frontend is on port 3000

**OCR not working?**
- Install Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
- Add to PATH or the image processing will skip text extraction

## Next Steps

1. Add your files to `winXP/public/downloads/`
2. Process them using the API or let them be processed on access
3. Start chatting with Clippy!
4. Edit text files - memories update automatically
5. Enjoy your AI Second Brain!
