import requests
from requests.exceptions import HTTPError, RequestException
from bs4 import BeautifulSoup
import json


class Scraper:
    """
    Scraper auxiliar para El Comercio.

    Obtiene:
    - titulares
    - enlaces
    - contenido
    - fechas
    """

    def __init__(self, url, news_number=20):

        self.url = url
        self.news_number = news_number

        # La página principal se descarga solamente una vez
        self.research = self.main_scraper()


    def main_scraper(self):
        """
        Descarga la página principal de El Comercio
        y obtiene los bloques de noticias.
        """

        print(f"Descargando: {self.url}")

        try:

            page = requests.get(
                self.url,
                timeout=30,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 "
                        "(Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 "
                        "(KHTML, like Gecko) "
                        "Chrome/140.0 Safari/537.36"
                    )
                }
            )

            print(
                f"Status HTTP: {page.status_code}"
            )

            page.raise_for_status()

        except HTTPError as error:

            print(
                f"Error HTTP en El Comercio: {error}"
            )

            return []

        except RequestException as error:

            print(
                f"Error de conexión en El Comercio: {error}"
            )

            return []

        except Exception as error:

            print(
                f"Error descargando El Comercio: {error}"
            )

            return []

        soup = BeautifulSoup(
            page.text,
            "lxml"
        )

        research = soup.find_all(
            "div",
            class_="story-item__information-box w-full"
        )

        print(
            f"Artículos encontrados: {len(research)}"
        )

        return research


    def _get_articles(self):
        """
        Devuelve solamente la cantidad de artículos
        solicitada.
        """

        return self.research[:self.news_number]


    def header_scraper(self):
        """
        Extrae los titulares.
        """

        titulares = []

        for dato in self._get_articles():

            try:

                titular = dato.h2.a.get_text(
                    strip=True
                )

                titulares.append(titular)

            except AttributeError:

                titulares.append("")

        return titulares


    def link_scraper(self):
        """
        Extrae los enlaces.
        """

        links = []

        for dato in self._get_articles():

            try:

                href = dato.h2.a.get("href")

                if not href:
                    links.append("")
                    continue

                if href.startswith("http"):

                    enlace = href

                else:

                    enlace = (
                        "https://elcomercio.pe"
                        + href
                    )

                links.append(enlace)

            except AttributeError:

                links.append("")

        return links


    def _get_json_ld(self, url):
        """
        Obtiene información JSON-LD de una noticia.
        """

        if not url:
            return

        try:

            response = requests.get(
                url,
                timeout=30,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 "
                        "(Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 "
                        "(KHTML, like Gecko) "
                        "Chrome/140.0 Safari/537.36"
                    )
                }
            )

            response.raise_for_status()

            soup = BeautifulSoup(
                response.text,
                "lxml"
            )

            scripts = soup.find_all(
                "script",
                type="application/ld+json"
            )

            for script in scripts:

                if not script.string:
                    continue

                try:

                    data = json.loads(
                        script.string,
                        strict=False
                    )

                except (
                    json.JSONDecodeError,
                    TypeError
                ):

                    continue

                # ------------------------------------------
                # JSON-LD como diccionario
                # ------------------------------------------

                if isinstance(data, dict):

                    # Noticia directamente
                    if (
                        "articleBody" in data
                        or "datePublished" in data
                        or "description" in data
                    ):

                        yield data

                    # JSON-LD usando @graph
                    if "@graph" in data:

                        graph = data["@graph"]

                        if isinstance(graph, list):

                            for item in graph:

                                if isinstance(
                                    item,
                                    dict
                                ):

                                    yield item

                # ------------------------------------------
                # JSON-LD como lista
                # ------------------------------------------

                elif isinstance(data, list):

                    for item in data:

                        if isinstance(
                            item,
                            dict
                        ):

                            yield item

        except RequestException as error:

            print(
                f"Error obteniendo noticia "
                f"desde El Comercio: {error}"
            )

        except Exception as error:

            print(
                f"Error procesando JSON-LD: {error}"
            )


    def news_scraper(self):
        """
        Extrae el contenido de cada noticia.
        """

        cuerpo = []

        links = self.link_scraper()

        for enlace in links:

            if not enlace:

                cuerpo.append("")
                continue

            descripcion = ""

            try:

                for data in self._get_json_ld(enlace):

                    # Preferimos articleBody
                    if data.get("articleBody"):

                        descripcion = data[
                            "articleBody"
                        ]

                        break

                    # Si no existe articleBody,
                    # utilizamos description
                    if data.get("description"):

                        descripcion = data[
                            "description"
                        ]

                if descripcion:

                    descripcion = str(
                        descripcion
                    ).strip()

                cuerpo.append(
                    descripcion
                )

            except Exception as error:

                print(
                    f"Error extrayendo contenido: "
                    f"{error}"
                )

                cuerpo.append("")

        return cuerpo


    def date_scraper(self):
        """
        Extrae la fecha de publicación.
        """

        fechas = []

        links = self.link_scraper()

        for enlace in links:

            if not enlace:

                fechas.append("")
                continue

            fecha = ""

            try:

                for data in self._get_json_ld(enlace):

                    if data.get("datePublished"):

                        fecha = data[
                            "datePublished"
                        ]

                        break

                    if data.get("uploadDate"):

                        fecha = data[
                            "uploadDate"
                        ]

                        break

                fechas.append(fecha)

            except Exception as error:

                print(
                    f"Error extrayendo fecha: "
                    f"{error}"
                )

                fechas.append("")

        return fechas
