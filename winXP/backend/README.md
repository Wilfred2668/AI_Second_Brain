# AI Second Brain Backend

A Flask-based backend system that integrates Qdrant vector database and Google Gemini AI to create an intelligent memory system for your files and conversations.

## Features

✅ **Qdrant Vector Database Integration**
- Stores all files and chat history as embeddings
- Semantic search with similarity threshold
- Automatic memory updates when files change

✅ **File Processing**
- PDF text extraction and chunking
- Image OCR text extraction (Tesseract)
- Text file memory synchronization

✅ **Chat Memory System**
- All conversations stored permanently
- Retrieval-Augmented Generation (RAG)
- Context-aware responses using Gemini Flash 2.0

✅ **Smart Retrieval**
- Relevance-based search (not fixed top-k)
- Multi-source context (files + chat history)
- Filename references in responses

## Setup Instructions

### 1. Install Python Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

### 2. Configure Tesseract OCR (Optional, for image processing)

Download and install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki

Add Tesseract to your PATH or update the path in the code.

### 3. Configure Environment Variables

The `.env` file is already created with your API keys:

```
QDRANT_URL=https://YOUR_CLUSTER_URL.qdrant.io
QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.bbqayy0qW_AWJAQLYBTOr1N6YBneSMTlX-J0Ihfs9yM
GEMINI_API_KEY=AIzaSyAn_NDXxixeKGENduIRZxjpJJpMIUzLAYk
COLLECTION_NAME=memories
VECTOR_SIZE=384
```

**⚠️ Important:** Update `QDRANT_URL` with your actual Qdrant Cloud cluster URL.

### 4. Start the Backend Server

```powershell
python app.py
```

The server will start on `http://localhost:8001`

## API Endpoints

### File Management
- `GET /api/files` - List all files
- `POST /api/save/<filename>` - Save file and update memory
- `GET /api/download/<filename>` - Download file

### Memory Processing
- `POST /api/process_pdf` - Process PDF file
- `POST /api/process_image` - Process image file
- `POST /api/process_all_files` - Process all files in downloads folder
- `DELETE /api/delete_memory/<filename>` - Delete file memory

### Chat
- `POST /api/chat` - Chat with AI assistant (RAG-enabled)

### Health
- `GET /api/health` - Health check

## Usage Examples

### Process All Files
```bash
curl -X POST http://localhost:8001/api/process_all_files
```

### Chat with Assistant
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What files do I have about machine learning?"}'
```

### Save and Update Text File
```bash
curl -X POST http://localhost:8001/api/save/notes.txt \
  -H "Content-Type: text/plain" \
  -d "My important notes about AI"
```

## Architecture

### Embedding Model
- **Model:** `all-MiniLM-L6-v2` (384 dimensions)
- **Library:** SentenceTransformers

### Vector Database
- **Database:** Qdrant Cloud
- **Collection:** memories
- **Distance Metric:** COSINE

### AI Model
- **Model:** Gemini 2.0 Flash Experimental
- **Provider:** Google Generative AI

## How It Works

1. **File Ingestion:**
   - PDFs are chunked into 500-word segments
   - Images are processed with OCR
   - Text files are stored as-is
   - All content is embedded and stored in Qdrant

2. **Chat Memory:**
   - Every user message is stored
   - Every bot response is stored
   - No message limit

3. **Retrieval:**
   - User query is embedded
   - Top 50 similar memories are retrieved
   - Filtered by similarity threshold (0.65)
   - Grouped by type (PDF, text, image, chat)

4. **Response Generation:**
   - Context is built from relevant memories
   - Prompt includes filenames and sources
   - Gemini generates contextual response
   - Response is stored as new memory

## Troubleshooting

### Issue: "Module not found"
**Solution:** Install dependencies: `pip install -r requirements.txt`

### Issue: OCR not working
**Solution:** Install Tesseract OCR and add to PATH

### Issue: "Connection refused to Qdrant"
**Solution:** Check your Qdrant URL and API key in `.env`

### Issue: "Invalid Gemini API key"
**Solution:** Verify your Gemini API key is correct

## File Structure

```
backend/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (API keys)
└── README.md          # This file
```

## Notes

- The backend automatically creates the Qdrant collection on first run
- Files are processed from `winXP/public/downloads` directory
- All embeddings use 384-dimensional vectors
- Chat context is limited to most relevant memories only
- File updates automatically refresh memories in Qdrant
