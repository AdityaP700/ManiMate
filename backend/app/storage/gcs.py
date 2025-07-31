# app/storage/gcs.py
from google.cloud import storage
from app.config import GCP_PROJECT_ID, GCS_BUCKET_NAME

def upload_to_gcs(file_path: str, bucket_name: str, destination_blob_name: str):
    """
    Uploads a file to GCS. It automatically finds credentials from the
    GOOGLE_APPLICATION_CREDENTIALS environment variable.
    """
    # The client will automatically find and use the credentials file
    # specified in your .env file. No manual path needed!
    storage_client = storage.Client(project=GCP_PROJECT_ID)
    
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Upload the file and make it public
    blob.upload_from_filename(file_path)
 

    return blob.public_url