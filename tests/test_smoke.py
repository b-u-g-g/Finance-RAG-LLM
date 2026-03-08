"""
Smoke tests — verify core dependencies are importable in the environment.
These run without any API keys or network access.
"""
import sys


def test_python_version_is_311_or_higher():
    assert sys.version_info >= (3, 11), f"Expected Python 3.11+, got {sys.version}"


def test_requests_importable():
    import requests
    assert requests is not None


def test_pandas_importable():
    import pandas as pd
    assert pd is not None


def test_plotly_importable():
    import plotly.express as px
    assert px is not None


def test_langchain_core_importable():
    from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
    assert PromptTemplate is not None
    assert ChatPromptTemplate is not None


def test_langchain_chains_importable():
    from langchain.chains import create_history_aware_retriever, create_retrieval_chain
    from langchain.chains.combine_documents import create_stuff_documents_chain
    assert create_history_aware_retriever is not None
    assert create_retrieval_chain is not None
    assert create_stuff_documents_chain is not None


def test_langchain_community_importable():
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import Chroma
    assert HuggingFaceEmbeddings is not None
    assert Chroma is not None


def test_pinecone_importable():
    from pinecone import Pinecone, ServerlessSpec
    assert Pinecone is not None


def test_groq_importable():
    from langchain_groq import ChatGroq
    assert ChatGroq is not None


def test_pymongo_importable():
    from pymongo import MongoClient
    assert MongoClient is not None
