from langchain_openai import AzureOpenAIEmbeddings
from langchain.document_loaders import CSVLoader, JSONLoader, OnlinePDFLoader, PyMuPDFLoader, UnstructuredExcelLoader
from langchain.document_loaders import CSVLoader, JSONLoader, OnlinePDFLoader, PyMuPDFLoader, UnstructuredAPIFileLoader, AzureBlobStorageFileLoader
from langchain.chat_models.azure_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

import io
import os
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


path = '/content/BenefitsYou Portal_User Guide_321234.pdf'

from typing import Any
from PIL import Image
from pydantic import BaseModel
from unstructured.partition.pdf import partition_pdf

# Get elements
raw_pdf_elements = partition_pdf(
    filename=path,
    # Using pdf format to find embedded image blocks
    extract_image_block_types=['Table', 'Image'],
    # Use layout model (YOLOX) to get bounding boxes (for tables) and find titles
    # Titles are any sub-section of the document
    infer_table_structure=True,
    include_page_breaks=True,
    # Post processing to aggregate text once we have the title
    chunking_strategy= 'by_title',#"by_title",
    # Chunking params to aggregate text blocks
    # Attempt to create a new chunk 3800 chars
    # Attempt to keep chunks > 2000 chars
    # Hard max on chunks
    #max_characters=4000,
    #new_after_n_chars=3800,
    #combine_text_under_n_chars=2000,
    image_output_dir_path="/content/",   )

documents = []
#pdf_path = "/content/stateofgpt.pdf"
loader = PyMuPDFLoader(path)
documents.extend(loader.load())

# Create a dictionary to store counts of each type
category_counts = {}
for element in raw_pdf_elements:
    category = str(type(element))
    if category in category_counts:
        category_counts[category] += 1
    else:
        category_counts[category] = 1

# Unique_categories will have unique elements
unique_categories = set(category_counts.keys())

# Categorize by type
tables = []
texts = []
for element in raw_pdf_elements:
    if "unstructured.documents.elements.Table" in str(type(element)):
        tables.append(str(element))
    elif "unstructured.documents.elements.CompositeElement" in str(type(element)):
        texts.append(str(element))

for i in documents:
  texts.append(i.page_content)

"""### Text and Table summaries"""

# Prompt
prompt_text = """You are an assistant tasked with summarizing tables and text. \
Give a concise summary of the table or text. Table or text chunk: {element} """
prompt = ChatPromptTemplate.from_template(prompt_text)

# Summary chain
#model = AzureChatOpenAI(deployment_name="gpt_4_vision_preview",temperature = 0.0,max_tokens = 500,api_version='2023-07-01-preview')
model_3 = AzureChatOpenAI(openai_api_base="https://cychatopenai.openai.azure.com/",
                            openai_api_version="2023-05-15",
                            deployment_name="gpt_35_turbo_16k",
                            openai_api_key="939524fdbb8d468da705e6c51bbd4894",
                            openai_api_type="azure",temperature = 0.0,max_tokens = 500)
summarize_chain = {"element": lambda x: x} | prompt | model_3 | StrOutputParser()

# Apply to text
# Typically this is reccomended only if you have large text chunks
text_summaries = summarize_chain.batch(texts)

# Apply to tables
table_summaries = summarize_chain.batch(tables, {"max_concurrency": 5})

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
prompt = "Describe the image in detail. Be specific about graphs, such as bar plots. and also about tables."
path = '/content/figures/'
# Read images, encode to base64 strings
for img_file in sorted(os.listdir(path)):
    if img_file.endswith('.jpg'):
        img_path = os.path.join(path, img_file)
        print(img_path)
        base64_image = encode_image(img_path)
        img_base64_list.append(base64_image)
        image_summaries.append(image_summarize(base64_image,prompt))
################################################################################################################ Preprocessing done
