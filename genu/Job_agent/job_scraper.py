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

from genu.Job_agent.config import (COMBINE_LIST, HEADERS,
                                   LINKEDIN_JOB_SEARCH_PARAMS, METADATA_LIST,
                                   PERSIST_PATH)
from genu.Job_agent.vectorestore import save_to_vectorestore
from genu.utils import text_clean


def linkedin_link_constructor(search_params: list[dict[str, str | bool]]):

    target_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={}&location={}&f_TPR={}"

    url_list = []
    for params in search_params:
        url = target_url.format(
            params["keywords"].replace(" ", "%20"),  # type: ignore
            params["location"].replace(" ", "%20"),  # type: ignore
            params["f_TPR"],
            # params["start"]
        )
        if params["parttime"]:
            url += "&f_JT=P"
        if params["remote"]:
            url += "&f_WT=2"
        # print(url)
        url_list.append(url + "&start={}")
    return url_list


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
        res = requests.get(target_url.format(i * 25), headers=HEADERS)
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
    date = datetime.datetime.now().date().isoformat()

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

            # For the posted time
            posted_time_elem = soup.find("span", {"class": "posted-time-ago__text"})
            job_info["posted_time"] = (
                posted_time_elem.text.strip() if posted_time_elem else "N/A"
            )

            # For the number of applicants
            applicants_elem = soup.find("span", {"class": "num-applicants__caption"})
            job_info["applicants"] = (
                applicants_elem.text.strip() if applicants_elem else "N/A"
            )
            job_info["parsing_link"] = job_details_url.format(job_id)

            link_elem = soup.find("a", {"class": "topcard__link"})
            job_info["job_posting_link"] = link_elem.get("href") if link_elem else "N/A"  # type: ignore

            job_info["job_id"] = job_id

            job_info["date"] = date
            job_data.append(job_info)
        except:
            continue

        if slow_down:
            time.sleep(random.uniform(1, 3))

    df = pd.DataFrame.from_dict(job_data)  # type: ignore
    if if_save:
        df.to_csv(file_name, index=False, encoding="utf-8-sig")

    return df


# def save_to_vectorestore(
#     df: pd.DataFrame, persist_directory="data/job_data/vectorstore",
#     append_to_vectorestore: bool = True
# ) -> None:
#     """
#     Save job data to a vector store.
#     """


#     def combine_text_columns(row):
#         text_content = ""
#         for col in COMBINE_LIST:  # List your text columns here
#             if col in row and pd.notna(
#                 row[col]
#             ):  # Check if the column exists and is not NaN
#                 text_content += str(row[col]) + " \n "  # Concatenate with a space
#         return text_content.strip()  # Remove trailing spa

#     print(f"Shape of table: {df.shape}")
#     # Create embeddings
#     embeddings = OpenAIEmbeddings()

#     # Convert DataFrame to documents (as shown in previous examples)
#     documents = [
#         Document(
#             page_content=combine_text_columns(row),
#             metadata={k: v for k, v in row.items() if k in METADATA_LIST},
#         )
#         for _, row in df.iterrows()
#     ]

#     if append_to_vectorestore:
#         # Try to load existing index
#         try:
#             vectorstore = FAISS.load_local(
#                 persist_directory,
#                 embeddings,
#                 allow_dangerous_deserialization=True
#             )
#             print("Loaded existing FAISS index.")
#         except Exception:
#             # If not found, create new
#             vectorstore = FAISS.from_documents([], embeddings)
#             print("Created new FAISS index.")

#         # Add new documents
#         vectorstore.add_documents(documents)
#     else:
#         vectorstore = FAISS.from_documents(documents, embeddings)

#     # this will overwrite the existing index if it exists
#     vectorstore.save_local(persist_directory)

#     print("FAISS vectorstore count:", len(vectorstore.index_to_docstore_id))


if __name__ == "__main__":

    print("Starting job scraping...")
    total_job_per_link = 5
    job_id_list = []

    linkedin_job_urls = linkedin_link_constructor(LINKEDIN_JOB_SEARCH_PARAMS)
    for target_url in linkedin_job_urls:
        print(f"Scraping from: {target_url}")
        _ls = get_job_ids(target_url, total_jobs=total_job_per_link)
        print(f"Found {len(_ls)} job IDs in this page.")
        [job_id_list.append(id) for id in _ls]  # type: ignore

    print(f"Found {len(list(set(job_id_list)))} unique job IDs.")

    job_df = get_job_data(
        list(set(job_id_list)),
        if_save=True,
        file_name="data/job_data/senior_data_scientist.csv",
        slow_down=True,
    )

    save_to_vectorestore(
        df=job_df,
        persist_directory=PERSIST_PATH,
        combine_list=COMBINE_LIST,
        metadata_list=METADATA_LIST,
        append_to_vectorestore=True,
    )
