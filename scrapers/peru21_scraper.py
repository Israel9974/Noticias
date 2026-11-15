import json
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException


BASE_URL = "https://peru21.pe"


class Scraper3:
    """
    Scraper auxiliar para Perú 21.

    Obtiene:
    - titulares
    - enlaces
    - fechas
    - contenido

    Perú 21 pertenece al mismo grupo que El Comercio y Gestión,
    así que se usa el mismo selector de listado y el mismo método
    para fechas y contenido (JSON-LD de cada nota).
    Si el selector principal no encuentra nada, se usa uno
    alternativo basado en los titulares (h2 / h3).
    """

    def __init__(self, url, news_number=20):

        self.url = url
        self.news_number = news_number

        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/140.0 Safari/537.36"
            ),
            "Accept-Language": "es-PE,es;q=0.9"
        })

        # Cada nota se descarga UNA sola vez
        # (fecha y contenido salen de la misma descarga)
        self._cache = {}

        # Lista de tuplas (titular, link)
        self.items = self.main_scraper()

    # ============================================================
    # PÁGINA PRINCIPAL
    # ============================================================

    def main_scraper(self):

        print(f"Descargando: {self.url}")

        try:

            page = self.session.get(
                self.url,
                timeout=30
            )

            print(f"Status HTTP: {page.status_code}")

            page.raise_for_status()

        except RequestException as error:

            print(f"Error de conexión Perú 21: {error}")

            return []

        soup = BeautifulSoup(
            page.text,
            "html.parser"
        )

        # --------------------------------------------------------
        # Selector principal (mismo que Gestión / El Comercio)
        # --------------------------------------------------------

        anchors = []

        for caja in soup.select(
            "div.story-item__information-box"
        ):

            anchors.append(
                caja.select_one("h2 a, h3 a")
            )

        items = self._armar_items(anchors)

        # --------------------------------------------------------
        # Selector alternativo
        # --------------------------------------------------------

        if not items:

            print(
                "Selector principal sin resultados. "
                "Usando selector alternativo..."
            )

            items = self._armar_items(
                soup.select("h2 a, h3 a")
            )

        print(f"Artículos encontrados: {len(items)}")

        return items

    # ============================================================
    # ARMAR LISTA (titular, link)
    # ============================================================

    def _armar_items(self, anchors):

        items = []
        vistos = set()

        for a in anchors:

            if a is None:
                continue

            href = a.get("href")
            titular = a.get_text(" ", strip=True)

            if not href or not titular:
                continue

            link = urljoin(BASE_URL, href)

            partes = urlparse(link)

            # Solo notas de peru21.pe
            if not partes.netloc.endswith("peru21.pe"):
                continue

            segmentos = [
                s for s in partes.path.split("/") if s
            ]

            # Descartar secciones y páginas de etiquetas
            if len(segmentos) < 2:
                continue

            if segmentos[0] == "noticias":
                continue

            if link in vistos:
                continue

            vistos.add(link)

            items.append((titular, link))

            if len(items) >= self.news_number:
                break

        return items

    # ============================================================
    # TITULARES Y LINKS
    # ============================================================

    def header_scraper(self):

        return [titular for titular, _ in self.items]

    def link_scraper(self):

        return [link for _, link in self.items]

    # ============================================================
    # JSON-LD
    # ============================================================

    @staticmethod
    def _nodos_json_ld(soup):

        for script in soup.find_all(
            "script",
            type="application/ld+json"
        ):

            if not script.string:
                continue

            try:

                data = json.loads(
                    script.string,
                    strict=False
                )

            except (json.JSONDecodeError, TypeError):

                continue

            candidatos = (
                data if isinstance(data, list) else [data]
            )

            for nodo in candidatos:

                if not isinstance(nodo, dict):
                    continue

                yield nodo

                grafo = nodo.get("@graph")

                if isinstance(grafo, list):

                    for sub in grafo:

                        if isinstance(sub, dict):
                            yield sub

    @staticmethod
    def _meta(soup, *nombres):

        for nombre in nombres:

            tag = (
                soup.find("meta", attrs={"property": nombre})
                or soup.find("meta", attrs={"name": nombre})
            )

            if tag and tag.get("content"):

                return tag["content"].strip()

        return ""

    # ============================================================
    # DATOS DE UNA NOTA (fecha + contenido)
    # ============================================================

    def _datos_nota(self, link):

        if link in self._cache:
            return self._cache[link]

        datos = {"fecha": "", "descripcion": ""}

        try:

            respuesta = self.session.get(
                link,
                timeout=30
            )

            respuesta.raise_for_status()

            soup = BeautifulSoup(
                respuesta.text,
                "html.parser"
            )

            fecha = ""
            cuerpo = ""
            resumen = ""

            for nodo in self._nodos_json_ld(soup):

                if not fecha:

                    valor = (
                        nodo.get("datePublished")
                        or nodo.get("uploadDate")
                    )

                    if isinstance(valor, str):
                        fecha = valor

                if not cuerpo:

                    valor = nodo.get("articleBody")

                    if isinstance(valor, str):
                        cuerpo = valor

                if not resumen:

                    valor = nodo.get("description")

                    if isinstance(valor, str):
                        resumen = valor

            # Respaldo con etiquetas meta
            if not fecha:

                fecha = self._meta(
                    soup,
                    "article:published_time",
                    "og:article:published_time"
                )

            if not (cuerpo or resumen):

                resumen = self._meta(
                    soup,
                    "og:description",
                    "description"
                )

            datos["fecha"] = fecha.strip()

            datos["descripcion"] = (
                cuerpo or resumen
            ).strip()

        except Exception as error:

            print(
                f"Error procesando nota de Perú 21: {error}"
            )

        self._cache[link] = datos

        return datos

    # ============================================================
    # FECHAS
    # ============================================================

    def date_scraper(self):

        fechas = []

        links = self.link_scraper()

        for i, link in enumerate(links, start=1):

            print(
                f"Extrayendo fecha Perú 21 "
                f"{i}/{len(links)}..."
            )

            fechas.append(
                self._datos_nota(link)["fecha"]
            )

        return fechas

    # ============================================================
    # CONTENIDO
    # ============================================================

    def news_scraper(self):

        descripciones = []

        links = self.link_scraper()

        for i, link in enumerate(links, start=1):

            print(
                f"Extrayendo contenido Perú 21 "
                f"{i}/{len(links)}..."
            )

            descripciones.append(
                self._datos_nota(link)["descripcion"]
            )

        return descripciones
