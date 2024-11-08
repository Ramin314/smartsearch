import os

from django.conf import settings	
from django.http import HttpResponseRedirect	
from django.urls import reverse	
from django.shortcuts import render	
from haystack_integrations.components.retrievers.opensearch import OpenSearchEmbeddingRetriever	
from haystack.components.builders import PromptBuilder	
from haystack.components.embedders import OpenAITextEmbedder	
from haystack.components.generators import OpenAIGenerator	
from haystack import Pipeline	
from haystack.utils import Secret	

from .utils import get_document_store, process_pdf, get_s3_client	
from . import models	


def index(request):
    search_url = reverse('search')
    return HttpResponseRedirect(search_url)

def upload(request):	
    if request.method == 'POST' and request.FILES.get('pdf'):	
        uploaded_file = request.FILES['pdf']	

        db_document = models.Document.objects.create(	
            name=os.path.basename(uploaded_file.name),	
        )	

        s3_client = get_s3_client()	
        object_key = f"{db_document.id}.pdf"	
        s3_client.upload_fileobj(uploaded_file, settings.S3_FILES_BUCKET, object_key)	

        process_pdf(document_id=str(db_document.id))	

        return render(request, 'upload_success.html')	
    return render(request, 'upload.html')	

def search_view(request):	
    if request.method == 'POST':	
        query = request.POST.get('query', '')	
        document_store = get_document_store()	
        query_pipeline = Pipeline()	
        query_pipeline.add_component(	
            "text_embedder", OpenAITextEmbedder(api_key=Secret.from_token(settings.OPEN_AI_API_KEY)))	
        query_pipeline.add_component("retriever", OpenSearchEmbeddingRetriever(document_store=document_store))	
        query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")	

        result = query_pipeline.run({"text_embedder": {"text": query}})	

        search_results = []	

        for doc in result['retriever']['documents']:	
            search_results.append((	
                doc.meta['title'],	
                doc.content,	
                models.Document.s3_file_link(doc.meta['db_id']),	
                models.Document.s3_text_link(doc.meta['db_id']),	
            ))	

        return render(request, 'search.html', {'query': query, 'search_results': search_results})	
    else:	
        return render(request, 'search.html')	

def ask(request):	
    if request.method == 'POST':	
        question = request.POST.get('question', '')	

        document_store = get_document_store()	

        text_embedder = OpenAITextEmbedder(api_key=Secret.from_token(settings.OPEN_AI_API_KEY))	

        retriever = OpenSearchEmbeddingRetriever(document_store=document_store)	

        template = """	
        Only using the following context, answer the question.	
        Context:	
        {% for document in documents %}	
            {{ document.content }}	
        {% endfor %}	
        Question: {{question}}	
        Answer:	
        """	

        prompt_builder = PromptBuilder(template=template)	

        generator = OpenAIGenerator(model="gpt-3.5-turbo")	

        basic_rag_pipeline = Pipeline()	

        basic_rag_pipeline.add_component("text_embedder", text_embedder)	
        basic_rag_pipeline.add_component("retriever", retriever)	
        basic_rag_pipeline.add_component("prompt_builder", prompt_builder)	
        basic_rag_pipeline.add_component("llm", generator)	

        basic_rag_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")	
        basic_rag_pipeline.connect("retriever", "prompt_builder.documents")	
        basic_rag_pipeline.connect("prompt_builder", "llm")	

        response = basic_rag_pipeline.run({"text_embedder": {"text": question}, "prompt_builder": {"question": question}})	

        answer = response["llm"]["replies"][0]	

        return render(request, 'ask.html', {'question': question, 'answer': answer})	
    else:	
        return render(request, 'ask.html')	
