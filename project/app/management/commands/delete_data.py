from django.core.management.base import BaseCommand
from app import models
from app import utils

from django.conf import settings
import boto3


class Command(BaseCommand):
    help = 'Populate the database with initial data'

    def handle(self, *args, **options):
        document_store = utils.get_document_store()
        s3 = boto3.client('s3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION)

        document_store.delete_documents([d.id for d in document_store._search_documents()])
        models.Document.objects.all().delete()

        # Empty the 'smart-search-outputs' bucket
        bucket_name_outputs = 'smart-search-outputs'
        objects_outputs = s3.list_objects_v2(Bucket=bucket_name_outputs)
        if 'Contents' in objects_outputs:
            delete_objects = [{'Key': obj['Key']} for obj in objects_outputs['Contents']]
            s3.delete_objects(Bucket=bucket_name_outputs, Delete={'Objects': delete_objects})

        # Empty the 'smart-search-inputs' bucket
        bucket_name_inputs = 'smart-search-inputs'
        objects_inputs = s3.list_objects_v2(Bucket=bucket_name_inputs)
        if 'Contents' in objects_inputs:
            delete_objects = [{'Key': obj['Key']} for obj in objects_inputs['Contents']]
            s3.delete_objects(Bucket=bucket_name_inputs, Delete={'Objects': delete_objects})

        self.stdout.write(self.style.SUCCESS('Successfully handled command'))

