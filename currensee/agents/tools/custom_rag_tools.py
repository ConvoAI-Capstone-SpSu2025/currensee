from typing import Literal
from langchain_core.messages import HumanMessage
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
import os




@tool
def retrieve_context_dynamic(query: str):
    """Search for relevant documents."""
    
    collection_name="New Collection
    
    docs = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=50)
    doc_splits = text_splitter.split_documents(docs)
    
    vectorstore = Chroma.from_documents(
        documents=doc_splits,
        collection_name=collection_name,
        embedding=OpenAIEmbeddings(),
    )
    retriever = vectorstore.as_retriever()
    results = retriever.invoke(query)
    return "\n".join([doc.page_content for doc in results])