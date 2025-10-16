import os
import hashlib
import boto3
from django.conf import settings
from botocore.exceptions import ClientError


class UploadService:
    """
    Service for handling file uploads to S3
    """

    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    def upload_to_s3(self, file_obj, tenant_id):
        """
        Upload file to S3 and return file path and hash
        """
        # Calculate file hash
        file_hash = self._calculate_file_hash(file_obj)

        # Generate S3 key
        file_extension = os.path.splitext(file_obj.name)[1].lower()
        s3_key = f"contracts/{tenant_id}/{file_hash}{file_extension}"

        try:
            # Upload to S3
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': file_obj.content_type,
                    'Metadata': {
                        'original_filename': file_obj.name,
                        'file_hash': file_hash
                    }
                }
            )

            return s3_key, file_hash

        except ClientError as e:
            raise Exception(f"Failed to upload file to S3: {str(e)}")

    def get_presigned_url(self, s3_key, expiration=3600):
        """
        Generate presigned URL for file download
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")

    def delete_from_s3(self, s3_key):
        """
        Delete file from S3
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
        except ClientError as e:
            raise Exception(f"Failed to delete file from S3: {str(e)}")

    def _calculate_file_hash(self, file_obj):
        """
        Calculate SHA-256 hash of file
        """
        hash_sha256 = hashlib.sha256()

        # Reset file pointer to beginning
        file_obj.seek(0)

        # Read file in chunks to handle large files
        for chunk in iter(lambda: file_obj.read(4096), b""):
            hash_sha256.update(chunk)

        # Reset file pointer to beginning for subsequent operations
        file_obj.seek(0)

        return hash_sha256.hexdigest()