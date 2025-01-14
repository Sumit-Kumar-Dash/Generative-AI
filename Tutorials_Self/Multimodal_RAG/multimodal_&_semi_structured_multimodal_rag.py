from langchain_openai import AzureOpenAIEmbeddings
from langchain.document_loaders import CSVLoader, JSONLoader, OnlinePDFLoader, PyMuPDFLoader, UnstructuredExcelLoader
from langchain.document_loaders import CSVLoader, JSONLoader, OnlinePDFLoader, PyMuPDFLoader, UnstructuredAPIFileLoader, AzureBlobStorageFileLoader
from langchain.chat_models.azure_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from operator import itemgetter
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda, RunnableParallel

import io
import os
import base64
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
from langchain.storage import InMemoryStore,LocalFileStore
from langchain.schema.document import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.retrievers.multi_vector import MultiVectorRetriever

from typing import Any
from PIL import Image
from pydantic import BaseModel
from unstructured.partition.pdf import partition_pdf

# load from disk
# Note: The following code is demonstrating how to load the Chroma database from disk.

embeddings = AzureOpenAIEmbeddings(
    azure_deployment="text_embedding",
    openai_api_version="2023-05-15",
    chunk_size = 1,
    azure_endpoint="https://cychatopenai.openai.azure.com/",
                             openai_api_key="939524fdbb8d468da705e6c51bbd4894",
                               openai_api_type='azure')

vectorstore = Chroma(collection_name = "harvia_823",embedding_function=embeddings,persist_directory="./chroma_db")

def plt_img_base64(img_base64):

    # Create an HTML img tag with the base64 string as the source
    image_html = f'<img src="data:image/jpeg;base64,{img_base64}" />'
    return image_html
    # Display the image by rendering the HTML
    # display(HTML(image_html))

def is_image_data(b64data):
    """
    Check if the base64 data is an image by looking at the start of the data
    """
    image_signatures = {
        b"\xFF\xD8\xFF": "jpg",
        b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A": "png",
        b"\x47\x49\x46\x38": "gif",
        b"\x52\x49\x46\x46": "webp",
    }
    try:
        header = base64.b64decode(b64data)[:8]  # Decode and get the first 8 bytes
        for sig, format in image_signatures.items():
            if header.startswith(sig):
                return True
        return False
    except Exception:
        return False


def resize_base64_image(base64_string, size=(128, 128)):
    """
    Resize an image encoded as a Base64 string
    """
    # Decode the Base64 string
    img_data = base64.b64decode(base64_string)
    img = Image.open(io.BytesIO(img_data))

    # Resize the image
    resized_img = img.resize(size, Image.LANCZOS)

    # Save the resized image to a bytes buffer
    buffered = io.BytesIO()
    resized_img.save(buffered, format=img.format)

    # Encode the resized image to Base64
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def split_image_text_types(docs):
    ''' Split base64-encoded images and texts 
        It used to collect both text(textual and summary) and b64(images) '''
    b64 = []
    text = []
    for doc in docs:
        try:
            b64decode(doc)
            b64.append(doc)
        except Exception as e:
            text.append(doc)
    return {
        "images": b64,
        "texts": text
    }

def prompt_func(data_dict):
    # Joining the context texts into a single string
    decode_string_list  = []
    for i in data_dict["context"]["texts"]:
           decode_string_list.append(i.decode('utf-8'))
    #print(data_dict["context"]["texts"])
    formatted_texts = "\n".join(decode_string_list)
    messages = []

    # Adding image(s) to the messages if present
    decode_images_list = []
    for i in data_dict["context"]["images"]:
           decode_images_list.append(i.decode('utf-8'))
    if decode_images_list:
        image_message = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{decode_images_list[0]}"
            },
        }
        messages.append(image_message)

    # Adding the text message for analysis
    # Adding the text for analysis
    text_message = {
        "type": "text",
        "text": (
            "You are an AI scientist tasking with providing factual answers.\n"
            "You will be given a mixed of text, tables, and image(s) usually of charts or graphs.\n"
            "Use this information to provide answers related to the user question. \n"
            f"User-provided question: {data_dict['question']}\n\n"
            "Text and / or tables:\n"
            f"{formatted_texts}"
        ),
    }

    messages.append(text_message)

    return [HumanMessage(content=messages)]

# The storage layer for the parent documents
#store = InMemoryStore()
store = LocalFileStore("./meta_data_content")
id_key = "doc_id"

# The retriever (empty to start)
retriever = MultiVectorRetriever(
    vectorstore=vectorstore,
    docstore=store,
    id_key=id_key)

llm = AzureChatOpenAI(deployment_name="gpt_4_vision_preview",temperature = 0.0,
                           openai_api_key = '2e147284963d4f938a11c5fbf7afb825',
                           openai_api_base = 'https://azureopenaicentralsweden.openai.azure.com/',
                           max_tokens = 500,api_version='2023-07-01-preview')

# RAG pipeline
chain = (
    {"context": retriever | RunnableLambda(split_image_text_types), "question": RunnablePassthrough()}
    | RunnableParallel({"response":prompt_func| llm | StrOutputParser(),  "context": itemgetter("context"),}))

response = chain.invoke("what is Safety distances (all dimensions in millimeters)")
#print(response['context'])
print(response['response'])
print(plt_img_base64(response['context']['images'][0]))