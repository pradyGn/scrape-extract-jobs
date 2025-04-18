from abc import ABC, abstractmethod

class SCRAPER(ABC):
    """this class serves as a base class to build any SCRAPER.
    """

    @abstractmethod
    def __init__(self) -> None:
        """constructor for SCRAPER class.
        """

    @abstractmethod
    def folder_exists_or_mk(self, folder:str) -> bool:
        """check if the save folder exists.
        """

    @abstractmethod
    def scrape(self, browser_name:str, headless_browser:bool) -> None:
        """scrape method for a SCRAPER object
        """