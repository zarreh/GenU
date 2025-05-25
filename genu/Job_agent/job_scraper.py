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

from genu.Job_agent.config import HEADERS, LINKEDIN_JOB_SEARCH_URL
from genu.utils import text_clean


def get_job_ids(target_url: str, total_jobs: int = 10) -> list["str"]:
    """
    Scrape job IDs from LinkedIn job search results.
    """
    # List to store job IDs
    job_ids = []

    # Calculate number of pages to scrape (25 jobs per page)
    pages = math.ceil(total_jobs / 25)

    # Get all job IDs
    for i in tqdm(range(0, pages)):
        res = requests.get(
            target_url.format("Python", "New York", i * 25), headers=HEADERS
        )
        soup = BeautifulSoup(res.text, "html.parser")
        jobs_on_page = soup.find_all("li")

        for job in jobs_on_page:
            try:
                job_id = (
                    job.find("div", {"class": "base-card"})  # type: ignore
                    .get("data-entity-urn")  # type: ignore
                    .split(":")[-1]
                )
                job_ids.append(job_id)
            except:
                continue

    return job_ids


def get_job_data(
    job_ids: list[str],
    if_save: bool = True,
    file_name: str = "job_data.csv",
    slow_down: bool = True,
) -> pd.DataFrame:
    """
    Scrape job details from LinkedIn using job IDs.
    """

    job_data = []

    # Get details for each job
    job_details_url = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{}"
    for job_id in tqdm(job_ids):
        resp = requests.get(job_details_url.format(job_id), headers=HEADERS)
        soup = BeautifulSoup(resp.text, "html.parser")

        job_info = {}
        try:
            job_info["company"] = (
                soup.find("div", {"class": "top-card-layout__card"})
                .find("a")  # type: ignore
                .find("img")
                .get("alt")
            )

            job_info["title"] = (
                soup.find("div", {"class": "top-card-layout__entity-info"})
                .find("a")  # type: ignore
                .text.strip()
            )

            # Get all li elements in the list
            criteria_list = soup.find(
                "ul", {"class": "description__job-criteria-list"}
            ).find_all(  # type: ignore
                "li"
            )  

            # Field names in order they typically appear
            field_names = ["level", "employment_type", "job_function", "industries"]
            field_labels = [
                "Seniority level",
                "Employment type",
                "Job function",
                "Industries",
            ]

            # Process each field
            for i, field in enumerate(field_names):
                if i < len(criteria_list):
                    job_info[field] = (
                        criteria_list[i].text.replace(field_labels[i], "").strip()
                    )
                else:
                    job_info[field] = ""

            # ========== Extracting job description ==========
            desc_elem = soup.find(
                "div", {"class": "description__text description__text--rich"}
            )
            job_info["description"] = text_clean(
                desc_elem.text.strip() if desc_elem else ""
            )
            job_info["link"] = job_details_url.format(job_id)
            job_data.append(job_info)
        except:
            continue

        if slow_down:
            time.sleep(random.uniform(1, 3))

    df = pd.DataFrame.from_dict(job_data)  # type: ignore
    if if_save:
        df.to_csv(file_name, index=False, encoding="utf-8-sig")

    return df


def save_to_vectorestore(
    df: pd.DataFrame, persist_directory="data/job_data/vectorstore"
) -> None:
    """
    Save job data to a vector store.
    """
    combine_list = ["title", "company", "description", "job_function", "industries",]
    metadata_list = ["title", "company", "job_function", "industries", "level", "employment_type" ,"link"]

    def combine_text_columns(row):
        text_content = ""
        for col in combine_list:  # List your text columns here
            if col in row and pd.notna(
                row[col]
            ):  # Check if the column exists and is not NaN
                text_content += str(row[col]) + " \n "  # Concatenate with a space
        return text_content.strip()  # Remove trailing spa

    print(f"Shape of table: {df.shape}")
    # Create embeddings
    embeddings = OpenAIEmbeddings()

    # Convert DataFrame to documents (as shown in previous examples)
    documents = [
        Document(
            page_content=combine_text_columns(row),
            metadata= {k: v for k, v in row.items() if k in metadata_list},
        )
        for _, row in df.iterrows()
    ]

    vectorstore_faiss = FAISS.from_documents(documents, embeddings)
    vectorstore_faiss.save_local(f"{persist_directory}_faiss")

    # Create and persist the vector store
    # vectorstore = Chroma.from_documents(
    #     documents=documents,
    #     embedding=embeddings,
    #     persist_directory=f"{persist_directory}_chroma",
    # )

    # print("Chroma vectorstore count:", vectorstore._collection.count())
    print("FAISS vectorstore count:", len(vectorstore_faiss.index_to_docstore_id))

    # # Load
    # loaded_chroma = Chroma(
    #     persist_directory=persist_directory,
    #     embedding_function=embeddings
    # )
    # print("Loaded:", loaded_chroma.get())

    # loaded_vectorstore = FAISS.load_local(
    #     f"{persist_directory}_faiss",
    #     OpenAIEmbeddings(),
    #     allow_dangerous_deserialization=True,
    # )
    # # For FAISS
    # print("FAISS vectorstore count:", len(loaded_vectorstore.index_to_docstore_id))


if __name__ == "__main__":
    print("Starting job scraping...")
    total_job_per_link = 500
    job_id_list = []
    for target_url in LINKEDIN_JOB_SEARCH_URL:
        print(f"Scraping from: {target_url}")
        _ls = get_job_ids(target_url, total_jobs=total_job_per_link)
        print(f"Found {len(_ls)} job IDs in this page.")
        [job_id_list.append(id) for id in _ls]  # type: ignore
        print(f"Found {len(list(set(job_id_list)))} uniquer job IDs SO FAR.")

    print(f"Found {len(list(set(job_id_list)))} uniquer job IDs.")
    job_df = get_job_data(
        list(set(job_id_list)),
        if_save=True,
        file_name="data/job_data/senior_data_scientist.csv",
        slow_down=True,
    )
    # print(job_df.head(3))
    save_to_vectorestore(df=job_df, persist_directory="data/job_data/vectorstore")
