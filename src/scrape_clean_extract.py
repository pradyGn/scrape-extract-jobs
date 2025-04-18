import sys
sys.path.append('./')

from src.scraper.scraper import career_page_scraper
from src.html_extractor.extractor import career_page_html_extractor
from src.post_extraction.post import post_extraction_cleaner
import src.constants as c

import asyncio
import argparse
from datetime import datetime
from pathlib import Path


"""
End-to-End Pipeline: Career Page Job Scraping, Extraction, and Post-Processing

Overview:
    This script performs a full pipeline run to scrape HTML from company career pages,
    extract structured job information using a fine-tuned language model, clean the
    results and merge into a master dataset.

Steps:
    1. Scraping:
        - Loads scraping metadata from config.
        - Scrapes each company's job page using Playwright and Chromium.
        - Saves raw HTML files in a timestamped folder.

    2. HTML Extraction:
        - Loads a fine-tuned LLM and tokenizer.
        - Converts HTML files into structured JSON output (e.g., job title, location, link).
        - Saves responses into a timestamped "extracted" directory.

    3. Post-Processing:
        - Reads extracted JSONs into a master DataFrame.
        - Cleans and deduplicates job listings.
        - Filters for U.S.-based jobs and removes irrelevant titles.
        - Saves cleaned outputs to a timestamped folder and appends to historical database.

Usage:
    Run from terminal:
        python run_pipeline.py --timestamp "2025-04-17_14:30:00"

Arguments:
    --timestamp (str, optional): Custom timestamp for folder versioning. 
                                 Defaults to current datetime formatted as `YYYY-MM-DD_HH:MM:SS`.

Notes:
    - All file/folder locations are defined in `src/constants.py`.
    - Assumes model weights, tokenizer, and PEFT adapter are available locally or from Hugging Face.

Author:
    MLOps Engineering Team
"""



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--timestamp",
        default=datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(" ", "_"),
        help="Pass a timestamp."
    )
    args = parser.parse_args()
    timestamp_str = args.timestamp

    scraper = career_page_scraper()
    scraper.load_scraping_info(file_path=c.SCRAPER_INFO_FILE_PATH)
    asyncio.run(
        scraper.scrape(browser_name=c.SCRAPER_BROWSER, headless_browser=False, save_folder_path=Path(c.SCRAPER_SAVE_FOLDER_PATH) / timestamp_str)
    )
    print("Finished scraping data.")

    extractor = career_page_html_extractor(
        split_folder_path = Path(c.SCRAPER_SAVE_FOLDER_PATH) / timestamp_str,
        extracted_foler_path = Path(c.EXTACTED_FOLDER_PATH) / timestamp_str,
    )
    extractor.initialize()
    extractor.produce_predicts()

    post_object = post_extraction_cleaner()
    post_object.initialize(
        extracted_folder_path = Path(c.EXTACTED_FOLDER_PATH) / timestamp_str,
        master_df_save_path = Path(c.FRONTEND_DATA_PATH) / timestamp_str / c.MASTER_DF_FILE_NAME,
        job_database_df_path = Path(c.FRONTEND_DATA_PATH) / c.OLD_JOB_DATABASE_FILE_NAME,
    )
    post_object.initiate_post_process()