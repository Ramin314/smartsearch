import os
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    @classmethod
    def s3_file_link(cls, id):
        environment = os.getenv('ENVIRONMENT')
        if environment == 'local':
            s3_endpoint = "http://localhost:4566"
        else:
            s3_endpoint = "https://smart-search-inputs.s3.eu-west-1.amazonaws.com"
        bucket_name = settings.S3_FILES_BUCKET

        s3_link = f"{s3_endpoint}/{id}.pdf"
        return s3_link

    @classmethod
    def s3_text_link(cls, id):
        environment = os.getenv('ENVIRONMENT')
        if environment == 'local':
            s3_endpoint = "http://localhost:4566"
        else:
            s3_endpoint = "https://smart-search-outputs.s3.eu-west-1.amazonaws.com"
        bucket_name = settings.S3_PROCESSED_BUCKET

        s3_link = f"{s3_endpoint}/{id}.txt"
        return s3_link
