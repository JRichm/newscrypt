import requests
from bs4 import BeautifulSoup


class Scraper:
    def __init__(self):
        pass

    def tmz(self, url):
        page = requests.get(url)
        soup = BeautifulSoup(page.text)

        body = soup.find('div', attrs={"class": "article__blocks"})
        sections = body.find_all("section", attrs={'class': "canvas-text-block"})

        text_items = []

        for section in sections:
            section_text = section.find_all("p")
            text_items.extend([i.text for i in section_text])

        full_text = " ".join(text_items)

        return full_text