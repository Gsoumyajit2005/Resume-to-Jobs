import asyncio
from scrapers.indeed import IndeedScraper

async def test():
    scraper = IndeedScraper()
    async with scraper as s:
        jobs = await s.search_jobs("Python developer", None, 10)
        print(f'Indeed found {len(jobs)} jobs')
        for job in jobs[:3]:
            print(f'  - {job["title"]} at {job["company"]}')

if __name__ == "__main__":
    asyncio.run(test())