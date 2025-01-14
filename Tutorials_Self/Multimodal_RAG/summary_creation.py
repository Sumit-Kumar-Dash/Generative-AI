from langchain_openai import AzureOpenAIEmbeddings
from langchain.document_loaders import CSVLoader, JSONLoader, OnlinePDFLoader, PyMuPDFLoader, UnstructuredExcelLoader
from langchain.document_loaders import CSVLoader, JSONLoader, OnlinePDFLoader, PyMuPDFLoader, UnstructuredAPIFileLoader, AzureBlobStorageFileLoader
from langchain.chat_models.azure_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

import io
import os
import json
import base64
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
from langchain.storage import InMemoryStore
from langchain.storage import InMemoryStore

from langchain.schema.document import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.retrievers.multi_vector import MultiVectorRetriever


from typing import Any
from PIL import Image
from pydantic import BaseModel
from unstructured.partition.pdf import partition_pdf

llm = AzureChatOpenAI(openai_api_base="https://cychatopenai.openai.azure.com/",
                            openai_api_version="2023-05-15",
                            deployment_name="gpt_35_turbo_16k",
                            openai_api_key="939524fdbb8d468da705e6c51bbd4894",
                            openai_api_type="azure",temperature = 0.0,max_tokens = 500)



"""### Text and Table summaries"""

from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

## for loading text and tables
with open("texts.json", "r") as text_file:
    texts = json.load(text_file)
with open("tables.json", "r") as table_file:
    tables = json.load(table_file)


# Generate summaries of text elements
def generate_text_summaries(texts, tables, summarize_texts=False):
    """
    Summarize text elements
    texts: List of str
    tables: List of str
    summarize_texts: Bool to summarize texts
    """

    # Prompt
    prompt_text = """You are an assistant tasked with summarizing tables and text for retrieval. \
    These summaries will be embedded and used to retrieve the raw text or table elements. \
    Give a concise summary of the table or text that is well-optimized for retrieval. Table \
    or text: {element} """

    prompt = PromptTemplate.from_template(prompt_text)
    empty_response = RunnableLambda(
        lambda x: AIMessage(content="Error processing document")
    )
    # Text summary chain

    # llm = ChatGoogleGenerativeAI(model="gemini-pro")

    summarize_chain = {"element": lambda x: x} | prompt | llm | StrOutputParser()

    # Initialize empty summaries
    text_summaries = []
    table_summaries = []

    # Apply to text if texts are provided and summarization is requested
    if texts and summarize_texts:
        text_summaries = summarize_chain.batch(texts, {"max_concurrency": 1})
    elif texts:
        text_summaries = texts

    # Apply to tables if tables are provided
    if tables:
        table_summaries = summarize_chain.batch(tables, {"max_concurrency": 1})

    return text_summaries, table_summaries


# Get text, table summaries
text_summaries, table_summaries = generate_text_summaries(texts, tables, summarize_texts=True)

## for saving tables and text

with open("text_summary.json", "w") as text_file:
     json.dump(text_summaries, text_file)
with open("table_summary.json", "w") as table_file:
     json.dump(table_summaries, table_file)


"""## Image Summaries"""

def encode_image(image_path):
    ''' Getting the base64 string '''
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def image_summarize(img_base64,prompt):
    ''' Image summary '''
    chat = AzureChatOpenAI(deployment_name="gpt_4_vision_preview",temperature = 0.0,
                           openai_api_key = '2e147284963d4f938a11c5fbf7afb825',
                           openai_api_base = 'https://azureopenaicentralsweden.openai.azure.com/',
                           max_tokens = 500,api_version='2023-07-01-preview')

    msg = chat.invoke(
        [
            HumanMessage(
                content=[
                    {"type": "text", "text":prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_base64}"
                        },
                    },
                ]
            )
        ]
    )
    return msg.content

# Store base64 encoded images
img_base64_list = []

# Store image summaries
image_summaries = []

# Prompt
prompt = """You are an AI assistant specialized in image summarization for efficient retrieval. 
      Your goal is to generate concise and optimized textual summaries for images. 
      These summaries will be transformed into embeddings and utilized to retrieve the corresponding raw images. 
      Craft a succinct summary that is tailored for optimal performance in image retrieval systems.
      Be specific about graphs, such as bar plots. and also about tables."""

path = './figures/'
# Read images, encode to base64 strings
for img_file in sorted(os.listdir(path)):
    if img_file.endswith('.jpg'):
        img_path = os.path.join(path, img_file)
        print(img_path)
        base64_image = encode_image(img_path)
        img_base64_list.append(base64_image)
        image_summaries.append(image_summarize(base64_image,prompt))

# ## saving in imagedata json
with open('image_data.json', 'w') as outfile:
     json.dump({'img_base64_list': img_base64_list, 'image_summaries': image_summaries}, outfile)

################################################################################################################ Preprocessing done
