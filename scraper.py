import re
import requests
from bs4 import BeautifulSoup

class ScraperManager:

    def __init__(self, product_id:str, fetching_mode:bool):
        self.__product_id = product_id
        self.initiateScrapers()
        self.scraper = self.getScraper(fetching_mode)

    def initiateScrapers(self):
        # To add new scrapers in future
        self.scrapers = { 0: OpenLibrary_Scraper,
                          1: RapidAPI_Scraper}

    def getScraper(self, fetching_mode):
        return self.scrapers[int(fetching_mode)]

    def scrape(self) -> dict:
       return self.scraper(self.__product_id).scrape()

# this link helped me understand Python OOP
# https://realpython.com/inheritance-composition-python
#
# ------------  Scraper ---------------
from abc import ABC, abstractmethod

class Scraper(ABC):

    def __init__(self, product_id:str, api_url:str, api_header:str):
        self._product_id = product_id
        self._API_url = api_url
        self._API_header = api_header

    @abstractmethod
    def getHeader(self) -> dict:
        pass
    @abstractmethod
    def scrape(self) -> list:
        pass
    @abstractmethod
    def getInfo(self, response_dic) -> dict:
        pass


# ------------ Rapid API ---------------

class RapidAPI_Scraper(Scraper):

    def __init__(self, product_id:str):
        api_url = "https://real-time-amazon-data.p.rapidapi.com/product-details"
        api_header = self.getHeader()
        super().__init__(product_id, api_url, api_header)
        self.__API_querystring =  {"asin":product_id, "country":"US"}

    def getHeader(self) -> dict:
        header = {
            "X-RapidAPI-Key": "fee06485b7msh71bce4efbc66d0bp1f9804jsnaad598cf1c16",
            "X-RapidAPI-Host": "real-time-amazon-data.p.rapidapi.com"
            }
        return header

    def scrape(self) -> list:
        response = requests.get(url=self._API_url, 
                                headers=self._API_header, 
                                params=self.__API_querystring)
        response_dic = response.json()
        fetched_info = self.getInfo(response_dic)
        return fetched_info

    def getInfo(self, response_dic) -> dict:
        product_title = None
        product_by = None
        product_category = None
        product_sub_category = None
        product_description = None
        publisher = None
        year_of_publication = None
        num_pages = None
        book_language = None
        product_img_link = None

        product_title = response_dic['data']['product_title']
        try:
            # Get Book info from Amazon
            product_by = response_dic['data']['book_author_name']
            product_category = response_dic['data']['category_path'][-2]['name']
            product_sub_category = response_dic['data']['category_path'][-1]['name']
            product_description = response_dic['data']['product_description']
            # Get img link 
            product_img_link = response_dic['data']['product_photo']
            publisher = response_dic['data']['product_information']['Publisher'].split(' (')[0].replace(';','')
            year_of_publication = re.findall(r'[0-9]{4}',response_dic['data']['book_publication_date'])[-1]
            for product_feature in response_dic['data']['product_information']:
                if product_feature in ['Paperback', 'Mass Market Paperback', 'Hardcover', 'School Library Binding']:
                    num_pages = response_dic['data']['product_information'][product_feature].split(' ')[0]

            book_language = response_dic['data']['product_information']['Language']
        except (AttributeError, IndexError, KeyError) as erorr_msg:
            print(erorr_msg)
            pass

        print(f'Fetched {self._product_id}, {year_of_publication}, {num_pages}, ...')

        return [self._product_id, product_title, product_by, product_category, product_sub_category, product_description
                                                    , publisher,year_of_publication,book_language,num_pages, product_img_link]

# ---------------- Open Library Scraper --------------------

class OpenLibrary_Scraper(Scraper):
    
    def __init__(self, product_id:str):
        api_url = "https://openlibrary.org/isbn/" + product_id
        api_header = self.getHeader()
        super().__init__(product_id, api_url, api_header)

    def getHeader(self):
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                    (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0'
        accept = "*/*"
        accept_en = "gzip, deflate, br, zstd"
        accept_lan = "en-US,en;q=0.9,ar;q=0.8"
        cache_con = "max-age=0"

        header = {'accept': accept, \
                        'accept-encoding': accept_en, \
                        'accept-language': accept_lan, \
                        'cache-control': cache_con, \
                        'user-agent': user_agent,}
        return header
    
    def scrape(self):
        source_code = requests.get(self._API_url, headers=self._API_header)
        plain_text = source_code.text
        html = BeautifulSoup(plain_text, 'html.parser')
        fetched_info = self.getInfo(html)
        return fetched_info
        
    def getInfo(self, html) -> dict:
        product_title = None
        product_by = None
        product_category = None
        product_sub_category = None
        product_description = None
        publisher = None
        year_of_publication = None
        num_pages = None
        book_language = None
        product_img_link = None
        try:
            product_title = html.select('.work-title')[0].text
        except Exception as e:
            raise AttributeError
            print(erorr_msg)

        try:
            # Get Book info from Amazon
            product_by = html.select('.edition-byline')[0].get_text(strip=True)[2:]
            category_list = html.find_all('a', attrs={'data-ol-link-track': 'BookOverview|SubjectClick'})
            category_list = [str(x).split('>')[1].replace('</a','') for x in category_list]
            if len(category_list) > 0:
                product_category = category_list[0]
                product_sub_category = category_list[-1]
            try:
                product_description = html.select('.read-more__content')[0].get_text(strip=True)
            except (AttributeError, IndexError) as erorr_msg:
                product_description = None
                print(erorr_msg)
            # Get img link 
            product_img_link = 'http:'+str(html.select('.cover')[0]).split('src="')[1].split('"')[0]
            publisher = html.find_all('a', attrs={'itemprop': 'publisher'})[0].text
            publication_year_info = html.find_all('span', attrs={'itemprop': 'datePublished'})[0]
            year_of_publication = re.findall(r'[0-9]{4}',publication_year_info.text)[0]
            num_pages = html.find_all('span', attrs={'itemprop': 'numberOfPages'})[0].text
            book_language = book_language = html.find_all('span', attrs={'itemprop': 'inLanguage'})[0].text
            
        except (AttributeError, IndexError, KeyError) as erorr_msg:
            print(erorr_msg)
            pass

        print(f'Fetched {self._product_id}, {year_of_publication}, {num_pages}, ...')

        return [self._product_id, product_title, product_by, product_category, product_sub_category, product_description
                                                    , publisher,year_of_publication,book_language,num_pages, product_img_link]