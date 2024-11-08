from django.core.management.base import BaseCommand
from app import models
from app import utils

from django.conf import settings
from haystack.components.embedders import OpenAITextEmbedder
from haystack.document_stores.types import DuplicatePolicy
from haystack import Document
from haystack.utils import Secret
import boto3

from haystack.components.embedders import OpenAITextEmbedder	
import tqdm
from haystack.components.preprocessors import DocumentSplitter, DocumentCleaner


class Command(BaseCommand):
    help = 'Populate the database with initial data'

    def handle(self, *args, **options):
        document_store = utils.get_document_store()
        s3 = boto3.client('s3',
                  aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                  region_name=settings.AWS_REGION)
        
        source_bucket_name = 'itjpsl-textract-uploads'
        output_bucket_name = 'smart-search-outputs'

        # List objects in source bucket
        response = s3.list_objects_v2(Bucket=source_bucket_name)
        files = response.get('Contents', [])

        i = 0

        # Iterate over files in the bucket
        for file in tqdm.tqdm(files, desc='Processing files'):
            i+=1
            if i==40:
                break
            # Extract file name
            filename = file['Key']

            # Create Document object
            db_document = models.Document.objects.create(
                name=filename.replace('.pdf',''),
            )

            # Upload file to smart-search-inputs bucket
            s3.copy_object(CopySource={'Bucket': source_bucket_name, 'Key': filename},
                        Bucket='smart-search-inputs', Key=str(db_document.id) + '.pdf')

            # Download file from itjpsl-textract-output-eu-west-1 bucket
            download_filename = filename + '.txt'
            s3.download_file('itjpsl-textract-output-eu-west-1', download_filename, download_filename)

            # Upload downloaded file to smart-search-outputs bucket
            s3.upload_file(download_filename, 'smart-search-outputs', str(db_document.id) + '.txt')

            # Read text from the downloaded file
            with open(download_filename, 'r') as f:
                text = f.read()

            # ai stuff starts here

            text_embedder = OpenAITextEmbedder(api_key=Secret.from_token(settings.OPEN_AI_API_KEY))
            
            temp_doc = Document(content=text)

            document_cleaner = DocumentCleaner()
            document_splitter = DocumentSplitter(split_by="word", split_length=150, split_overlap=50)

            temp_doc = document_cleaner.run([temp_doc])['documents'][0]

            documents = []
            for doc in document_splitter.run([temp_doc])['documents']:
                embedding = text_embedder.run(doc.content)["embedding"]

                document = Document(
                    content=doc.content,
                    embedding=embedding,
                    meta={
                        'db_id': str(db_document.id),
                        'title': filename.replace('.pdf',''),
                    },
                )
                documents.append(document)
            document_store.write_documents(documents, policy=DuplicatePolicy.SKIP)

