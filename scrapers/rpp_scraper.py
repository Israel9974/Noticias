import json
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException


BASE_URL = "https://rpp.pe"

# Las notas de RPP terminan en "-noticia-<número>"
# Ejemplo: .../alcalde-de-piura-dice-...-noticia-1715191
PATRON_NOTA = re.compile(r"-noticia-\d+")

# En el listado, las notas del día solo muestran la hora: "21:10 hs"
PATRON_HORA = re.compile(r"\b\d{1,2}:\d{2}\s*hs\b")

# Perú no usa horario de verano: siempre UTC-5
ZONA_PERU = timezone(timedelta(hours=-5))


class Scraper6:
    """
    Scraper auxiliar para RPP.

    Obtiene:
    - titulares
    - enlaces
    - fechas
    - contenido

    El listado de RPP solo muestra la hora de las notas del día
    (sin fecha), por eso la fecha se toma de cada nota
    (JSON-LD / meta). Si la nota no trae fecha pero el listado
    mostraba una hora, se asume que es de hoy (hora de Lima).
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
        self._cache = {}

        # Lista de tuplas (titular, link, muestra_hora)
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

            print(f"Error de conexión RPP: {error}")

            return []

        soup = BeautifulSoup(
            page.text,
            "html.parser"
        )

        # --------------------------------------------------------
        # Titulares: enlaces dentro de h2 / h3
        # --------------------------------------------------------

        items = self._armar_items(
            soup.select("h2 a, h3 a")
        )

        # --------------------------------------------------------
        # Alternativo: cualquier enlace con forma de nota
        # --------------------------------------------------------

        if not items:

            print(
                "Selector principal sin resultados. "
                "Usando selector alternativo..."
            )

            items = self._armar_items(
                soup.select("a[href]")
            )

        print(f"Artículos encontrados: {len(items)}")

        return items

    # ============================================================
    # ARMAR LISTA (titular, link, muestra_hora)
    # ============================================================

    def _armar_items(self, anchors):

        items = []
        vistos = set()

        for a in anchors:

            href = a.get("href")

            if not href or not PATRON_NOTA.search(href):
                continue

            link = urljoin(BASE_URL, href)

            if not urlparse(link).netloc.endswith("rpp.pe"):
                continue

            # Quitar parámetros y fragmentos
            link = link.split("#")[0].split("?")[0]

            titular = a.get_text(" ", strip=True)

            # Los enlaces de imagen no tienen texto
            if len(titular) < 15:
                continue

            if link in vistos:
                continue

            vistos.add(link)

            items.append((
                titular,
                link,
                self._muestra_hora(a)
            ))

            if len(items) >= self.news_number:
                break

        return items

    @staticmethod
    def _muestra_hora(anchor):
        """
        True si en el bloque de ESTA nota aparece una hora
        tipo '21:10 hs'.

        Se sube por los contenedores del titular y se detiene en
        cuanto un contenedor abarca más de una nota, para no leer
        la hora de otra nota por error.
        """

        nodo = anchor

        for _ in range(6):

            nodo = nodo.parent

            if nodo is None:
                break

            notas = {
                a["href"].split("?")[0].split("#")[0]
                for a in nodo.select("a[href]")
                if PATRON_NOTA.search(a["href"])
            }

            # El contenedor ya incluye otras notas
            if len(notas) > 1:
                break

            if PATRON_HORA.search(
                nodo.get_text(" ", strip=True)
            ):

                return True

        return False

    # ============================================================
    # TITULARES Y LINKS
    # ============================================================

    def header_scraper(self):

        return [titular for titular, _, _ in self.items]

    def link_scraper(self):

        return [link for _, link, _ in self.items]

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
                f"Error procesando nota de RPP: {error}"
            )

        self._cache[link] = datos

        return datos

    # ============================================================
    # FECHAS
    # ============================================================

    def date_scraper(self):

        fechas = []

        hoy = datetime.now(ZONA_PERU).strftime("%Y-%m-%d")

        total = len(self.items)

        for i, (_, link, muestra_hora) in enumerate(
            self.items,
            start=1
        ):

            print(
                f"Extrayendo fecha RPP {i}/{total}..."
            )

            fecha = self._datos_nota(link)["fecha"]

            # Sin fecha en la nota, pero el listado mostraba
            # la hora: es una nota de hoy
            if not fecha and muestra_hora:

                fecha = hoy

            fechas.append(fecha)

        return fechas

    # ============================================================
    # CONTENIDO
    # ============================================================

    def news_scraper(self):

        descripciones = []

        links = self.link_scraper()

        for i, link in enumerate(links, start=1):

            print(
                f"Extrayendo contenido RPP "
                f"{i}/{len(links)}..."
            )

            descripciones.append(
                self._datos_nota(link)["descripcion"]
            )

        return descripciones
