import json
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
import os

os.environ["OPENAI_API_KEY"] = "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"


raw_documents = TextLoader('FVE.').load()
text_splitter = CharacterTextSplitter(chunk_size = 500, chunk_overlap = 0)
documents = text_splitter.split_documents(raw_documents)
db = Chroma.from_documents(documents, OpenAIEmbeddings())