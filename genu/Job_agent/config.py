HEADERS: dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
}

## time formats, r86400: # last 24 hours, r604800: last 7 days, r2592000: last 30 days

LINKEDIN_JOB_SEARCH_PARAMS: list[dict[str, str | bool]] = [
    {
        "keywords": "senior data scientist",
        "location": "San Antonio",
        "f_TPR": "r604800",  # last 7 days
        "remote": False,
        "parttime": False,  # full-time
    },
    {
        "keywords": "senior data scientist",
        "location": "united states",
        "f_TPR": "r604800",  # last 7 days
        "remote": True,
        "parttime": False,  # full-time
    },
    {
        "keywords": "senior data scientist",
        "location": "united states",
        "f_TPR": "r604800",  # last 7 days
        "remote": True,
        "parttime": True,  # full-time
    },
]

PERSIST_PATH = "data/job_data/vectorstore_faiss"

COMBINE_LIST = [
    "title",
    "company",
    "salary_range",
    "description",
    "job_function",
    "industries",
]
METADATA_LIST = [
    "title",
    "company",
    "salary_range",
    "job_function",
    "industries",
    "level",
    "employment_type",
    "posted_time",
    "applicants",
    "job_id",
    "parsing_link",
    "job_posting_link",
    "date",
]
