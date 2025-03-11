# pip install azure-storage-blob

from azure.storage.blob import BlobClient

# Storage account and container details
STORAGE_ACCOUNT_NAME = "ai1021121sa"
CONTAINER_NAME = "logs"
BLOB_NAME = "logfile.txt"

# Your SAS token (without '?')
SAS_TOKEN = ""


# Construct full Blob URL
BLOB_URL = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{CONTAINER_NAME}/{BLOB_NAME}?{SAS_TOKEN}"

# Create BlobClient
blob_client = BlobClient.from_blob_url(BLOB_URL)

# Log data to upload
log_data = "New security log entry: Suspicious login attempt detected.\n"

# Upload the log file
blob_client.upload_blob(log_data, overwrite=True)

print("✅ Logs successfully uploaded using SAS Token!")
