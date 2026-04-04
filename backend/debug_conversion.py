import asyncio
import pandas as pd
from datetime import datetime
from scrapers.jobspy_scraper import JobSpyScraper
from schemas.job import JobListing

async def test_conversion():
    # Test the conversion process directly
    scraper = JobSpyScraper()
    
    # Get raw data from jobspy
    df = await scraper._scrape_jobs_sync("software engineer", None, 10)
    
    if df is not None and not df.empty:
        print(f"Raw DataFrame shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        print(f"Source distribution:")
        if 'site' in df.columns:
            source_counts = df['site'].value_counts()
            for source, count in source_counts.items():
                print(f"  {source}: {count}")
        
        print("\nTesting conversion of first few rows:")
        for i, row in df.head(5).iterrows():
            print(f"\nRow {i}:")
            print(f"  site: {row.get('site')}")
            print(f"  title: {row.get('title')}")
            print(f"  company: {row.get('company')}")
            print(f"  location: {row.get('location')}")
            print(f"  date_posted: {row.get('date_posted')} (type: {type(row.get('date_posted'))})")
            
            try:
                job_dict = scraper._convert_jobspy_row_to_dict(row)
                if job_dict:
                    print(f"  Converted successfully:")
                    print(f"    id: {job_dict.get('id')}")
                    print(f"    title: {job_dict.get('title')}")
                    print(f"    company: {job_dict.get('company')}")
                    print(f"    location: {job_dict.get('location')}")
                    print(f"    source: {job_dict.get('source')}")
                    print(f"    posted_date: {job_dict.get('posted_date')}")
                else:
                    print(f"  Conversion returned None")
            except Exception as e:
                print(f"  Conversion failed: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_conversion())