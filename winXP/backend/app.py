#!/usr/bin/env python3
"""
Flask-based AI Second Brain backend with Qdrant and Gemini integration
"""

from flask import Flask, jsonify, send_file, abort, request
from flask_cors import CORS
import os
import mimetypes
from datetime import datetime
import uuid
from dotenv import load_dotenv
import json
from supabase import create_client, Client

# AI and Vector DB imports
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

# File processing imports
import PyPDF2
import pytesseract
from PIL import Image

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure CORS based on environment
if os.getenv('FLASK_ENV') == 'production':
    # In production, specify your frontend URL
    frontend_url = os.getenv('FRONTEND_URL', 'https://your-frontend.vercel.app')
    CORS(app, resources={r"/api/*": {"origins": [frontend_url]}})
else:
    # In development, allow all origins
    CORS(app)

# ============================================================================
# CONFIGURATION
# ============================================================================

QDRANT_URL = os.getenv('QDRANT_URL')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'memories')
VECTOR_SIZE = int(os.getenv('VECTOR_SIZE', 384))

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://ahhkjfisxgtjcufqxkff.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFoaGtqZmlzeGd0amN1ZnF4a2ZmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ1MTU0OTAsImV4cCI6MjA4MDA5MTQ5MH0.Gc56hU7BEvWFHw5K13C9K9dO0WY1vedOSD51ef8Tsto')

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.0-flash')

# Initialize Qdrant client
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Supabase Storage bucket name
STORAGE_BUCKET = 'knowledge-base'

# Initialize embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Chunk size for processing large documents
CHUNK_SIZE = 500
SIMILARITY_THRESHOLD = 0.5  # Lowered threshold for better recall

def get_downloads_path():
    """Get the path to the downloads folder"""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'public', 'downloads')

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_database():
    """Check Supabase connection"""
    try:
        # Test connection by checking if tables exist
        result = supabase.table('chat_sessions').select('session_id').limit(1).execute()
        print("✓ Supabase database connected successfully")
        return True
    except Exception as e:
        print(f"⚠️  Supabase connection warning: {e}")
        print("Please ensure you've created the tables using supabase_schema.sql")
        return False

# Icon URLs from various sources
ICON_URLS = {
    'text': 'https://cdn-icons-png.flaticon.com/512/136/136538.png',
    'pdf': 'https://cdn-icons-png.flaticon.com/512/136/136522.png',
    'image': 'https://cdn-icons-png.flaticon.com/512/136/136524.png',
    'video': 'https://cdn-icons-png.flaticon.com/512/136/136528.png',
    'audio': 'https://cdn-icons-png.flaticon.com/512/136/136532.png',
    'document': 'https://cdn-icons-png.flaticon.com/512/136/136539.png',
    'spreadsheet': 'https://cdn-icons-png.flaticon.com/512/136/136544.png',
    'archive': 'https://cdn-icons-png.flaticon.com/512/136/136547.png',
    'code': 'https://cdn-icons-png.flaticon.com/512/136/136525.png',
    'unknown': 'https://cdn-icons-png.flaticon.com/512/136/136549.png'
}

# ============================================================================
# QDRANT INITIALIZATION
# ============================================================================

def initialize_qdrant():
    """Initialize Qdrant collection if it doesn't exist"""
    try:
        from qdrant_client.models import PayloadSchemaType
        
        collections = qdrant_client.get_collections().collections
        collection_exists = any(col.name == COLLECTION_NAME for col in collections)
        
        if not collection_exists:
            qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )
            print(f"✓ Created Qdrant collection: {COLLECTION_NAME}")
        else:
            print(f"✓ Qdrant collection already exists: {COLLECTION_NAME}")
        
        # Create payload index for filename field to enable filtering
        try:
            qdrant_client.create_payload_index(
                collection_name=COLLECTION_NAME,
                field_name="filename",
                field_schema=PayloadSchemaType.KEYWORD
            )
            print(f"✓ Created payload index for 'filename' field")
        except Exception as index_error:
            # Index might already exist
            if "already exists" not in str(index_error).lower():
                print(f"Note: Could not create filename index: {index_error}")
            
    except Exception as e:
        print(f"Error initializing Qdrant: {e}")

# ============================================================================
# EMBEDDING FUNCTIONS
# ============================================================================

