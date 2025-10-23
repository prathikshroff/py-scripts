import requests, base64, csv, json

# ---- CONFIG ----
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"
INSTANCE_URL = "YOUR_INSTANCE_URL"
API_VERSION = "64.0"
CSV_FILE = "files.csv"
RESULT_CSV = "upload_results.csv"

# ----------------

def upload_to_salesforce(file_name, file_bytes, title):
    url = f"{INSTANCE_URL}/services/data/v{API_VERSION}/sobjects/ContentVersion"
    payload = {
        "Title": title,
        "PathOnClient": file_name,
        "VersionData": base64.b64encode(file_bytes).decode("utf-8")        
    }
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response

with open(CSV_FILE, newline='') as f, open(RESULT_CSV, 'w', newline='') as out_f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames + ['Status', 'Message', 'ContentVersionId']
    writer = csv.DictWriter(out_f, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        try:
            print(f"Processing {row['Title']}...")
            s3_url = row['S3_URL']
            file_name = row['PathOnClient'] or row['Title']

            s3_res = requests.get(s3_url)
            if s3_res.status_code != 200:
                raise Exception(f"S3 download failed: {s3_res.status_code}")

            res = upload_to_salesforce(file_name, s3_res.content, row['Title'])
            if res.status_code == 201:
                res_json = res.json()
                row['Status'] = 'Success'
                row['Message'] = 'Uploaded successfully'
                row['ContentVersionId'] = res_json.get('id')
            else:
                row['Status'] = 'Failed'
                row['Message'] = res.text
                row['ContentVersionId'] = ''
        except Exception as e:
            row['Status'] = 'Failed'
            row['Message'] = str(e)
            row['ContentVersionId'] = ''
        writer.writerow(row)
