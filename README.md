## File Upload, Download, and CSV Utilities

Simple, focused Python scripts to:

- Download files from pre-signed S3 URLs and save them with new names
- Upload files to Salesforce as ContentVersion records
- Generate de-duplicated filenames in a CSV by appending numeric suffixes

These scripts are designed to be small, readable, and easy to adapt.

---

## Requirements

- Python 3.9+
- Install dependencies:

```bash
pip3 install -r requirements.txt
```

Note: On macOS you may see a warning about LibreSSL from urllib3; it is safe to ignore. To hide it, install an older urllib3:

```bash
pip3 install 'urllib3<2.0'
```

---

## Scripts

### 1) download_script.py

Downloads files from pre-signed S3 URLs in a CSV and saves them locally using the `new_name` column.

- Input CSV: `download_files.csv`
- Required columns: `filename,s3_url,new_name`
- Output: Files saved to the configured folder

Key configuration (top of the file):

```python
CSV_FILE = "download_files.csv"
DOWNLOAD_FOLDER = "/absolute/path/to/your/folder"
```

Run:

```bash
python3 download_script.py
```

Import and use in your own code:

```python
from download_script import download_files_from_csv

download_files_from_csv()  # Uses the constants in the script
```

CSV example:

```csv
filename,s3_url,new_name
original.png,https://your-presigned-url,renamed.png
```

---

### 2) s3_to_sf_upload.py

Downloads files from `files.csv` and uploads them to Salesforce as `ContentVersion` records.

- Input CSV: `files.csv`
- Required columns: `Title,S3_URL,PathOnClient`
- Output CSV: `upload_results.csv` (adds `Status,Message,ContentVersionId`)

Configuration (top of the file):

```python
ACCESS_TOKEN = "<Salesforce OAuth access token>"
INSTANCE_URL = "https://your-instance.my.salesforce.com"
API_VERSION = "64.0"
CSV_FILE = "files.csv"
RESULT_CSV = "upload_results.csv"
```

Run:

```bash
python3 s3_to_sf_upload.py
```

Notes:
- Ensure the access token and instance URL are valid for your org/sandbox.

---

### 4) dedupe_audio_script.py

Adds a `renamed` column to a CSV by numbering the `new_name` column with `-1, -2, ...`. Unique names also get `-1` for consistency.

- Default Input CSV: `input.csv`
- Output CSV: `deduped_files.csv`
- Required column: `new_name`

Run:

```bash
python3 dedupe_audio_script.py
```

Example transformation:

- `xyz.mp4` → `xyz-1.mp4`, `xyz-2.mp4`, ...
- `xyz.mp4` (unique) → `xyz-1.mp4`

---

## Configuration Tips

For quick experiments, edit the constants at the top of each script. For team/shared environments, prefer injecting configuration (env vars, arguments, or constructor parameters) over hardcoding secrets or org-specific values.

Environment variable example:

```python
import os

ACCESS_TOKEN = os.getenv("SF_ACCESS_TOKEN", "")
INSTANCE_URL = os.getenv("SF_INSTANCE_URL", "")
API_VERSION = os.getenv("SF_API_VERSION", "64.0")
```

Then run with:

```bash
SF_ACCESS_TOKEN=... SF_INSTANCE_URL=... python3 s3_to_sf_upload.py
```

This approach keeps secrets out of source and aligns with best practices for configurable code.

---

## CSV Formats (at a glance)

- download_script.py: `filename,s3_url,new_name`
- s3_to_sf_upload.py: `Title,S3_URL,PathOnClient`
- dedupe_audio_script.py: must include `new_name`; output adds `renamed`

---

## Troubleshooting

- Missing module `requests`:

  ```bash
  pip3 install requests
  ```

- macOS LibreSSL warning from urllib3: ignore it or run `pip3 install 'urllib3<2.0'`.

- Large downloads: the downloader streams in 8 KB chunks and prints progress periodically; adjust chunk size if needed.

---

## Contributing / Adapting

These scripts are intentionally minimal. Feel free to copy, adapt, and extend. Keep functions small and configuration injectable so they’re easy to maintain and reuse.


