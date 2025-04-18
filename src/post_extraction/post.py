import sys
sys.path.append('./')

from src.post_extraction.base_post import POST
import src.constants as c
import src.utils as u

import os
import json
import pandas as pd
from pathlib import Path



class post_extraction_cleaner(POST):
    """
    Handles post-processing of job data extracted from company career pages.

    This class reads the model-generated JSON files, converts them to a master DataFrame,
    cleans job titles, standardizes job locations, filters out old and non-U.S. listings, 
    and saves the results for downstream applications (e.g., frontend, database ingestion).

    Inherits:
        POST (Base class for post-extraction processing logic)

    Attributes:
        extracted_folder_path (str): Path to the directory containing extracted job JSONs.
        master_df_save_path (str): File path to save the cleaned master DataFrame.
        job_database_df_path (str): File path to save or append job records in the historical job database.
        job_database_df (pd.DataFrame | None): Loaded existing job database for deduplication.
        master_df (pd.DataFrame | None): The consolidated DataFrame built from extracted job data.
    """

    def __init__(self):
        """
        Initializes the post-extraction cleaner with all internal states set to None.
        """

        self.extracted_folder_path = None
        self.master_df_save_path = None
        self.job_database_df_path = None
        self.job_database_df = None
        self.master_df = None
    
    def initialize(self, extracted_folder_path, master_df_save_path, job_database_df_path):
        """
        Sets all internal file path references and optionally loads existing job database.

        Args:
            extracted_folder_path (str): Path to extracted job data.
            master_df_save_path (str): Path where the cleaned job listings will be saved.
            job_database_df_path (str): Path to existing job database (optional for deduplication).
        """
            
        self.extracted_folder_path = extracted_folder_path
        self.master_df_save_path = master_df_save_path
        self.job_database_df_path = job_database_df_path
        if os.path.exists(self.job_database_df_path):
            self.job_database_df = self.read_df_from_parquet(job_database_df_path)
    
    def make_folder(self, folder_path:str) -> None:
        """
        Creates a directory.

        Args:
            folder_path (str): Target directory path.
        """

        os.makedirs(folder_path, exist_ok=True)

    def folder_exists_or_mk(self, folder_path:str) -> None:
        """
        Checks if the directory exists and creates it if it does not.

        Args:
            folder_path (str): Path to check or create.
        """

        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            return
        self.make_folder(folder_path=folder_path)
    
    def read_txt(self, file_path:str) -> None:
        """
        Reads and strips the content of a `.txt` file.

        Args:
            file_path (str): Path to the text file.

        Returns:
            str: Cleaned text content.
        """
        
        with open(file_path, 'r') as file:
            return file.read().strip()
    
    def save_df_to_parquet(self, df, file_path:str) -> None:
        """
        Saves a DataFrame to a Parquet file, creating directories as needed.

        Args:
            df (pd.DataFrame): DataFrame to save.
            file_path (str): Output file path.
        """
        
        merged_path = Path(*file_path.parts[:-1])
        self.folder_exists_or_mk(folder_path = merged_path)
        df.to_parquet(file_path)
    
    def read_df_from_parquet(self, file_path: str) -> pd.DataFrame:
        """
        Loads a Parquet file into a pandas DataFrame.

        Args:
            file_path (str): Path to the Parquet file.

        Returns:
            pd.DataFrame: Loaded data.
        """

        return pd.read_parquet(file_path)

    def read_dict_from_txt(self, content:str, file_path:str) -> list:
        """
        Parses a string as a list of dictionaries if it appears to be valid JSON.

        Args:
            content (str): JSON string to parse.
            file_path (str): Path to the original file (for logging/debug, unused here).

        Returns:
            list: Parsed list of dictionaries, or an empty list on failure.
        """

        if content.startswith("[") and content.endswith("]") and len(content) > 10:
            try:
                data = json.loads(content)
                if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                    return data
            except json.JSONDecodeError:
                pass
        
        return []

    def process_file_read_txt(self, file_path:str) -> str:
        """
        Reads and cleans a text file by removing known start and end markers.

        Args:
            file_path (str): Path to the text file.

        Returns:
            str: Preprocessed content ready for JSON parsing.
        """

        content = self.read_txt(file_path)
        return content.replace(c.POST_START_TXT, "").replace(c.POST_END_TXT, "").replace("'", '"')

    def extract_json_to_df(self, file_path:str, company_name:str):
        """
        Converts one JSON file to a pandas DataFrame and appends it to the master DataFrame.

        Args:
            file_path (str): Path to the extracted file.
            company_name (str): Company associated with the extracted file.
        """

        processed_content = self.process_file_read_txt(file_path)
        cur_json = self.read_dict_from_txt(content=processed_content, file_path=file_path)
        cur_df = pd.DataFrame(cur_json)
        cur_df['company'] = company_name
        if self.master_df is not None:
            self.master_df = pd.concat([self.master_df, cur_df], ignore_index=True)
        else:
            self.master_df = cur_df
    
    def get_job_df(self):
        """
        Iterates over all extracted files and compiles a master DataFrame of job records.
        Handles both flat and nested directory structures.
        """

        for company in os.listdir(self.extracted_folder_path):
            for data_software in os.listdir(Path(self.extracted_folder_path) / company):
                if data_software == 'data' or data_software == 'software':
                    file_name_list = os.listdir(Path(self.extracted_folder_path) / company / data_software); file_name_list.sort()
                    for file_name in file_name_list:
                        # print(self.master_df)
                        self.extract_json_to_df(
                            file_path = Path(self.extracted_folder_path) / company / data_software / file_name,
                            company_name = company,
                        )
                else:
                    self.extract_json_to_df(
                        file_path = Path(self.extracted_folder_path) / company / data_software,
                        company_name = company,
                    )
    
    def process_master_df(self):
        """
        Cleans the master DataFrame by:
        - Dropping irrelevant columns.
        - Renaming columns
        - Dropping null or malformed job links
        - Appending URL prefixes if needed
        - Removing duplicates
        """

        self.master_df = self.master_df[["company", "Job Title", "Job Location", "Job ID", "Job Link"]]
        self.master_df = self.master_df[~pd.isna(self.master_df["Job Link"])].reset_index(drop=True).rename(columns={
            'Job ID': 'job_id',
            'Job Title': 'job_title',
            'company': 'company_name',
            'Job Link': 'job_link',
            'Job Location': 'location'
        })
        self.master_df = self.master_df.drop_duplicates().reset_index(drop=True)
        row_to_del = []
        for idx, r in self.master_df.iterrows():
            if r['job_link'] is not None and 'http' not in r['job_link']:
                if r['company_name'] in c.LINK_PREPEND:
                    self.master_df.loc[idx, 'job_link'] = f"{c.LINK_PREPEND[r['company_name']]}{r['job_link']}"
                else:
                    row_to_del.append(idx)
        self.master_df.drop(row_to_del, inplace=True)
    
    def clean_location_field(self):
        """
        Empties the location field for jobs not clearly marked as U.S.-based.
        """

        for ix, r in self.master_df.iterrows():
            change = True
            for keyword in c.UNITED_STATES_LIST:
                if keyword in  r["location"].lower():
                    change = False
            if change:
                self.master_df.iloc[ix, 2] = ""
    
    def location_check_helper(self, row:pd.DataFrame, location_mask:list) -> None:
        """
        Updates a boolean mask to exclude jobs with non-U.S. locations.

        Args:
            row (pd.DataFrame): A row in the job listing DataFrame.
            location_mask (list): The running mask to update.

        Returns:
            list: Updated mask list.
        """

        for country in c.COUNTRY_SET:
            if country in row["location"].lower():
                location_mask = location_mask[:-1]
                location_mask.append(False)
                return location_mask
        return location_mask
    
    def drop_non_us_jobs(self):
        """
        Drops all rows from `master_df` that have a location outside of the U.S.
        """
        
        location_mask = []
        for _, r in self.master_df.iterrows():
            location_mask.append(True)
            location_mask = self.location_check_helper(row= r, location_mask = location_mask)
        self.master_df = self.master_df[location_mask].reset_index(drop=True)

    def remove_old_n_irrelevant_roles(self):
        """
        Removes:
        - Roles containing 'technician' in the title
        - Job listings already present in the job database (deduplication)
        """

        self.master_df = self.master_df[~self.master_df['job_title'].str.contains('technician', case=False, na=False)]
        if self.job_database_df is not None:
            self.master_df = self.master_df[~self.master_df["job_link"].isin(self.job_database_df["job_link"])]
    
    def save_files(self):
        """
        Saves the cleaned `master_df` to disk and appends it to the job database if available.
        """

        self.save_df_to_parquet(self.master_df, self.master_df_save_path)
        if self.job_database_df is not None:
            self.job_database_df = pd.concat([self.job_database_df, self.master_df], ignore_index=True)
        else:
            self.job_database_df = self.master_df
        self.save_df_to_parquet(self.job_database_df, self.job_database_df_path)

    def initiate_post_process(self):
        """
        Full post-processing pipeline:
        - Loads extracted files
        - Cleans, filters, and deduplicates data
        - Saves outputs to disk for further use
        """
        
        self.get_job_df()
        self.process_master_df()
        self.remove_old_n_irrelevant_roles()
        self.drop_non_us_jobs()
        self.clean_location_field()
        self.save_files()
    
if __name__ == "__main__":
    """
    Use for testing the post_extraction_cleaner class.
    """
    timstamp = ""
    post_object = post_extraction_cleaner()
    post_object.initialize(
        extracted_folder_path = Path(c.EXTACTED_FOLDER_PATH) / timstamp,
        master_df_save_path = Path(c.FRONTEND_DATA_PATH) / timstamp / "extract.parquet",
        job_database_df_path = Path(c.FRONTEND_DATA_PATH) / "job_database.parquet",
        sql_table_save_path = Path(c.FRONTEND_DATA_PATH) / timstamp / f"job_listings_{timstamp}.sql",
        sql_table_save_folder = Path(c.FRONTEND_DATA_PATH) / timstamp,
    )
    post_object.initiate_post_process()

    

