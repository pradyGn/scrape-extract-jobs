from abc import ABC, abstractmethod
from typing import Dict

class POST(ABC):
    """this class serves as a base class to build any POST.
    """

    @abstractmethod
    def __init__(self, split_clean_folder_path:str, extracted_foler_path:str) -> None:
        """constructor for POST class.
        """

    @abstractmethod
    def folder_exists_or_mk(self, folder:str) -> bool:
        """check if the save folder exists.
        """

    @abstractmethod
    def save_df_to_parquet(self, save_folder_path:str) -> None:
        """method to save data frame for a POST object
        """

    @abstractmethod
    def read_df_from_parquet(self, save_folder_path:str) -> None:
        """method to read data frame for a POST object
        """
    
    @abstractmethod
    def read_txt(self, read_file_path:str) -> None:
        """method to read .txt for a POST object
        """