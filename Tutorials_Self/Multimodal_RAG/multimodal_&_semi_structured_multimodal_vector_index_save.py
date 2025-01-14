from langchain_openai import AzureOpenAIEmbeddings
from langchain.document_loaders import CSVLoader, JSONLoader, OnlinePDFLoader, PyMuPDFLoader, UnstructuredExcelLoader
from langchain.document_loaders import CSVLoader, JSONLoader, OnlinePDFLoader, PyMuPDFLoader, UnstructuredAPIFileLoader, AzureBlobStorageFileLoader
from langchain.chat_models.azure_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from operator import itemgetter
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda

import io
import os
import base64
import json
from base64 import b64decode
import numpy as np
from PIL import Image
from langchain.chat_models import ChatOpenAI
from langchain.schema.messages import HumanMessage, SystemMessage

import openai
import os
# os.environ["AZURE_OPENAI_API_KEY"] = "2e147284963d4f938a11c5fbf7afb825"
# os.environ["AZURE_OPENAI_ENDPOINT"] = "https://azureopenaicentralsweden.openai.azure.com/"

import uuid
from langchain.vectorstores import Chroma
from langchain.storage import InMemoryStore, LocalFileStore
from langchain.schema.document import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.retrievers.multi_vector import MultiVectorRetriever

from typing import Any
from PIL import Image
from pydantic import BaseModel
from unstructured.partition.pdf import partition_pdf


## for loading the imagedata json:

with open('image_summary.json', 'r') as infile:
     data = json.load(infile)
     image_summaries = data['image_summaries']
     img_base64_list = data['img_base64_list']

## for loading the text json:
with open('tables.json', 'r') as infile:
     tables = json.load(infile)

## for loading the table json:
with open('table_summary.json', 'r') as infile:
     table_summaries = json.load(infile)

## for loading the table summary json:
with open('text_summary.json', 'r') as infile:
     text_summaries = json.load(infile)


## for loading the text summary json:
with open('texts.json', 'r') as infile:
     texts = json.load(infile)


"""## Add to vectorstore"""

embeddings = AzureOpenAIEmbeddings(
    azure_deployment="text_embedding",
    openai_api_version="2023-05-15",
    chunk_size = 1,
    azure_endpoint="https://cychatopenai.openai.azure.com/",
                             openai_api_key="939524fdbb8d468da705e6c51bbd4894",
                               openai_api_type='azure')

# The vectorstore to use to index the child chunks
vectorstore = Chroma(collection_name = "harvia_823",embedding_function=embeddings,persist_directory="./chroma_db")

# The storage layer for the parent documents
# store = InMemoryStore() # this act like cache memory
store = LocalFileStore("./meta_data_content")
id_key = "doc_id"

# The retriever (empty to start)
retriever = MultiVectorRetriever(
    vectorstore=vectorstore,
    docstore=store,
    id_key=id_key)

# Add texts
doc_ids = [str(uuid.uuid4()) for _ in text_summaries]
summary_texts = [    Document(page_content=s, metadata={id_key: doc_ids[i]}) for i, s in enumerate(text_summaries) ]

retriever.vectorstore.add_documents(summary_texts)
text_meta = []
for i in list(zip(doc_ids, texts)):
   text_meta.append(tuple([i[0],i[1].encode('utf-8')]))
retriever.docstore.mset(text_meta)
#retriever.docstore.mset(list(zip(doc_ids, texts)))


# Add tables
table_ids = [str(uuid.uuid4()) for _ in tables]
summary_tables = [
    Document(page_content=s, metadata={id_key: table_ids[i]})
    for i, s in enumerate(table_summaries)]

retriever.vectorstore.add_documents(summary_tables)
table_meta = []
for i in list(zip(table_ids, tables)):
   table_meta.append(tuple([i[0],i[1].encode('utf-8')]))
retriever.docstore.mset(table_meta)
#retriever.docstore.mset(list(zip(table_ids, tables)))

# Add image summaries
img_ids = [str(uuid.uuid4()) for _ in img_base64_list]
summary_img = [
    Document(page_content=s, metadata={id_key: img_ids[i]})
    for i, s in enumerate(image_summaries) ]

retriever.vectorstore.add_documents(summary_img)
img_meta = []
for i in list(zip(img_ids, img_base64_list)):
   img_meta.append(tuple([i[0],i[1].encode('utf-8')]))
retriever.docstore.mset(img_meta)
#retriever.docstore.mset(list(zip(img_ids, img_base64_list)))

vectorstore.persist()
