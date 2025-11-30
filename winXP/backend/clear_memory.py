"""
Clear Memory Script
This script clears all data from the AI Second Brain:
- Deletes all vectors from Qdrant collection
- Clears all chat sessions and messages from SQLite
- Optionally recreates the Qdrant collection
"""

import os
import sqlite3
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Load environment variables
load_dotenv()

QDRANT_URL = os.getenv('QDRANT_URL')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'memories')
VECTOR_SIZE = int(os.getenv('VECTOR_SIZE', 384))

def get_db_path():
    """Get the path to the SQLite database"""
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(backend_dir, 'chat_sessions.db')

def clear_qdrant_collection():
    """Clear all vectors from Qdrant collection"""
    try:
        print("\n🗑️  Connecting to Qdrant...")
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        
        # Check if collection exists
        collections = client.get_collections().collections
        collection_exists = any(col.name == COLLECTION_NAME for col in collections)
        
        if collection_exists:
            print(f"🗑️  Deleting collection '{COLLECTION_NAME}'...")
            client.delete_collection(collection_name=COLLECTION_NAME)
            print("✅ Qdrant collection deleted")
            
            # Recreate the collection
            print(f"🔄 Recreating collection '{COLLECTION_NAME}'...")
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
            )
            
            # Create payload index for filename field
            from qdrant_client.models import PayloadSchemaType
            client.create_payload_index(
                collection_name=COLLECTION_NAME,
                field_name="filename",
                field_schema=PayloadSchemaType.KEYWORD
            )
            print("✅ Qdrant collection recreated with payload index")
        else:
            print(f"ℹ️  Collection '{COLLECTION_NAME}' does not exist, creating new one...")
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
            )
            
            # Create payload index for filename field
            from qdrant_client.models import PayloadSchemaType
            client.create_payload_index(
                collection_name=COLLECTION_NAME,
                field_name="filename",
                field_schema=PayloadSchemaType.KEYWORD
            )
            print("✅ Qdrant collection created")
            
        return True
    except Exception as e:
        print(f"❌ Error clearing Qdrant: {e}")
        return False

def clear_sqlite_database():
    """Clear all data from SQLite database"""
    try:
        db_path = get_db_path()
        
        if not os.path.exists(db_path):
            print("ℹ️  SQLite database does not exist")
            return True
            
        print("\n🗑️  Clearing SQLite database...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Clear messages table
        cursor.execute('DELETE FROM messages')
        messages_deleted = cursor.rowcount
        
        # Clear chat_sessions table
        cursor.execute('DELETE FROM chat_sessions')
        sessions_deleted = cursor.rowcount
        
        # Reset auto-increment counters
        cursor.execute('DELETE FROM sqlite_sequence WHERE name="messages"')
        cursor.execute('DELETE FROM sqlite_sequence WHERE name="chat_sessions"')
        
        conn.commit()
        conn.close()
        
        print(f"✅ Deleted {sessions_deleted} chat sessions and {messages_deleted} messages")
        return True
    except Exception as e:
        print(f"❌ Error clearing SQLite: {e}")
        return False

def main():
    print("=" * 60)
    print("🧹 AI Second Brain - Clear All Memory")
    print("=" * 60)
    print("\n⚠️  WARNING: This will delete ALL data:")
    print("  - All vectors in Qdrant (files + chat history)")
    print("  - All chat sessions in SQLite")
    print("  - All messages in SQLite")
    print()
    
    confirm = input("Are you sure you want to continue? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("\n❌ Operation cancelled")
        return
    
    print("\n🚀 Starting cleanup...\n")
    
    # Clear Qdrant
    qdrant_success = clear_qdrant_collection()
    
    # Clear SQLite
    sqlite_success = clear_sqlite_database()
    
    print("\n" + "=" * 60)
    if qdrant_success and sqlite_success:
        print("✅ All memory cleared successfully!")
        print("ℹ️  You can now restart the backend and start fresh")
    else:
        print("⚠️  Some operations failed. Check the errors above.")
    print("=" * 60)

if __name__ == "__main__":
    main()
