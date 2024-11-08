import os

from django.conf import settings
from haystack.components.embedders import OpenAITextEmbedder
from haystack.document_stores.types import DuplicatePolicy
from haystack_integrations.document_stores.opensearch import OpenSearchDocumentStore
from haystack import Document
from haystack.utils import Secret
from PIL import Image
import fitz
import pytesseract
import boto3
from io import BytesIO

from . import models

def get_document_store():
    return OpenSearchDocumentStore(
        hosts='http://' + settings.OPEN_SEARCH_HOST + ':9200',
        use_ssl=True,
        verify_certs=False,
        http_auth=("admin", settings.OPEN_SEARCH_ADMIN_PASSWORD),
        index="document-dim-1536",
        embedding_dim=1536,
    )

def get_s3_client():
    if os.getenv("ENVIRONMENT") == "local":
        return boto3.client("s3", endpoint_url="http://localstack:4566")
    else:
        return boto3.client("s3")

def process_pdf(document_id):

    document = models.Document.objects.get(id=document_id)

    s3_client = get_s3_client()
    s3_response = s3_client.get_object(
        Bucket=settings.S3_FILES_BUCKET, Key=f"{document.id}.pdf")
    pdf_content = s3_response['Body'].read()

    # OCR processing

    with BytesIO(pdf_content) as pdf_file:
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        pdf_name = os.path.basename(document.name)  
        for page_number in range(len(pdf_document)):
            page = pdf_document.load_page(page_number)

            pix = page.get_pixmap()
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            ocr_text = pytesseract.image_to_string(image)
        pdf_document.close()

    # Upload text content

    s3_client.put_object(
        Bucket=settings.S3_PROCESSED_BUCKET,
        Key=f"{document_id}.txt",
        Body=ocr_text.encode('utf-8'),
        ContentType='text/plain'
    )

    # LLM embedding

    text_embedder = OpenAITextEmbedder(api_key=Secret.from_token(settings.OPEN_AI_API_KEY))
    embedding = text_embedder.run(ocr_text)["embedding"]

    # Store in OpenSearch

    document = Document(
        content=ocr_text,
        embedding=embedding,
        meta={
            'db_id': document_id,
            'title': pdf_name,
        },
    )

    document_store = get_document_store()
    document_store.write_documents([document], policy=DuplicatePolicy.SKIP)
	