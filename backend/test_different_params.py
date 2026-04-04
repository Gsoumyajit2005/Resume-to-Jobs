import asyncio
import pandas as pd
from jobspy import scrape_jobs

async def test_different():
    # Test with different parameters to get more varied results
    print("Testing with location specified...")
    try:
        df = scrape_jobs(
            site_name=["indeed", "linkedin", "zip_recruiter", "google"],
            search_term="software engineer",
            location="San Francisco, CA",
            results_wanted=20,
            hours_old=168,  # Last week
            country_indeed='usa',
        )
        
        print(f"Results with location: {len(df)} jobs")
        if not df.empty:
            print("\nSource distribution:")
            if 'site' in df.columns:
                source_counts = df['site'].value_counts()
                for source, count in source_counts.items():
                    print(f"  {source}: {count}")
            
            print("\nSample jobs:")
            for i, row in df.head(10).iterrows():
                title = row.get('title', 'N/A')
                company = row.get('company', 'N/A')
                site = row.get('site', 'N/A')
                location = row.get('location', 'N/A')
                print(f"  {site:12} | {title} at {company} ({location})")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*50)
    print("Testing with different search term...")
    try:
        df2 = scrape_jobs(
            site_name=["indeed", "linkedin", "zip_recruiter", "google"],
            search_term="developer",
            location=None,
            results_wanted=20,
            hours_old=168,
            country_indeed='usa',
        )
        
        print(f"Results with 'developer': {len(df2)} jobs")
        if not df2.empty:
            print("\nSource distribution:")
            if 'site' in df2.columns:
                source_counts = df2['site'].value_counts()
                for source, count in source_counts.items():
                    print(f"  {source}: {count}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_different())