def embed_text(text):
    """Generate embedding for text using SentenceTransformers"""
    try:
        embedding = embedding_model.encode(text)
        return embedding.tolist()
    except Exception as e:
        print(f"Error embedding text: {e}")
        return None

# ============================================================================
# QDRANT OPERATIONS
# ============================================================================

def insert_memory(text, payload):
    """Insert a memory into Qdrant"""
    try:
        embedding = embed_text(text)
        if embedding is None:
            return False
            
        point_id = str(uuid.uuid4())
        payload['updated_at'] = datetime.now().isoformat()
        
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )
            ]
        )
        return True
    except Exception as e:
        print(f"Error inserting memory: {e}")
        return False

def delete_memory_for_file(filename):
    """Delete all memories associated with a specific file"""
    try:
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        # Search for all points with this filename using proper filter
        search_result = qdrant_client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="filename",
                        match=MatchValue(value=filename)
                    )
                ]
            ),
            limit=1000
        )
        
        point_ids = [point.id for point in search_result[0]]
        
        if point_ids:
            qdrant_client.delete(
                collection_name=COLLECTION_NAME,
                points_selector=point_ids
            )
            print(f"✓ Deleted {len(point_ids)} memories for file: {filename}")
        
        return True
    except Exception as e:
        print(f"Error deleting memory for file: {e}")
        return False

def search_only_chat_exchange(query, limit=20):
    """Search ONLY chat_exchange memories (for recall queries)"""
    try:
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        # Embed the query
        query_vector = embed_text(query)
        if query_vector is None:
            return []
        
        # Search with filter for chat_exchange only
        search_results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=limit,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="type",
                        match=MatchValue(value="chat_exchange")
                    )
                ]
            )
        )
        
        chat_memories = []
        for result in search_results:
            if result.score >= 0.3:  # Lower threshold for recall queries
                chat_memories.append({
                    'type': 'chat_exchange',
                    'problem': result.payload.get('problem', ''),
                    'answer': result.payload.get('answer', ''),
                    'full_text': result.payload.get('full_text', ''),
                    'session_id': result.payload.get('session_id', 'unknown'),
                    'score': result.score
                })
                print(f"  🔍 Exchange | Score: {result.score:.3f} | Problem: {result.payload.get('problem', '')[:50]}...")
        
        return chat_memories
    except Exception as e:
        print(f"Error searching chat exchanges: {e}")
        return []

def search_relevant_memories(query, limit=50):
    """Two-phase retrieval: Try chat exchanges first for recall queries, then general search"""
    try:
        # Detect if this is a recall query (asking about previous conversations)
        recall_keywords = ['previous', 'last', 'earlier', 'math', 'problem', 'question', 'asked', 'gave', 'told', 'said']
        query_lower = query.lower()
        is_recall_query = any(keyword in query_lower for keyword in recall_keywords)
        
        print(f"\n🔍 Query type: {'RECALL' if is_recall_query else 'GENERAL'}")
        
        # PHASE 1: If recall query, try chat exchanges FIRST
        if is_recall_query:
            print("📊 Phase 1: Searching chat exchanges only...")
            exchange_results = search_only_chat_exchange(query, limit)
            if len(exchange_results) > 0:
                print(f"✅ Found {len(exchange_results)} chat exchanges, returning them")
                return exchange_results
            else:
                print("⚠️  No chat exchanges found, falling back to general search...")
        
        # PHASE 2: General search (files + chats)
        print("📊 Phase 2: General search across all memories...")
        
        query_embedding = embed_text(query)
        if query_embedding is None:
            return []
        
        search_results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=limit
        )
        
        # Separate file memories from chat memories with different thresholds
        file_memories = []
        chat_memories = []
        
        for result in search_results:
            mem_type = result.payload.get('type', 'unknown')
            print(f"  📄 {mem_type:8s} | Score: {result.score:.3f} | {result.payload.get('filename', 'N/A')[:30]}")
            
            memory_obj = {
                'text': result.payload.get('text', ''),
                'type': mem_type,
                'filename': result.payload.get('filename', ''),
                'source': result.payload.get('source', ''),
                'score': result.score
            }
            
            # For files - slightly higher threshold for better relevance
            if mem_type in ['pdf', 'text', 'image']:
                if result.score >= 0.25:  # Tightened from 0.15
                    file_memories.append(memory_obj)
            # For chat exchanges - extract problem/answer pairs
            elif mem_type == 'chat_exchange':
                if result.score >= 0.35:  # Moderate threshold for exchanges
                    chat_memories.append({
                        'type': 'chat_exchange',
                        'problem': result.payload.get('problem', ''),
                        'answer': result.payload.get('answer', ''),
                        'full_text': result.payload.get('full_text', ''),
                        'session_id': result.payload.get('session_id', 'unknown'),
                        'score': result.score
                    })
            # For individual chat messages (legacy)
            elif mem_type == 'chat':
                if result.score >= 0.4:  # Higher threshold for individual messages
                    chat_memories.append(memory_obj)
        
        # Prioritize file memories, then add relevant chat
        relevant_memories = file_memories + chat_memories[:5]  # Limit chat to top 5
        
        return relevant_memories
    except Exception as e:
        print(f"Error searching memories: {e}")
        return []

