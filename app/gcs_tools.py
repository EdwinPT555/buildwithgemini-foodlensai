# Copyright 2026 Google LLC
# Cloud Storage tools for FoodlensAI image uploads

import os
import uuid
import subprocess
from google.cloud import storage
from google.oauth2 import credentials

BUCKET_NAME = "foodlensai-media-7526c4c4"
PROJECT_ID = "qwiklabs-gcp-01-7526c4c469dc"


def get_gcs_client() -> storage.Client:
    """Helper to initialize GCS client with hardcoded project ID."""
    try:
        token = subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True, stderr=subprocess.DEVNULL).strip()
        creds = credentials.Credentials(token)
        return storage.Client(project=PROJECT_ID, credentials=creds)
    except Exception:
        return storage.Client(project=PROJECT_ID)


def upload_product_image(
    file_path: str,
    barcode: str = "unknown",
    category: str = "barcodes"
) -> str:
    """Uploads a food product or barcode image to the public Cloud Storage bucket.

    Args:
        file_path: Absolute local file path of the image to upload (e.g., '/tmp/barcode123.jpg').
        barcode: Associated barcode number or identifier.
        category: Image category, either 'barcodes' or 'products'.

    Returns:
        Public HTTP URL of the uploaded image accessible for web page embedding.
    """
    if not os.path.exists(file_path):
        return f"Error: Local file '{file_path}' does not exist."

    file_ext = os.path.splitext(file_path)[1] or ".jpg"
    unique_filename = f"{category}/{barcode}_{uuid.uuid4().hex[:8]}{file_ext}"

    try:
        client = get_gcs_client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(unique_filename)

        # Infer content type
        content_type = "image/jpeg"
        if file_ext.lower() in [".png"]:
            content_type = "image/png"
        elif file_ext.lower() in [".webp"]:
            content_type = "image/webp"

        blob.upload_from_filename(file_path, content_type=content_type)
        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{unique_filename}"
        return f"Successfully uploaded image to Cloud Storage!\nPublic URL: {public_url}"
    except Exception as e:
        return f"Error uploading image to Cloud Storage: {str(e)}"


def list_uploaded_product_images(prefix: str = "") -> str:
    """Lists publicly accessible product and barcode images stored in the Cloud Storage bucket.

    Args:
        prefix: Optional prefix to filter images (e.g. 'barcodes/' or 'products/').

    Returns:
        Formatted string list of image URLs.
    """
    try:
        client = get_gcs_client()
        bucket = client.bucket(BUCKET_NAME)
        blobs = bucket.list_blobs(prefix=prefix)

        image_urls = []
        for blob in blobs:
            public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{blob.name}"
            image_urls.append(public_url)

        if image_urls:
            return "Uploaded Images:\n" + "\n".join(image_urls)
        return "No images found in Cloud Storage bucket."
    except Exception as e:
        return f"Error listing images from Cloud Storage: {str(e)}"
