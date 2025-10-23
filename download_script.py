import csv
import requests
import os
from pathlib import Path
import time

# Configuration
CSV_FILE = "download_files.csv"
DOWNLOAD_FOLDER = "/Users/prathikshroff/Desktop/Renamed"  # Change this to your desired folder

def create_download_folder(folder_path):
    """Create download folder if it doesn't exist"""
    Path(folder_path).mkdir(parents=True, exist_ok=True)
    print(f"📁 Download folder: {os.path.abspath(folder_path)}")

def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def download_file(url, local_path, original_name):
    """Download file from URL and save to local path"""
    try:
        print(f"⬇️  Downloading: {original_name}")
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Get file size for progress tracking
        total_size = int(response.headers.get('content-length', 0))
        
        with open(local_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # Show progress for large files
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        if downloaded % (1024 * 1024) == 0:  # Update every MB
                            print(f"   Progress: {progress:.1f}%", end='\r')
        
        print(f"✅ Downloaded: {os.path.basename(local_path)}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to download {original_name}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error saving {original_name}: {e}")
        return False

def download_files_from_csv():
    """Main function to download all files from CSV"""
    
    # Create download folder
    create_download_folder(DOWNLOAD_FOLDER)
    
    # Statistics
    total_files = 0
    successful_downloads = 0
    failed_downloads = 0
    
    try:
        with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, 1):
                total_files += 1
                
                # Get values from CSV
                original_name = row.get('filename', '').strip()
                s3_url = row.get('s3_url', '').strip()
                new_name = row.get('new_name', '').strip()
                
                # Skip if required fields are empty
                if not s3_url or not new_name:
                    print(f"⚠️  Row {row_num}: Missing URL or new name, skipping")
                    failed_downloads += 1
                    continue
                
                # Use original name if new name is empty
                if not new_name:
                    new_name = original_name
                
                # Sanitize filename
                safe_filename = sanitize_filename(new_name)
                local_path = os.path.join(DOWNLOAD_FOLDER, safe_filename)
                
                # Check if file already exists
                if os.path.exists(local_path):
                    print(f"⚠️  File already exists: {safe_filename}, skipping")
                    continue
                
                # Download the file
                if download_file(s3_url, local_path, original_name):
                    successful_downloads += 1
                else:
                    failed_downloads += 1
                
                # Small delay to be nice to the server
                time.sleep(0.1)
    
    except FileNotFoundError:
        print(f"❌ CSV file '{CSV_FILE}' not found!")
        return
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return
    
    # Print summary
    print(f"\n📊 Download Summary:")
    print(f"   Total files: {total_files}")
    print(f"   ✅ Successful: {successful_downloads}")
    print(f"   ❌ Failed: {failed_downloads}")
    print(f"   📁 Files saved to: {os.path.abspath(DOWNLOAD_FOLDER)}")

if __name__ == "__main__":
    print("🚀 Starting file download process...")
    download_files_from_csv()
    print("🏁 Download process completed!")