# ============================================================================
# FILE PROCESSING FUNCTIONS
# ============================================================================

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_image(file_path):
    """Extract text from image using OCR"""
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except pytesseract.TesseractNotFoundError:
        print(f"⚠️  Tesseract OCR not installed - skipping text extraction from image")
        return ""
    except Exception as e:
        print(f"⚠️  Error extracting text from image: {e}")
        return ""

def chunk_text(text, chunk_size=CHUNK_SIZE):
    """Break text into fixed-size chunks"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        current_chunk.append(word)
        current_size += len(word) + 1
        
        if current_size >= chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_size = 0
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def process_pdf_file(filename):
    """Process and vectorize PDF file"""
    try:
        file_path = os.path.join(get_downloads_path(), filename)
        
        # Delete old memories for this file
        delete_memory_for_file(filename)
        
        # Extract text
        text = extract_text_from_pdf(file_path)
        if not text:
            return {'success': False, 'error': 'No text extracted from PDF'}
        
        # Chunk text
        chunks = chunk_text(text)
        
        # Insert each chunk
        for idx, chunk in enumerate(chunks):
            payload = {
                'type': 'pdf',
                'filename': filename,
                'chunk_index': idx,
                'text': chunk,
                'source': 'file'
            }
            insert_memory(chunk, payload)
        
        return {'success': True, 'chunks': len(chunks)}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def process_image_file(filename):
    """Process and vectorize image file using OCR"""
    try:
        file_path = os.path.join(get_downloads_path(), filename)
        
        # Delete old memories for this file
        delete_memory_for_file(filename)
        
        # Extract text using OCR
        text = extract_text_from_image(file_path)
        
        if text:
            payload = {
                'type': 'image',
                'filename': filename,
                'text': text,
                'source': 'file'
            }
            insert_memory(text, payload)
            return {'success': True, 'text_extracted': True}
        else:
            # Store metadata even if no text extracted
            payload = {
                'type': 'image',
                'filename': filename,
                'text': f"Image file: {filename}",
                'source': 'file'
            }
            insert_memory(f"Image file: {filename}", payload)
            return {'success': True, 'text_extracted': False}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def process_text_file(filename, content):
    """Process and vectorize text file"""
    try:
        # Delete old memories for this file
        delete_memory_for_file(filename)
        
        # Insert new memory
        payload = {
            'type': 'text',
            'filename': filename,
            'text': content,
            'source': 'file'
        }
        insert_memory(content, payload)
        
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# ============================================================================
# CHAT MEMORY FUNCTIONS
# ============================================================================

def store_chat_exchange(user_message, bot_response, session_id=None):
    """Store a Q&A exchange pair in Qdrant for better context retrieval"""
    try:
        # Create a combined exchange text for embedding
        combined_exchange = f"Problem: {user_message}\nAnswer: {bot_response}"
        
        payload = {
            'type': 'chat_exchange',
            'scope': 'archived',
            'session_id': session_id if session_id else 'unknown',
            'problem': user_message,
            'answer': bot_response,
            'full_text': combined_exchange,
            'source': 'chat',
            'timestamp': datetime.now().isoformat()
        }
        return insert_memory(combined_exchange, payload)
    except Exception as e:
        print(f"Error storing chat exchange: {e}")
        return False

def store_chat_message(sender, text, session_id=None):
    """Store individual chat message in Qdrant (legacy support)"""
    try:
        payload = {
            'type': 'chat',
            'scope': 'archived',
            'session_id': session_id if session_id else 'unknown',
            'sender': sender,
            'text': text,
            'source': 'chat',
            'timestamp': datetime.now().isoformat()
        }
        return insert_memory(text, payload)
    except Exception as e:
        print(f"Error storing chat message: {e}")
        return False

def build_context_from_memories(memories):
    """Build structured context from retrieved memories"""
    context_parts = []

    # Group memories by type
    pdf_memories = [m for m in memories if m['type'] == 'pdf']
    text_memories = [m for m in memories if m['type'] == 'text']
    image_memories = [m for m in memories if m['type'] == 'image']
    chat_exchange_memories = [m for m in memories if m['type'] == 'chat_exchange']
    individual_chat_memories = [m for m in memories if m['type'] == 'chat']

    # Add PDF context
    if pdf_memories:
        context_parts.append("=== Knowledge from PDF documents ===")
        for mem in pdf_memories[:5]:
            context_parts.append(f"[FILE: {mem['filename']}] {mem['text'][:300]}...")

    # Add text file context
    if text_memories:
        context_parts.append("\n=== Knowledge from text files (.txt, notes) ===")
        for mem in text_memories[:5]:
            context_parts.append(f"[FILE: {mem['filename']}] {mem['text'][:300]}...")

    # Add image context
    if image_memories:
        context_parts.append("\n=== Knowledge extracted from images (OCR) ===")
        for mem in image_memories[:3]:
            context_parts.append(f"[IMAGE: {mem['filename']}] {mem['text'][:200]}...")

    # Add archived conversations (from Qdrant, cross-session)
    if chat_exchange_memories or individual_chat_memories:
        # Show chat exchanges as archived solved problems
        if chat_exchange_memories:
            context_parts.append("\n=== Archived Solved Problems ===")
            for mem in chat_exchange_memories[:4]:
                session_id = mem.get('session_id', 'unknown')
                full_text = mem.get('full_text', '')
                if full_text:
                    context_parts.append(f"\n[Session {session_id}]")
                    context_parts.append(full_text)

        # If no exchanges, fall back to individual messages
        if not chat_exchange_memories and individual_chat_memories:
            context_parts.append("\n=== Archived Past Conversations ===")
            for mem in individual_chat_memories[:3]:
                session_id = mem.get('session_id', 'unknown')
                sender = mem.get('sender', 'unknown')
                context_parts.append(f"[Session {session_id}] {sender}: {mem.get('text', '')}")

    return "\n".join(context_parts)

def get_chat_history(session_id, limit=20):
    """Get chat history for a session"""
    try:
        response = supabase.table('messages') \
            .select('sender, message, timestamp') \
            .eq('session_id', session_id) \
            .order('timestamp', desc=False) \
            .limit(limit) \
            .execute()
        
        return [{'sender': m['sender'], 'message': m['message'], 'timestamp': m['timestamp']} 
                for m in response.data]
    except Exception as e:
        print(f"Error getting chat history: {e}")
        return []

def save_message_to_session(session_id, sender, message):
    """Save a message to a chat session"""
    try:
        # Update session updated_at
        supabase.table('chat_sessions') \
            .update({'updated_at': datetime.now().isoformat()}) \
            .eq('session_id', session_id) \
            .execute()
        
        # Insert message
        supabase.table('messages') \
            .insert({
                'session_id': session_id,
                'sender': sender,
                'message': message
            }) \
            .execute()
        
        return True
    except Exception as e:
        print(f"Error saving message: {e}")
        return False

def generate_chat_response(user_message, session_id):
    """Generate chat response using Gemini with conversation context and RAG"""
    try:
        # 1) Save current user message to session (SQLite)
        save_message_to_session(session_id, 'user', user_message)

        # 2) Get current session history (only this chat window)
        chat_history = get_chat_history(session_id, limit=12)

        # 3) Also store in Qdrant as long-term memory (cross-session)
        store_chat_message('user', user_message, session_id)

        # 4) Retrieve relevant memories from ALL knowledge (files + past chats)
        relevant_memories = search_relevant_memories(user_message)

        # Debug output
        print(f"\n🔍 Query: {user_message}")
        print(f"📊 Found {len(relevant_memories)} relevant memories")
        if relevant_memories:
            print("📝 Memory types:", {m['type'] for m in relevant_memories})

        # Build knowledge base context (files + archived chats)
        kb_context = build_context_from_memories(relevant_memories)

        # Build current conversation history string (only this session)
        conversation_history = ""
        if len(chat_history) > 1:
            conversation_history_lines = []
            for msg in chat_history[:-1]:  # exclude current user message
                sender = "User" if msg['sender'] == 'user' else "Clippy"
                conversation_history_lines.append(f"{sender}: {msg['message']}")
            conversation_history = "\n".join(conversation_history_lines)

        # Construct a very clear, structured prompt
        prompt_parts = []

        # System / role
        prompt_parts.append(
            "You are Clippy, a helpful Windows XP office assistant with a long-term memory.\n"
            "You are talking to the user in a single current chat session, but you also have access "
            "to a separate memory bank built from files (PDFs, text files, images) and archived past chats."
        )

        # Current session context
        if conversation_history:
            prompt_parts.append("\n\n[CURRENT SESSION CONVERSATION]\n")
            prompt_parts.append(conversation_history)

        # Knowledge base context
        if kb_context:
            prompt_parts.append("\n\n[MEMORY BANK: FILES AND ARCHIVED PAST CHATS]\n")
            prompt_parts.append(
                "The following information does NOT come from the current chat, "
                "but from stored documents and older conversations. Use it only if it clearly helps answer the user's question.\n"
            )
            prompt_parts.append(kb_context)

        # Current user message
        prompt_parts.append("\n\n[CURRENT USER MESSAGE]\n")
        prompt_parts.append(user_message)

        # Instructions to control style and confusion
        prompt_parts.append(
            "\n\n[INSTRUCTIONS]\n"
            "1. Your first priority is to answer the CURRENT USER MESSAGE directly, fully, and with your own domain knowledge.\n"
            "2. If the MEMORY BANK contains documents (PDF, text files, or OCR text) that are clearly related to the user's question, list ONLY the filenames of those relevant files at the end of your answer in a short \"Related Files\" section. Do NOT quote or summarize irrelevant files.\n"
            "3. If the user is asking about something that exists in a file, you may include information from that file in your explanation, but do not rely solely on the file if your own general knowledge can answer the question better.\n"
            "4. Do NOT mention file types, supported formats, APIs, commands, or any technical metadata unless the user explicitly asks for it.\n"
            "5. Do NOT mention or reference past chat sessions unless the user explicitly asks about previous chats or past questions. When the question is NOT about past chats, ignore archived conversations entirely.\n"
            "6. Use only the MEMORY BANK entries that are semantically related to the question. Ignore unrelated items.\n"
            "7. Present the answer in a clean, educational style. Avoid self-referential phrases like \"Based on my memory\", \"You asked earlier\", or \"In a previous conversation\" unless directly asked.\n"
            "8. If a file is relevant, include it at the end in this format:\n\n"
            "[Related Files]\n"
            "- machine_learning.pdf\n\n"
            "and nothing more.\n"
            "9. Do not say you \"don't have access to\" something. You always have access to your MEMORY BANK and your inherent knowledge.\n"
            "10. Never fabricate files. Only list files that exist in the provided MEMORY BANK.\n"
        )

        full_prompt = "".join(prompt_parts)

        # Call Gemini
        response = gemini_model.generate_content(full_prompt)
        bot_response = response.text

        # Save bot response to session + Qdrant
        save_message_to_session(session_id, 'bot', bot_response)
        store_chat_exchange(user_message, bot_response, session_id)

        return bot_response

    except Exception as e:
        print(f"Error generating chat response: {e}")
        return "I'm having trouble processing that request right now. Please try again."

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_file_type(filename):
    """Determine file type based on extension"""
    ext = os.path.splitext(filename)[1].lower()
    
    if ext in ['.txt', '.md', '.log', '.readme']:
        return 'text'
    elif ext in ['.pdf']:
        return 'pdf'
    elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']:
        return 'image'
    elif ext in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']:
        return 'video'
    elif ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg']:
        return 'audio'
    elif ext in ['.doc', '.docx', '.rtf']:
        return 'document'
    elif ext in ['.xls', '.xlsx', '.csv']:
        return 'spreadsheet'
    elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
        return 'archive'
    elif ext in ['.js', '.py', '.html', '.css', '.json', '.xml']:
        return 'code'
    else:
        return 'unknown'

def get_icon_url(file_type):
    """Get icon URL for file type"""
    return ICON_URLS.get(file_type, ICON_URLS['unknown'])

# ============================================================================
# FLASK ENDPOINTS
# ============================================================================

@app.route('/api/files', methods=['GET'])
def list_files():
    """List all files from Supabase Storage"""
    try:
        # Get files from Supabase Storage
        try:
            storage_files = supabase.storage.from_(STORAGE_BUCKET).list('files')
            
            files = []
            for file_obj in storage_files:
                filename = file_obj['name']
                file_type = get_file_type(filename)
                storage_path = f"files/{filename}"
                
                # Get public URL
                public_url = supabase.storage.from_(STORAGE_BUCKET).get_public_url(storage_path)
                
                file_info = {
                    'name': filename,
                    'path': public_url,
                    'url': public_url,
                    'size': file_obj.get('metadata', {}).get('size', 0),
                    'type': file_type,
                    'mime': file_obj.get('metadata', {}).get('mimetype', 'application/octet-stream'),
                    'icon': get_icon_url(file_type),
                    'updated_at': file_obj.get('updated_at', ''),
                    'storage_path': storage_path
                }
                files.append(file_info)
            
            return jsonify(files)
            
        except Exception as storage_error:
            # Fallback to local files if Supabase storage fails
            print(f"Supabase storage error: {storage_error}")
            downloads_path = get_downloads_path()
            
            if not os.path.exists(downloads_path):
                return jsonify([])
            
            files = []
            for filename in os.listdir(downloads_path):
                file_path = os.path.join(downloads_path, filename)
                if os.path.isfile(file_path):
                    file_type = get_file_type(filename)
                    file_info = {
                        'name': filename,
                        'path': f'/api/download/{filename}',
                        'url': f'/api/download/{filename}',
                        'size': os.path.getsize(file_path),
                        'type': file_type,
                        'mime': mimetypes.guess_type(filename)[0] or 'application/octet-stream',
                        'icon': get_icon_url(file_type)
                    }
                    files.append(file_info)
            
            return jsonify(files)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload a file to Supabase Storage and automatically process it into Qdrant"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Read file content
        file_content = file.read()
        
        # Upload to Supabase Storage
        try:
            storage_path = f"files/{file.filename}"
            supabase.storage.from_(STORAGE_BUCKET).upload(
                storage_path,
                file_content,
                file_options={"content-type": file.content_type or "application/octet-stream"}
            )
            
            # Get public URL
            public_url = supabase.storage.from_(STORAGE_BUCKET).get_public_url(storage_path)
            
        except Exception as upload_error:
            # If file exists, update it
            if 'duplicate' in str(upload_error).lower() or 'exists' in str(upload_error).lower():
                supabase.storage.from_(STORAGE_BUCKET).update(
                    storage_path,
                    file_content,
                    file_options={"content-type": file.content_type or "application/octet-stream"}
                )
                public_url = supabase.storage.from_(STORAGE_BUCKET).get_public_url(storage_path)
            else:
                raise upload_error
        
        # Save temporarily for processing
        downloads_path = get_downloads_path()
        os.makedirs(downloads_path, exist_ok=True)
        temp_file_path = os.path.join(downloads_path, file.filename)
        
        with open(temp_file_path, 'wb') as f:
            f.write(file_content)
        
        # Automatically process the file based on type
        file_type = get_file_type(file.filename)
        result = {
            'success': True,
            'filename': file.filename,
            'type': file_type,
            'url': public_url,
            'storage_path': storage_path
        }
        
        if file_type == 'pdf':
            process_result = process_pdf_file(file.filename)
            result['processed'] = process_result.get('success', False)
        elif file_type == 'image':
            process_result = process_image_file(file.filename)
            result['processed'] = process_result.get('success', False)
        elif file_type == 'text':
            with open(temp_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            process_result = process_text_file(file.filename, content)
            result['processed'] = process_result.get('success', False)
        else:
            result['processed'] = False
            result['message'] = 'File uploaded but not processed (unsupported type)'
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/save/<filename>', methods=['POST'])
def save_file(filename):
    """Save content to a specific file in Supabase Storage and update memory"""
    try:
        # Get content from request
        content = request.get_data(as_text=True)
        content_bytes = content.encode('utf-8')
        
        # Upload to Supabase Storage
        try:
            storage_path = f"files/{filename}"
            
            # Try update first (if file exists)
            try:
                supabase.storage.from_(STORAGE_BUCKET).update(
                    storage_path,
                    content_bytes,
                    file_options={"content-type": "text/plain"}
                )
            except:
                # If update fails, try upload (new file)
                supabase.storage.from_(STORAGE_BUCKET).upload(
                    storage_path,
                    content_bytes,
                    file_options={"content-type": "text/plain"}
                )
            
            public_url = supabase.storage.from_(STORAGE_BUCKET).get_public_url(storage_path)
            
        except Exception as storage_error:
            # Fallback to local storage
            print(f"Supabase storage save error: {storage_error}")
            downloads_path = get_downloads_path()
            file_path = os.path.join(downloads_path, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            public_url = f"/api/download/{filename}"
        
        # Update memory if it's a text file
        if get_file_type(filename) == 'text':
            process_text_file(filename, content)
        
        return jsonify({
            'success': True,
            'message': 'File saved successfully',
            'url': public_url
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    """Delete a file from Supabase Storage"""
    try:
        storage_path = f"files/{filename}"
        
        # Delete from Supabase Storage
        try:
            supabase.storage.from_(STORAGE_BUCKET).remove([storage_path])
            
            # Also delete locally if exists
            downloads_path = get_downloads_path()
            file_path = os.path.join(downloads_path, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return jsonify({
                'success': True,
                'message': 'File deleted successfully'
            })
            
        except Exception as storage_error:
            # Fallback to local deletion
            print(f"Supabase storage delete error: {storage_error}")
            downloads_path = get_downloads_path()
            file_path = os.path.join(downloads_path, filename)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                return jsonify({
                    'success': True,
                    'message': 'File deleted successfully (local)'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'File not found'
                }), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/process_pdf', methods=['POST'])
def process_pdf():
    """Process and vectorize a PDF file"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'success': False, 'error': 'Filename required'}), 400
        
        result = process_pdf_file(filename)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/process_image', methods=['POST'])
