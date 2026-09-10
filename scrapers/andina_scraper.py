import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
import unicodedata
import json
import re

class Scraper8:
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
            research = datos.find_all('h3',
                                      class_='col s6 m12 l12 xl12 underline truncate3')
            research = ["https://andina.pe/agencia/" + item.find("a")["href"] for item in research]
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
                cabeza = requests.get(dato)
                soup = BeautifulSoup(cabeza.text, 'html.parser')

                titular = []
                capturar = False

                for node in soup.find_all(string=True):               
                    if "TITULO" in node:
                        capturar = True
                        continue

                    if "BAJADA" in node:
                        break

                    if capturar:
                        txt = node.strip()
                        if txt:
                            titular.append(txt)

                titular2 = " ".join(titular)
                titular2 = re.sub(r'\s+', ' ', titular2)
                titular2 = re.sub(r'\. ', '.\n\n', titular2)

                titulares.append(titular2)
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
                ws_news = requests.get(dato)
                soup = BeautifulSoup(ws_news.text, 'html.parser')

                contenido = []
                capturar = False

                for node in soup.find_all(string=True):               
                    if "CONTENIDO DE LA NOTICIA" in node:
                        capturar = True
                        continue

                    if "(FIN)" in node:
                        break

                    if capturar:
                        txt = node.strip()
                        if txt:
                            contenido.append(txt)

                news = " ".join(contenido)
                news = re.sub(r'\s+', ' ', news)
                news = re.sub(r'\. ', '.\n\n', news)

                cuerpo.append(news)
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
                links.append(dato)
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
                date = requests.get(dato)
                soup = BeautifulSoup(date.text, 'html.parser')

                nodo = soup.find(string=lambda t: "Publicado:" in t)

                if nodo:
                    m = re.search(r'Publicado:\s*([0-9/]+)', nodo)
                    if m:
                        dia.append(m.group(1))

            return dia
        except TypeError:
            pass