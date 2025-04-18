import sys
sys.path.append('./')

from src.html_extractor.base_extractor import EXTRACTOR
import src.constants as c
import src.utils as u

import os
import json

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
)
from peft import PeftModel
from tqdm import tqdm
from pathlib import Path
import pandas as pd

class career_page_html_extractor(EXTRACTOR):
    """
    Extracts structured information from HTML content scraped from career pages using a fine-tuned small language model.
    
    This class handles model/tokenizer loading, HTML chunking, prompt construction, generation of predictions using 
    a PEFT (Parameter-Efficient Fine-Tuning) model, and saving of extracted content.

    Inherits:
        EXTRACTOR (Base class for language model extraction logic)

    Attributes:
        split_folder_path (str): Directory path where raw HTML files are stored (input).
        extracted_foler_path (str): Directory path to store extracted JSON/text outputs (output).
        model (transformers.PreTrainedModel): The fine-tuned language model used for inference.
        tokenizer (transformers.PreTrainedTokenizer): Tokenizer used to encode/decode prompts.
        old_extract_df (pd.DataFrame): Optional placeholder to hold older extractions (not yet in use).
    """

    def __init__(self, split_folder_path:str, extracted_foler_path:str):
        """
        Initializes the extractor with input/output folder paths.

        Args:
            split_folder_path (str): Folder containing raw HTML files split by company.
            extracted_foler_path (str): Folder where extracted outputs will be saved.
        """

        self.split_folder_path = split_folder_path
        self.extracted_foler_path = extracted_foler_path
        self.model = None
        self.tokenizer = None
        self.old_extract_df = None
    
    def make_folder(self, folder_path:str) -> None:
        """
        Creates the specified folder path.

        Args:
            folder_path (str): The directory path to create.
        """
        
        os.makedirs(folder_path, exist_ok=True)

    def folder_exists_or_mk(self, folder_path:str) -> None:
        """
        Checks if a folder exists and creates it if it doesn't.

        Args:
            folder_path (str): Path to check and create if necessary.
        """

        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            return
        self.make_folder(folder_path=folder_path)

    def data_software_contents(self, company_folder_path:str, data_software:str) -> (list[str] | list):
        """
        Lists all HTML files under a specific subdirectory for a given company and data or software sub-directory.

        Args:
            company_folder_path (str): Base directory for the company.
            data_software (str): Name of the data/software source or HTML subfolder.

        Returns:
            list[str] | list: List of filenames, or empty list if folder not found.
        """

        if data_software in os.listdir(company_folder_path):
            return os.listdir(Path(company_folder_path) / data_software)
        return []
    
    def find_substring(self, substring:str, _string_:str) -> list[int]:
        """
        Finds all positions of a substring within a string, returning start indices.

        Args:
            substring (str): Substring to search for.
            _string_ (str): Full string to search within.

        Returns:
            list[int]: List of starting indices where the substring is found.
        """

        split_string = _string_.split(substring)
        return_pos = []; offset = 0
        for s in split_string[:-1]:
            return_pos.append(len(s)+offset)
            offset += len(substring) + len(s)
        return return_pos
    
    def load_model(self):
        """
        Loads the base Hugging Face model and applies PEFT fine-tuning weights.

        The model is later used for HTML-to-structured-response generation.
        """

        base_model = AutoModelForCausalLM.from_pretrained(
            c.HF_MODEL,
            low_cpu_mem_usage=c.LOW_CPU_MEM_USAGE,
            return_dict=c.RETURN_DICT,
            torch_dtype=c.TORCH_DTYPE,
            device_map=c.DEVICE_MAP,
        )
        self.model = PeftModel.from_pretrained(
            base_model,
            c.TUNED_MODEL,
        )
        self.model = self.model.merge_and_unload()
        self.model = self.model.to(dtype=torch.float32)
    
    def load_tokenizer(self):
        """
        Loads the tokenizer corresponding to the base model, with special padding/token config.
        """

        self.tokenizer = AutoTokenizer.from_pretrained(
            c.HF_MODEL,
            trust_remote_code=c.TRUST_REMOTE_CODE,
            padding_side = c.PADDING_SIDE,
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "left"
    
    def initialize(self):
        """
        Initializes the model and tokenizer together.
        """

        self.load_model()
        self.load_tokenizer()

    def return_prompt(self, html_content:str):
        """
        Creates a prompt for the LLM using HTML content and a pre-defined template.

        Args:
            html_content (str): HTML snippet to include in the prompt.

        Returns:
            str: Formatted prompt to be passed to the model.
        """

        return c.EXTRACTOR_PROMPT.format(html_content)

    def make_predictions(self, input_ids):
        """
        Performs prediction using the loaded model and tokenizer.

        Args:
            input_ids (dict): Tokenized input prompt.

        Returns:
            str: Decoded text starting from '### Response:' marker.
        """

        input_ids.to("cuda")
        outputs = self.model.generate(**input_ids, max_new_tokens=c.MAX_NEW_TOKENS, pad_token_id=self.tokenizer.eos_token_id, temperature=c.TEMPERATURE)
        pred_output = self.tokenizer.decode(outputs[0])
        pred_response_start_pos = pred_output.find('### Response:')
        return pred_output[pred_response_start_pos:]

    def read_dict_from_content(self, content:str) -> list:
        """
        Attempts to parse a string into a list of dictionaries.

        Args:
            content (str): JSON-formatted string (ideally a list of dicts).

        Returns:
            list: Parsed list of dictionaries, or an empty list if parsing fails.
        """

        if content.startswith("[") and content.endswith("]") and len(content) > 10:
            try:
                data = json.loads(content)
                if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                    return data
            except json.JSONDecodeError:
                pass
        
        return []

    def call_make_predictions(self, company:str, data_software:str, html_file:str) -> list:
        """
        Performs the full prediction pipeline: reads HTML, checks if relevant,
        chunks by key token, runs generation, and saves the result.

        Args:
            company (str): Name of the company whose HTML is being processed.
            data_software (str): Subdirectory or identifier for the job data source.
            html_file (str): Filename of the raw HTML file to process.

        Returns:
            list: Currently returns an empty list (can be extended to return JSONs).
        """

        should_i_make_preds = True
        html_content = u.read_html(
            HTML_file_path = Path(self.split_folder_path) / company / data_software / html_file
        )
        if company in c.EXTRACTOR_CHECK and c.EXTRACTOR_CHECK[company] not in html_content:
            should_i_make_preds = False
        if should_i_make_preds:

            important_pos = self.find_substring(substring=c.EXTRACTOR_CHECK[company], _string_=html_content)
            for ix, pos in enumerate(important_pos):
                html_content_split = html_content[max(0, pos-c.EXTRACTOR_BUFFER):min(len(html_content), pos+c.EXTRACTOR_BUFFER)]

                input_prompt = self.return_prompt(html_content_split)
                input_ids = self.tokenizer(input_prompt, return_tensors="pt")
                if len(input_prompt) < 100_000:
                    # try:
                    pred_response = self.make_predictions(input_ids=input_ids)
                    self.folder_exists_or_mk(
                        folder_path = Path(self.extracted_foler_path) / company / data_software
                    )
                    u.save_response_as_txt(
                        save_location = Path(self.extracted_foler_path) / company / data_software / f"extracted_{html_file[:-4]}_part_{ix}.txt",
                        response = pred_response
                    )

        return []
    
    def produce_predicts(self):
        """
        Main method to process all HTML files across companies and subfolders.

        Iterates over all files, runs the prediction pipeline, and saves results.
        Handles both single-level and nested directory structures.
        """
        
        self.folder_exists_or_mk(folder_path = self.extracted_foler_path)
        company_list = os.listdir(self.split_folder_path); company_list.sort(); company_list_extracted = os.listdir(self.extracted_foler_path)
        for company in tqdm(company_list, desc="Extracted Companies"):
            if company not in company_list_extracted:
                for data_software in os.listdir(Path(self.split_folder_path) / company):
                    if os.path.isdir(Path(self.split_folder_path) / company / data_software):
                        data_software_html_paths = self.data_software_contents(
                            company_folder_path = Path(self.split_folder_path) / company,
                            data_software = data_software
                        )
                        data_software_html_paths.sort()
                        for html_file in data_software_html_paths:
                            self.call_make_predictions(
                                company = company,
                                data_software = data_software,
                                html_file = html_file
                            )

                    else:
                        self.call_make_predictions(
                            company = company,
                            data_software = "",
                            html_file = data_software
                        )

if __name__ == "__main__":
    """
    Use for testing the career_page_html_extractor class.
    """
    extractor = career_page_html_extractor(
        split_folder_path = c.SCRAPER_SAVE_FOLDER_PATH,
        extracted_foler_path = c.EXTACTED_FOLDER_PATH
    )
    extractor.initialize()
    extractor.produce_predicts()