LINKEDIN_JOB_SEARCH_URL: list[str] = [
    "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={}&location={}&start={}".format('senior%20data%20scientist', 'San%20Antonio', 0),  # remote
    "https://www.linkedin.com/jobs/search/?currentJobId=4220232511&f_TPR=r604800&geoId=90000724&keywords=senior%20data%20scientist&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true",  # onsite
    "https://www.linkedin.com/jobs/search/?currentJobId=4216706661&f_TPR=r604800&f_WT=2&geoId=103644278&keywords=senior%20data%20scientist&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true",  # remote
    "https://www.linkedin.com/jobs/search/?currentJobId=4223490501&distance=25&f_JT=P&f_WT=2&geoId=103644278&keywords=senior%20data%20scientist&origin=JOB_COLLECTION_PAGE_KEYWORD_HISTORY&refresh=true",   # part-time  
    "https://www.linkedin.com/jobs/search/?currentJobId=4216706661&f_TPR=r604800&f_WT=2&geoId=103644278&keywords=senior%20data%20scientist&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true"
]
HEADERS: dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
}
