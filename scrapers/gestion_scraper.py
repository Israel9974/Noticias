import requests
from requests.exceptions import HTTPError, RequestException
from bs4 import BeautifulSoup
import json


class Scraper4:
    """
    Scraper auxiliar para Gestión.

    Obtiene:
    - titulares
    - contenido
    - enlaces
    - fechas
    """

    def __init__(self, url, news_number=20):
        self.url = url
        self.news_number = news_number

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/140.0 Safari/537.36"
            )
        }

        # Descargar la página UNA sola vez
        self.research = self.main_scraper()

    # ============================================================
    # PÁGINA PRINCIPAL
    # ============================================================

    def main_scraper(self):

        print(f"Descargando: {self.url}")

        try:

            page = requests.get(
                self.url,
                timeout=30,
                headers=self.headers
            )

            print(f"Status HTTP: {page.status_code}")

            page.raise_for_status()

            soup = BeautifulSoup(
                page.text,
                "html.parser"
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

        except HTTPError as error:

            print(
                f"Error HTTP Gestión: {error}"
            )

            return []

        except RequestException as error:

            print(
                f"Error de conexión Gestión: {error}"
            )

            return []

        except Exception as error:

            print(
                f"Error inesperado Gestión: {error}"
            )

            return []

    # ============================================================
    # ARTÍCULOS
    # ============================================================

    def _get_articles(self):

        return self.research[:self.news_number]

    # ============================================================
    # TITULARES
    # ============================================================

    def header_scraper(self):

        titulares = []

        articles = self._get_articles()

        for i, dato in enumerate(articles, start=1):

            try:

                titular = dato.h2.a.get_text(
                    strip=True
                )

                titulares.append(titular)

            except (AttributeError, TypeError):

                titulares.append("")

        return titulares

    # ============================================================
    # LINKS
    # ============================================================

    def link_scraper(self):

        links = []

        articles = self._get_articles()

        for dato in articles:

            try:

                href = dato.h2.a.get("href")

                if not href:
                    links.append("")
                    continue

                if href.startswith("http"):

                    enlace = href

                else:

                    enlace = (
                        "https://gestion.pe"
                        + href
                    )

                links.append(enlace)

            except (AttributeError, TypeError):

                links.append("")

        return links

    # ============================================================
    # JSON-LD
    # ============================================================

    def _get_json_ld(self, url):

        try:

            response = requests.get(
                url,
                timeout=30,
                headers=self.headers
            )

            response.raise_for_status()

            soup = BeautifulSoup(
                response.text,
                "html.parser"
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

                # ----------------------------------------------
                # JSON como diccionario
                # ----------------------------------------------

                if isinstance(data, dict):

                    yield data

                    # @graph
                    graph = data.get("@graph")

                    if isinstance(graph, list):

                        for item in graph:

                            if isinstance(item, dict):
                                yield item

                # ----------------------------------------------
                # JSON como lista
                # ----------------------------------------------

                elif isinstance(data, list):

                    for item in data:

                        if isinstance(item, dict):
                            yield item

        except Exception as error:

            print(
                f"Error obteniendo JSON-LD:"
                f" {error}"
            )

    # ============================================================
    # CONTENIDO
    # ============================================================

    def news_scraper(self):

        cuerpo = []

        links = self.link_scraper()

        total = len(links)

        for i, enlace in enumerate(
            links,
            start=1
        ):

            print(
                f"Extrayendo contenido Gestión "
                f"{i}/{total}..."
            )

            if not enlace:

                cuerpo.append("")
                continue

            descripcion = ""

            try:

                for data in self._get_json_ld(enlace):

                    # articleBody tiene prioridad
                    article_body = data.get(
                        "articleBody"
                    )

                    if article_body:

                        descripcion = str(
                            article_body
                        )

                        break

                    # description como respaldo
                    description = data.get(
                        "description"
                    )

                    if description:

                        descripcion = str(
                            description
                        )

                        break

            except Exception as error:

                print(
                    f"Error procesando contenido "
                    f"{i}: {error}"
                )

            cuerpo.append(
                descripcion.strip()
                if descripcion
                else ""
            )

        return cuerpo

    # ============================================================
    # FECHAS
    # ============================================================

    def date_scraper(self):

        fechas = []

        links = self.link_scraper()

        total = len(links)

        for i, enlace in enumerate(
            links,
            start=1
        ):

            print(
                f"Extrayendo fecha Gestión "
                f"{i}/{total}..."
            )

            if not enlace:

                fechas.append("")
                continue

            fecha = ""

            try:

                for data in self._get_json_ld(enlace):

                    date_published = data.get(
                        "datePublished"
                    )

                    if date_published:

                        fecha = str(
                            date_published
                        )

                        break

                    upload_date = data.get(
                        "uploadDate"
                    )

                    if upload_date:

                        fecha = str(
                            upload_date
                        )

                        break

            except Exception as error:

                print(
                    f"Error procesando fecha "
                    f"{i}: {error}"
                )

            fechas.append(fecha)

        return fechas
