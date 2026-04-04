import asyncio
from scrapers.remoteok import RemoteOKScraper

async def test():
    scraper = RemoteOKScraper()
    async with scraper as s:
        jobs = await s.search_jobs("Python developer", None, 10)
        print(f'RemoteOK found {len(jobs)} jobs')
        for job in jobs[:3]:
            print(f'  - {job["title"]} at {job["company"]}')

if __name__ == "__main__":
    asyncio.run(test())