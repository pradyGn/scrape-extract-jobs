import sys
sys.path.append('./')

import os

import src.utils as u
import src.constants as c
from src.scraper.base_scraper import SCRAPER

import asyncio
import pandas as pd

class career_page_scraper(SCRAPER):
    """
    A web scraping utility class designed to automate scraping of HTML from 
    various company career pages. Inherits from the base `SCRAPER` class and supports 
    scraping static, scroll-based, and paginated web pages using Playwright with Chromium.

    Inherits:
        SCRAPER (Base class for scraping logic)

    Attributes:
        scraping_info_df (pd.DataFrame): DataFrame loaded from configuration CSV that contains
            scraping metadata for each company (e.g., URL, pagination type, identifier).
    """

    def __init__(self) -> None:
        """
        Initializes the career page scraper object with an empty configuration state.
        """

        self.scraping_info_df = None
    
    def make_folder(self, folder_path:str) -> None:
        """
        Creates a new directory at the specified path.

        Args:
            folder_path (str): Path where the new folder should be created.

        Returns:
            None
        """

        os.makedirs(folder_path, exist_ok=True)
    
    def folder_exists_or_mk(self, folder_path:str) -> None:
        """
        Checks whether the specified folder path exists. If not, creates it.

        Args:
            folder_path (str): Directory path to validate or create.

        Returns:
            None
        """

        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            return
        self.make_folder(folder_path=folder_path)
    
    def load_scraping_info(self, file_path:str) -> None:
        """
        Loads the scraping configuration from a CSV file into a DataFrame. The file
        should include details such as company name, URL, pagination style, and link type.

        Args:
            file_path (str): Path to the CSV file containing scraping metadata.

        Returns:
            None
        """

        self.scraping_info_df = pd.read_csv(file_path)
    
    async def call_scrape_link_manu_wi_chromium(self, headless_browser:bool, r:any, folder_path:str) -> None:
        """
        Wrapper to call the paginated scraper function using Chromium for a given row of scraping metadata.

        Args:
            headless_browser (bool): Whether to launch the browser in headless mode.
            r (any): A row (typically a pandas Series) from the scraping metadata DataFrame.
            folder_path (str): Directory where the scraped HTML pages will be saved.

        Returns:
            None
        """

        await u.scrape_link_manu_wi_chromium(
            headless_browser = headless_browser,
            base_url = r['link'],
            page_identifier = r['page_identifier'],
            num_pages = int(r['num_pages']),
            save_folder_path = folder_path,
            multiplier = int(r['mulriplier'])
        )
    
    async def call_scrape_static_wi_chromium(self, headless_browser:bool, r:any, folder_path:str) -> None:

        """
        Wrapper to call the static page scraper function using Chromium for a given row of scraping metadata.

        Args:
            headless_browser (bool): Whether to launch the browser in headless mode.
            r (any): A row (typically a pandas Series) from the scraping metadata DataFrame.
            folder_path (str): Directory where the scraped HTML content will be saved.

        Returns:
            None
        """

        await u.scrape_static_wi_chromium(
            headless_browser = headless_browser,
            base_url = r['link'],
            save_folder_path = folder_path,
        )
    
    async def scrape(self, browser_name:str, headless_browser:bool, save_folder_path:str) -> None:
        """
        Main orchestration method to run the scraping pipeline. It iterates over all configured
        companies and selects the appropriate scraping strategy based on metadata (scrolling, static, or paginated).

        Args:
            browser_name (str): Name of the browser to use (currently only 'chromium' is supported).
            headless_browser (bool): Whether to run the browser in headless mode.
            save_folder_path (str): Root directory where all scraping results will be saved.

        Returns:
            None
        """

        if browser_name == "chromium":

            for _, r in self.scraping_info_df.iterrows():
                print(f"Starting to scrape {r['company']}...")
                if r['link_identifier'] == 'scroll':
                    folder_path = f"{save_folder_path}/{r['company']}/{r['link_type']}/"
                    self.folder_exists_or_mk(folder_path=folder_path)
                    await u.scrape_scroll_wi_chromium(
                        headless_browser = headless_browser,
                        base_url = r['link'],
                        save_folder_path = f"{save_folder_path}/{r['company']}/{r['link_type']}/"
                    )
                
                elif pd.isna(r['link_type']):
                    folder_path = f"{save_folder_path}/{r['company']}/"
                    self.folder_exists_or_mk(folder_path=folder_path)
                    
                    await self.call_scrape_static_wi_chromium(
                        headless_browser = headless_browser,
                        r = r,
                        folder_path = folder_path
                    )
                else:
                    folder_path = f"{save_folder_path}/{r['company']}/{r['link_type']}/"
                    self.folder_exists_or_mk(folder_path=folder_path)
                    
                    await self.call_scrape_link_manu_wi_chromium(
                        headless_browser = headless_browser,
                        r = r,
                        folder_path = folder_path
                    )

        else:
            """TODO: build integration for other browsers too.
            """
            pass
    

if __name__ == "__main__":
    """
    Use for testing the career_page_scraper class.
    """
    scraper_obj = career_page_scraper()
    scraper_obj.load_scraping_info(file_path=c.SCRAPER_INFO_FILE_PATH)
    asyncio.run(
        scraper_obj.scrape(browser_name=c.SCRAPER_BROWSER, headless_browser=False, save_folder_path=c.SCRAPER_SAVE_FOLDER_PATH)
    )

