import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
from datetime import datetime
import unicodedata


class Scraper2:
    """ Local package que permite obtener las etiquetas(html),
    titulares, descripciones y links de las noticias en el sitio """

    def __init__(self, url, news_number):
        self.url = url
        self.news_number = news_number

    def main_scraper(self):
        """
        Solicitud al servidor y obtención del html

        Return:
            Elementos html (etiquetas) de la clase que contiene la
            caja con la información necesaria.

        """
        try:
            page = requests.get(self.url)
            page.raise_for_status()
        except HTTPError as http_err:
            print(f'Un error ha ocurrido: {http_err}')
        except Exception as err:
            print(f'Un error ha ocurrido : {err}')
        else:
            datos = BeautifulSoup(page.text, 'lxml')
            research = datos.find_all('article')
            return research

    def header_scraper(self):
        """
        Extracción de los titulares.

        Return:
            Lista con titulares dependientes del
            número solicitado.

        """
        titulares = []
        try:
            for dato in self.main_scraper()[:self.news_number]:
                titulares.append(dato.h2.a.text)
                titulares = [elem.strip() for elem in titulares]
            return titulares
        except TypeError:
            pass

    def news_scraper(self):
        """
        Extracción de links de cada noticia.

        Return:
            Lista con links o urls de referencia.
        """
        cuerpo = []
        try:
            for dato in self.main_scraper()[:self.news_number]:
                enlace = dato.h2.a['href']
                ws_news = requests.get(enlace)
                news_datos = BeautifulSoup(ws_news.text, 'lxml')
                news_text = news_datos.find('div', attrs={'class':'et_pb_module et_pb_post_content et_pb_post_content_0_tb_body'}).text
                news = unicodedata.normalize("NFKD", news_text)
                cuerpo.append(news)
                cuerpo = [elem.strip() for elem in cuerpo]
            return cuerpo
        except TypeError:
            pass

    def link_scraper(self):
        """
        Extracción de links de cada noticia.

        Return:
            Lista con links o urls de referencia.
        """
        links = []
        try:
            for dato in self.main_scraper()[:self.news_number]:
                links.append(dato.h2.a['href'])
            return links
        except TypeError:
            pass

    def date_scraper(self):
        """
        Extracción del día de publicación de cada noticia.

        Return:
            Día de publicación de referencia.
        """
        dia = []
        try:
            for dato in self.main_scraper()[:self.news_number]:
                dia.append(dato.p.text)
            return dia
        except TypeError:
            pass