def process_image():
    """Process and vectorize an image file"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'success': False, 'error': 'Filename required'}), 400
        
        result = process_image_file(filename)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/process_all_files', methods=['POST'])
def process_all_files():
    """Process all files in the downloads directory"""
    try:
        downloads_path = get_downloads_path()
        results = {
            'pdf': [],
            'image': [],
            'text': []
        }
        
        for filename in os.listdir(downloads_path):
            file_path = os.path.join(downloads_path, filename)
            if not os.path.isfile(file_path):
                continue
                
            file_type = get_file_type(filename)
            
            if file_type == 'pdf':
                result = process_pdf_file(filename)
                results['pdf'].append({'filename': filename, 'result': result})
            elif file_type == 'image':
                result = process_image_file(filename)
                results['image'].append({'filename': filename, 'result': result})
            elif file_type == 'text':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                result = process_text_file(filename, content)
                results['text'].append({'filename': filename, 'result': result})
        
        return jsonify({'success': True, 'results': results})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests with conversation context and RAG"""
    try:
        data = request.get_json()
        user_message = data.get('message')
        session_id = data.get('session_id')
        
        if not user_message:
            return jsonify({'success': False, 'error': 'Message required'}), 400
        
        if not session_id:
            return jsonify({'success': False, 'error': 'Session ID required'}), 400
        
        # Generate response
        bot_response = generate_chat_response(user_message, session_id)
        
        return jsonify({
            'success': True,
            'response': bot_response
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sessions/new', methods=['POST'])
def create_session():
    """Create a new chat session"""
    try:
        session_id = str(uuid.uuid4())
        title = request.get_json().get('title', 'New Chat')
        
        supabase.table('chat_sessions') \
            .insert({
                'session_id': session_id,
                'title': title
            }) \
            .execute()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'title': title
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """Get all chat sessions"""
    try:
        response = supabase.table('chat_sessions') \
            .select('session_id, title, created_at, updated_at') \
            .order('updated_at', desc=True) \
            .execute()
        
        return jsonify({
            'success': True,
            'sessions': response.data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session_messages(session_id):
    """Get all messages for a session"""
    try:
        messages = get_chat_history(session_id, limit=100)
        
        return jsonify({
            'success': True,
            'messages': messages
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a chat session"""
    try:
        # Delete messages (will cascade delete if FK is set up)
        supabase.table('messages') \
            .delete() \
            .eq('session_id', session_id) \
            .execute()
        
        # Delete session
        supabase.table('chat_sessions') \
            .delete() \
            .eq('session_id', session_id) \
            .execute()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sync_all_chats_to_qdrant', methods=['POST'])
def sync_all_chats_to_qdrant():
    """Sync all existing chat messages from Supabase to Qdrant"""
    try:
        response = supabase.table('messages').select('sender, message').order('timestamp').execute()
        
        messages = response.data
        synced_count = 0
        for msg in messages:
            if store_chat_message(msg['sender'], msg['message']):
                synced_count += 1
        
        return jsonify({
            'success': True,
            'synced': synced_count,
            'total': len(messages)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/delete_memory/<filename>', methods=['DELETE'])
def delete_memory(filename):
    """Delete all memories associated with a file"""
    try:
        success = delete_memory_for_file(filename)
        return jsonify({'success': success})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/memory_stats', methods=['GET'])
def memory_stats():
    """Get statistics about stored memories"""
    try:
        # Count total memories
        result = qdrant_client.count(collection_name=COLLECTION_NAME)
        total_count = result.count
        
        # Sample some memories to show types
        scroll_result = qdrant_client.scroll(
            collection_name=COLLECTION_NAME,
            limit=100
        )
        
        type_counts = {}
        file_samples = []
        for point in scroll_result[0]:
            mem_type = point.payload.get('type', 'unknown')
            type_counts[mem_type] = type_counts.get(mem_type, 0) + 1
            
            # Collect sample file memories
            if mem_type in ['pdf', 'text', 'image'] and len(file_samples) < 10:
                file_samples.append({
                    'type': mem_type,
                    'filename': point.payload.get('filename', 'N/A'),
                    'text_preview': point.payload.get('text', '')[:100]
                })
        
        return jsonify({
            'success': True,
            'total_memories': total_count,
            'types': type_counts,
            'file_samples': file_samples
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Serve a specific file from Supabase Storage or local folder"""
    try:
        # Try to get file from Supabase Storage first
        try:
            storage_path = f"files/{filename}"
            
            # Download file from Supabase Storage
            file_data = supabase.storage.from_(STORAGE_BUCKET).download(storage_path)
            
            # Get MIME type
            mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            
            # Return file data
            from io import BytesIO
            return send_file(
                BytesIO(file_data),
                mimetype=mime_type,
                as_attachment=False,
                download_name=filename
            )
            
        except Exception as storage_error:
            # Fallback to local file if Supabase fails
            print(f"Supabase storage download error: {storage_error}")
            
            downloads_path = get_downloads_path()
            file_path = os.path.join(downloads_path, filename)
            
            if not os.path.exists(file_path):
                abort(404)
            
            # Get MIME type
            mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
            
            # Serve file with proper content type
            return send_file(file_path, mimetype=mime_type, as_attachment=False)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'file-server'})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("="*60)
    print("AI Second Brain Backend Starting...")
    print("="*60)
    
    # Initialize Database
    print("Initializing chat sessions database...")
    init_database()
    
    # Initialize Qdrant
    print("Initializing Qdrant collection...")
    initialize_qdrant()
    
    print("\nEndpoints:")
    print("  Session Management:")
    print("    POST /api/sessions/new - Create new chat session")
    print("    GET  /api/sessions - Get all sessions")
    print("    GET  /api/sessions/<id> - Get session messages")
    print("    DELETE /api/sessions/<id> - Delete session")
    print("  Chat:")
    print("    POST /api/chat - Chat with AI assistant")
    print("  Files:")
    print("    GET  /api/files - List all files")
    print("    POST /api/save/<filename> - Save file")
    print("    POST /api/process_all_files - Process all files")
    print("  Other:")
    print("    GET  /api/memory_stats - Knowledge base stats")
    print("    GET  /api/health - Health check")
    print("="*60)
    
    app.run(host='localhost', port=8001, debug=True)