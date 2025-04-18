from typing import Union, List

import json
import csv
import time
import random
from pathlib import Path

import src.constants as c

from playwright.async_api import async_playwright
import requests
import base64




def save_data_as_txt(save_location:str, data:list[str]) -> None:
    """
    Saves a list of strings to a plain text file, one item per line.

    Args:
        save_location (str): Full path where the text file will be saved.
        data (list[str]): A list of strings to be written to the file.

    Returns:
        None
    """

    with open(save_location, "w") as file:
        for i in range(len(data)):
            file.write(f"{data[i]}\n")

def save_response_as_txt(save_location:str, response:str) -> None:
    """
    Saves a single response string (e.g., from an HTTP request) to a plain text file.

    Args:
        save_location (str): Path to save the text file.
        response (str): The response content to save.

    Returns:
        None
    """

    with open(save_location, "w") as file:
        file.write(response)

def save_data_as_csv(save_location:str, extraction_fields:list[str], data:list[str]) -> None:
    """
    Saves a list of JSON strings as rows in a CSV file with specified headers.

    Args:
        save_location (str): Destination file path for the CSV.
        extraction_fields (list[str]): Header fields to use in the CSV file.
        data (list[str]): A list of JSON-formatted strings to be written as rows.

    Returns:
        None
    """

    with open(f"{save_location}", mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=extraction_fields)
        writer.writeheader()
        
        for dictionary_string in data:
            dictionary = json.loads(dictionary_string)
            writer.writerow(dictionary)

def save_html(save_location:str, html_data:str, encoding:str='utf-8') -> None:
    """
    Writes raw HTML content to a file.

    Args:
        save_location (str): Path to save the HTML file.
        html_data (str): The HTML content to write.
        encoding (str, optional): File encoding format. Defaults to 'utf-8'.

    Returns:
        None
    """

    with open(save_location, 'w', encoding=encoding) as f:
        f.write(html_data)

def read_html(HTML_file_path:str, encoding:str='utf-8') -> str:
    """
    Reads an HTML file and returns its content as a string.

    Args:
        HTML_file_path (str): Path to the HTML file.
        encoding (str, optional): Encoding format to use while reading. Defaults to 'utf-8'.

    Returns:
        str: The content of the HTML file.
    """
    
    with open(HTML_file_path, 'r', encoding=encoding) as file:
        return file.read()





##################################
#### SCRAPER Helper Functions ####
##################################

async def scrape_link_manu_wi_chromium(headless_browser:bool, base_url:str, page_identifier:str, num_pages:int, save_folder_path:str, multiplier:int) -> None:
    """
    Scrapes multiple pages by manipulating a paginated URL and saves each page’s HTML content.

    Args:
        headless_browser (bool): Whether to run the browser in headless mode.
        base_url (str): Base URL template with a placeholder for pagination.
        page_identifier (str): Identifier to locate the pagination point in the URL.
        num_pages (int): Number of pages to scrape.
        save_folder_path (str): Directory where HTML files will be saved.
        multiplier (int): Multiplier to control pagination logic.

    Returns:
        None
    """

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=headless_browser)
        context = await browser.new_context(java_script_enabled=True, ignore_https_errors=True)
        page = await context.new_page()

        for n in range(num_pages):
            try:
                time.sleep(random.randint(4, 8))
                base_url_ext = base_url.replace(f"{page_identifier}", f"{page_identifier}{n*multiplier if multiplier > 1 else n+1}")
                await page.goto(base_url_ext, wait_until='load')
                await page.wait_for_timeout(5000)
                html_to_save = await page.content()
                save_html(
                    save_location=f"{save_folder_path}{n}.txt",
                    html_data=html_to_save,
                )
            except:
                print(f"Error loading page {base_url_ext}")
        await context.close()
        await browser.close()

async def scrape_static_wi_chromium(headless_browser:bool, base_url:str, save_folder_path:str) -> None:
    """
    Loads a static web page using Chromium and saves the HTML content to a file.

    Args:
        headless_browser (bool): Whether to run the browser in headless mode.
        base_url (str): URL of the static page to scrape.
        save_folder_path (str): File path prefix to save the HTML file.

    Returns:
        None
    """

    async with async_playwright() as playwright:
        try:
            browser = await playwright.chromium.launch(headless=headless_browser)
            context = await browser.new_context(java_script_enabled=True)
            page = await context.new_page()
            await page.goto(base_url)
            await page.wait_for_timeout(20000)
            html_to_save = await page.content()
            save_html(
                save_location=f"{save_folder_path}.txt",
                html_data=html_to_save,
            )
            await context.close()
            await browser.close()
        except:
            print(f"Error loading page {base_url}")

async def scrape_scroll_wi_chromium(headless_browser:bool, base_url:str, save_folder_path:str) -> None:
    """
    Scrolls through a dynamically loaded web page to trigger lazy-loaded content, then saves the HTML.

    Args:
        headless_browser (bool): Whether to run the browser in headless mode.
        base_url (str): URL of the dynamic, scrollable page.
        save_folder_path (str): Path to save the HTML content.

    Returns:
        None
    """

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=headless_browser)
        context = await browser.new_context(java_script_enabled=True)
        page = await context.new_page()
        await page.goto(base_url, wait_until='load')
        time.sleep(random.randint(5, 7))
        try:
            for _ in range(100):
                await page.keyboard.press('Space')
                time.sleep(random.randint(2, 4))
            new_height = await page.evaluate("document.body.scrollHeight")

            time.sleep(random.randint(2, 5))
        except:
            print(f"Did not finish loading page {base_url}")
            keep_scrolling = False

        await page.wait_for_timeout(5000)
        html_to_save = await page.content()
        save_html(
            save_location=f"{save_folder_path}.txt",
            html_data=html_to_save,
        )
        await context.close()
        await browser.close()


def download_image(url, file_name):
    """
    Downloads an image from a URL and saves it to the specified file path.

    Args:
        url (str): Direct URL to the image.
        file_name (str): Destination file path to save the image.

    Returns:
        None
    """

    response = requests.get(url)
    if response.status_code == 200:
        with open(file_name, 'wb') as f:
            f.write(response.content)
    else:
        print(f"Failed to download image: {response.status_code}")

def encode_image(image_path):
    """
    Encodes an image file in Base64 format.

    Args:
        image_path (str): Path to the image file to encode.

    Returns:
        str: Base64-encoded string of the image.
    """
    
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')