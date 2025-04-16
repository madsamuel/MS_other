# pip install azure-storage-blob
# pip install python-dotenv

import os
from dotenv import load_dotenv
from azure.storage.blob import BlobClient

# Load .env file
load_dotenv()

# Storage account and container details
STORAGE_ACCOUNT_NAME = "ai1021121sa"
CONTAINER_NAME = "logs"
BLOB_NAME = "logfile.txt"

# Retrieve SAS Token from .env file
SAS_TOKEN = os.getenv("SAS_TOKEN")

if not SAS_TOKEN:
    raise ValueError("❌ Error: SAS Token is missing. Make sure it is set in the .env file.")

# Construct full Blob URL
BLOB_URL = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{CONTAINER_NAME}/{BLOB_NAME}?{SAS_TOKEN}"

# Create BlobClient
blob_client = BlobClient.from_blob_url(BLOB_URL)

# Log data to upload
log_data = "New security log entry: Suspicious login attempt detected.\n"

# Upload the log file
blob_client.upload_blob(log_data, overwrite=True)

print("✅ Logs successfully uploaded using SAS Token from .env file!")
