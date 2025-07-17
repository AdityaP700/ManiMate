# app/storage/gcs.py
from google.cloud import storage
from app.config import GCP_PROJECT_ID, GCS_BUCKET_NAME

def upload_to_gcs(file_path: str, bucket_name: str, destination_blob_name: str):
    """Uploads a file to GCS and returns the public URL."""
    storage_client = storage.Client(project=GCP_PROJECT_ID)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(file_path)
    blob.make_public()  # Ensure it's publicly accessible

    return blob.public_url
