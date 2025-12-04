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
    

    def abc(self, url):
        pass


    def nbc(self, url):
        pass


    def cbs(self, url):
        pass


    def live_science(self, url):
        pass


    def variety(self, url):
        pass


    def the_washington_post(self, url):
        pass


    def associated_press(self, url):
        pass


    def _9to5mac(self, url):
        pass