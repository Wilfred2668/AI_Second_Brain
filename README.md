# AI Second Brain - Windows XP Edition

A nostalgic Windows XP-themed AI knowledge management system that lets you chat with your documents using RAG (Retrieval Augmented Generation).

## Features

- **Windows XP UI** - Authentic retro interface with draggable windows, start menu, and classic design
- **AI Chat** - Query your knowledge base using Google Gemini 2.0 Flash
- **Document Processing** - Upload and process PDF, TXT, and image files (OCR)
- **Vector Search** - Powered by Qdrant for semantic document retrieval
- **Cloud Storage** - Supabase for document management and metadata

## Tech Stack

**Frontend:**
- React 16.8 with Windows XP UI components
- Deployed on Vercel

**Backend:**
- Flask API with CORS support
- Google Gemini AI for chat responses
- Qdrant Cloud for vector embeddings
- Supabase for PostgreSQL + Storage
- Sentence Transformers for embeddings
- PyPDF2 + Tesseract for document processing

## Quick Start

### Prerequisites

- Node.js 14+
- Python 3.12+
- Supabase account
- Qdrant Cloud account
- Google AI API key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Wilfred2668/AI_Second_Brain.git
cd AI_Second_Brain
```

2. **Backend Setup**
```bash
cd winXP/backend
pip install -r requirements.txt

# Create .env file with:
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
GEMINI_API_KEY=your_gemini_api_key
COLLECTION_NAME=knowledge_base
VECTOR_SIZE=384
FLASK_ENV=development
FRONTEND_URL=http://localhost:3000

# Run backend
python app.py
```

3. **Frontend Setup**
```bash
cd winXP
npm install

# Create .env file with:
REACT_APP_API_URL=http://localhost:5000

# Run frontend
npm start
```

4. **Access the app**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## Deployment

**Frontend (Vercel):**
- Connected to GitHub repository
- Auto-deploys on push to main
- Environment variable: `REACT_APP_API_URL`

**Backend (Render):**
- Web service with automatic deploys
- Uses `runtime.txt` for Python 3.12.3
- Add all environment variables from .env

## Screenshots

![Landing Page](landing%20page.png)
*Classic Windows XP desktop with authentic start menu and desktop icons*

![File Upload](upload.png)
*My Computer window for uploading documents (PDF, TXT, images)*

![Chat Sessions](chat_sessions.png)
*Google Chrome browser interface for AI-powered chat interactions*

![Multiple Tabs](tabs%20open.png)
*Multi-window experience with draggable, resizable windows*

![File Tags](tags_file.png)
*Document management with tagging and organization features*

## Usage

1. Click **My Computer** to upload documents (PDF, TXT, PNG, JPG)
2. Documents are processed and stored in your knowledge base
3. Use **Google Chrome** to chat with your AI assistant
4. Ask questions about your uploaded documents
5. Get AI-powered responses with context from your files


## Author

Built with ❤️ using React and Flask
