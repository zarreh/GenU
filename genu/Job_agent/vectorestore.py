import datetime
import math
import random
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from tqdm import tqdm

from genu.Job_agent.config import (HEADERS, LINKEDIN_JOB_SEARCH_PARAMS,
                                   PERSIST_PATH)
from genu.utils import text_clean


def save_to_vectorestore(
    df, persist_directory, combine_list, metadata_list, append_to_vectorestore=True
):
    def combine_text_columns(row):
        text_content = ""
        for col in combine_list:
            if col in row and pd.notna(row[col]):
                text_content += str(row[col]) + " \n "
        return text_content.strip()

    print(f"Shape of table: {df.shape}")
    # Create embeddings
    embeddings = OpenAIEmbeddings()

    # Convert DataFrame to documents
    documents = [
        Document(
            page_content=combine_text_columns(row),
            metadata={k: v for k, v in row.items() if k in metadata_list},
        )
        for _, row in df.iterrows()
    ]

    # Check if job_id is in metadata_list
    if "job_id" not in metadata_list:
        print(
            "Warning: 'job_id' not in metadata_list. Duplicate prevention won't work."
        )

    if append_to_vectorestore:
        # Try to load existing index
        try:
            vectorstore = FAISS.load_local(
                persist_directory, embeddings, allow_dangerous_deserialization=True
            )
            print("Loaded existing FAISS index.")

            # Get existing job_ids
            existing_job_ids = set()
            for doc_id in vectorstore.index_to_docstore_id.values():
                doc = vectorstore.docstore.search(doc_id)
                if doc and "job_id" in doc.metadata:
                    existing_job_ids.add(doc.metadata["job_id"])

            print(
                f"Found {len(existing_job_ids)} existing job_ids in the vector store."
            )

            # Filter out documents with existing job_ids
            new_documents = []
            for doc in documents:
                if (
                    "job_id" in doc.metadata
                    and doc.metadata["job_id"] in existing_job_ids
                ):
                    continue  # Skip this document
                new_documents.append(doc)

            print(
                f"Adding {len(new_documents)} new documents out of {len(documents)} total."
            )

            # Add only new documents
            if new_documents:
                vectorstore.add_documents(new_documents)

        except Exception as e:
            print(f"Error loading existing index: {e}")
            # If not found, create new
            vectorstore = FAISS.from_documents(documents, embeddings)
            print("Created new FAISS index.")
    else:
        # Create new vector store
        vectorstore = FAISS.from_documents(documents, embeddings)

    # Save the index
    vectorstore.save_local(persist_directory)

    print("FAISS vectorstore count:", len(vectorstore.index_to_docstore_id))

    return vectorstore
