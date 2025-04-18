from abc import ABC, abstractmethod
from typing import Dict

class EXTRACTOR(ABC):
    """this class serves as a base class to build any EXTRACTOR.
    """

    @abstractmethod
    def __init__(self, split_clean_folder_path:str, extracted_foler_path:str) -> None:
        """constructor for EXTRACTOR class.
        """

    @abstractmethod
    def folder_exists_or_mk(self, folder:str) -> bool:
        """check if the save folder exists.
        """