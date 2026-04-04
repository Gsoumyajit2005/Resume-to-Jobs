from scrapers.jobspy_scraper import JobSpyScraper
import asyncio

async def test():
    async with JobSpyScraper() as scraper:
        jobs = await scraper.search_jobs('Python developer', 'San Francisco, CA', 3)
        print(f'Found {len(jobs)} jobs')
        for job in jobs[:2]:
            print(f'  - {job["title"]} at {job["company"]}')

asyncio.run(test())