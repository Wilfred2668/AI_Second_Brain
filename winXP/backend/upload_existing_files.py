import os
import requests
from pathlib import Path

# Get the downloads folder
downloads_path = Path('../public/downloads')
api_url = 'http://localhost:8001/api/upload'

print('Uploading files to Supabase Storage...\n')

files_to_upload = list(downloads_path.glob('*'))
total = len(files_to_upload)

for idx, file_path in enumerate(files_to_upload, 1):
    if file_path.is_file():
        print(f'[{idx}/{total}] Uploading: {file_path.name}')
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f)}
                response = requests.post(api_url, files=files)
                result = response.json()
                
                if result.get('success'):
                    status = 'Uploaded'
                    if result.get('processed'):
                        status += ' and processed to Qdrant'
                    print(f'  ✓ {status}')
                    print(f'  URL: {result.get("url", "N/A")}')
                else:
                    print(f'  ✗ Failed: {result.get("error", "Unknown error")}')
        except Exception as e:
            print(f'  ✗ Error: {str(e)}')
        print()

print('Upload complete!')
