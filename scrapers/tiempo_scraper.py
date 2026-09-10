import requests
from requests.exceptions import HTTPError, RequestException
from bs4 import BeautifulSoup
import unicodedata


class Scraper2:
    """
    Scraper base para El Tiempo.

    Obtiene las noticias de una página y permite extraer:
    - titulares
    - descripciones
    - enlaces
    - fechas
    """

    def __init__(self, url, news_number=30):
        self.url = url
        self.news_number = news_number

        # La página se descargará una sola vez
        self.research = self.main_scraper()

    def main_scraper(self):
        """
        Descarga la página principal y obtiene los artículos.
        """

        try:
            print(f"Descargando: {self.url}")

            page = requests.get(
                self.url,
                timeout=30
            )

            print(f"Status HTTP: {page.status_code}")

            page.raise_for_status()

            # Usamos el parser incluido con Python.
            # No dependemos de lxml.
            datos = BeautifulSoup(
                page.text,
                'html.parser'
            )

            research = datos.find_all('article')

            print(f"Artículos encontrados: {len(research)}")

            return research

        except HTTPError as err:
            print(f"Error HTTP: {err}")
            return []

        except RequestException as err:
            print(f"Error de conexión: {err}")
            return []

        except Exception as err:
            print(f"Error inesperado: {err}")
            return []

    def _articles(self):
        """
        Devuelve solamente el número de artículos solicitado.
        """

        return self.research[:self.news_number]

    def header_scraper(self):
        """
        Extrae los titulares.
        """

        titulares = []

        for dato in self._articles():

            try:
                titular = dato.h2.a.get_text(strip=True)
                titulares.append(titular)

            except AttributeError:
                titulares.append("")

        return titulares

    def news_scraper(self):
        """
        Extrae el contenido de cada noticia.
        """

        cuerpo = []

        for dato in self._articles():

            try:
                enlace = dato.h2.a['href']

                respuesta = requests.get(
                    enlace,
                    timeout=30
                )

                respuesta.raise_for_status()

                news_datos = BeautifulSoup(
                    respuesta.text,
                    'html.parser'
                )

                contenido = news_datos.find(
                    'div',
                    attrs={
                        'class': (
                            'et_pb_module '
                            'et_pb_post_content '
                            'et_pb_post_content_0_tb_body'
                        )
                    }
                )

                if contenido is None:
                    cuerpo.append("")
                    continue

                news_text = contenido.get_text(
                    " ",
                    strip=True
                )

                news = unicodedata.normalize(
                    "NFKD",
                    news_text
                )

                cuerpo.append(news.strip())

            except (AttributeError, KeyError):
                cuerpo.append("")

            except RequestException as err:
                print(
                    f"Error obteniendo noticia: {err}"
                )
                cuerpo.append("")

        return cuerpo

    def link_scraper(self):
        """
        Extrae los enlaces de las noticias.
        """

        links = []

        for dato in self._articles():

            try:
                links.append(
                    dato.h2.a['href']
                )

            except (AttributeError, KeyError):
                links.append("")

        return links

    def date_scraper(self):
        """
        Extrae la fecha de publicación.
        """

        dia = []

        for dato in self._articles():

            try:
                dia.append(
                    dato.p.get_text(strip=True)
                )

            except AttributeError:
                dia.append("")

        return dia
