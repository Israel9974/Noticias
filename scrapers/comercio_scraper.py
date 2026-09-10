import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
import json


class Scraper:
    """
    Scraper auxiliar para El Comercio.
    """

    def __init__(self, url, news_number):
        self.url = url
        self.news_number = news_number

    def main_scraper(self):

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

            page.raise_for_status()

            print(
                f"Status HTTP: {page.status_code}"
            )

        except HTTPError as http_err:

            print(
                f"Error HTTP: {http_err}"
            )

            return []

        except Exception as err:

            print(
                f"Error descargando El Comercio: {err}"
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
            f"Artículos encontrados: "
            f"{len(research)}"
        )

        return research

    def _get_articles(self):

        articles = self.main_scraper()

        return articles[:self.news_number]

    def header_scraper(self):

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

        links = []

        for dato in self._get_articles():

            try:

                href = dato.h2.a.get("href")

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

                except json.JSONDecodeError:

                    continue

                # Caso:
                # {"articleBody": "..."}
                if isinstance(data, dict):

                    if (
                        "articleBody" in data
                        or "datePublished" in data
                    ):
                        yield data

                    # @graph
                    if "@graph" in data:

                        for item in data["@graph"]:

                            if isinstance(
                                item,
                                dict
                            ):
                                yield item

                # Caso:
                # [{...}, {...}]
                elif isinstance(data, list):

                    for item in data:

                        if isinstance(
                            item,
                            dict
                        ):
                            yield item

        except Exception as e:

            print(
                f"Error obteniendo JSON-LD: {e}"
            )

    def news_scraper(self):

        cuerpo = []

        for enlace in self.link_scraper():

            if not enlace:

                cuerpo.append("")
                continue

            descripcion = ""

            for data in self._get_json_ld(enlace):

                if data.get("articleBody"):

                    descripcion = data[
                        "articleBody"
                    ]

                    break

                if data.get("description"):

                    descripcion = data[
                        "description"
                    ]

            cuerpo.append(
                descripcion.strip()
                if descripcion
                else ""
            )

        return cuerpo

    def date_scraper(self):

        fechas = []

        for enlace in self.link_scraper():

            if not enlace:

                fechas.append("")
                continue

            fecha = ""

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

        return fechas
