import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from typing import List, Dict
from excel_saver import save_orders_to_excel

HC_URL = 'https://freelance.habr.com/tasks?q=django&categories=development_backend'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}


class JobCard(ABC):
    @property
    @abstractmethod
    def title_selector(self):
        pass

    @property
    @abstractmethod
    def url_selector(self):
        pass

    @property
    @abstractmethod
    def tags_selector(self):
        pass

    def __init__(self, tag: BeautifulSoup):
        self.tag = tag

    def get_title(self) -> str:
        title_tag = self.tag.select_one(self.title_selector)
        return title_tag.text.strip() if title_tag else None

    def get_url(self) -> str:
        url_tag = self.tag.select_one(self.url_selector)
        if url_tag and url_tag.has_attr('href'):
            href = url_tag['href']
            return href if href.startswith('http') else f'https://freelance.habr.com{href}'
        return None

    def get_tags(self) -> str:
        tags = self.tag.select(self.tags_selector)
        return ', '.join([tag.text.strip() for tag in tags]) if tags else None


class HabrJobCard(JobCard):
    title_selector = '.task__title a'
    url_selector = '.task__title a'
    tags_selector = '.tags a'


class Page(ABC):
    @property
    @abstractmethod
    def card_selector(self):
        pass

    @property
    @abstractmethod
    def card_class(self):
        pass

    def __init__(self, url: str):
        self.url = url
        self.soup = None

    def fetch(self):
        response = requests.get(self.url, headers=HEADERS)
        if response.status_code == 200:
            self.soup = BeautifulSoup(response.text, 'html.parser')
        else:
            raise Exception(f'Ошибка при запросе страницы: {response.status_code}')

    def get_orders(self) -> List[Dict[str, str]]:
        if not self.soup:
            self.fetch()
        order_tags = self.soup.select(self.card_selector)
        orders = []
        for tag in order_tags:
            card = self.card_class(tag)
            title = card.get_title()
            url = card.get_url()
            tags = card.get_tags()
            if title and url:
                orders.append({
                    'Title': title,
                    'URL': url,
                    'Tags': tags if tags else ''
                })
        return orders


class HabrPage(Page):
    card_selector = '.content-list__item'
    card_class = HabrJobCard


if __name__ == '__main__':
    habr_page = HabrPage(HC_URL)
    orders = habr_page.get_orders()
    save_orders_to_excel(orders, 'orders.xlsx')


