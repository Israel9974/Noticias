import json
import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException


BASE_URL = "https://peru21.pe"

# True  -> además del listado, abre cada nota para intentar obtener
#          el texto completo y la fecha de publicación (más lento).
# False -> usa solo lo que muestra el listado (fecha y resumen):
#          mucho más rápido y con muchas menos peticiones.
DESCARGAR_TEXTO_COMPLETO = True

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,image/avif,"
        "image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "es-PE,es;q=0.9,en;q=0.8",
    "Referer": "https://www.google.com/",
    "Upgrade-Insecure-Requests": "1"
}


class Scraper3:
    """
    Scraper auxiliar para Perú 21.

    Perú 21 usa Drupal. Cada nota del listado tiene esta forma:

        <article class="node node--type-article ...">
          <div class="fecha-teaser-2col"> 2026-11-12 12:01 </div>
          <div class="titulo-teaser-2col">
            <a href="/peru/..."><h2>Titular</h2></a>
          </div>
          <div class="entradilla-teaser-2col"> resumen </div>
        </article>

    Del listado se toma titular, link, fecha y resumen.
    Si DESCARGAR_TEXTO_COMPLETO es True, se abre cada nota para
    obtener el texto completo y la fecha de publicación (JSON-LD);
    si no se puede, se queda con lo del listado.

    IMPORTANTE: Perú 21 devuelve 403 si la petición no trae
    cabeceras de navegador completas, por eso se usan HEADERS.
    """

    def __init__(self, url, news_number=20):

        self.url = url
        self.news_number = news_number

        self.session = requests.Session()
        self.session.headers.update(HEADERS)

        # Cada nota se descarga UNA sola vez
        self._cache = {}

        # Lista de diccionarios: titular, link, fecha, entradilla
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
        # Estructura actual (Drupal)
        # --------------------------------------------------------

        items = self._items_desde_articulos(soup)

        # --------------------------------------------------------
        # Respaldo: cualquier titular h2/h3 con enlace
        # --------------------------------------------------------

        if not items:

            print(
                "Selector principal sin resultados. "
                "Usando selector alternativo..."
            )

            items = self._items_desde_titulares(soup)

        print(f"Artículos encontrados: {len(items)}")

        return items

    # ============================================================
    # NOTAS DEL LISTADO
    # ============================================================

    def _items_desde_articulos(self, soup):

        items = []
        vistos = set()

        # "node--type-article" evita contar los <article> internos
        # de las imágenes (media)
        for art in soup.select("article.node--type-article"):

            titulo = art.select_one("h2, h3")

            if titulo is None:
                continue

            a = titulo.find_parent("a") or titulo.find("a")

            if a is None:
                continue

            link = self._link_valido(a.get("href"))

            if not link or link in vistos:
                continue

            titular = titulo.get_text(" ", strip=True)

            if not titular:
                continue

            # Fecha del listado: "2026-11-12 12:01"
            fecha = ""

            fecha_tag = art.select_one('[class*="fecha"]')

            if fecha_tag is not None:

                coincidencia = re.search(
                    r"\d{4}-\d{2}-\d{2}",
                    fecha_tag.get_text(" ", strip=True)
                )

                if coincidencia:
                    fecha = coincidencia.group(0)

            # Resumen del listado
            entradilla = ""

            entradilla_tag = art.select_one(
                '[class*="entradilla"]'
            )

            if entradilla_tag is not None:

                entradilla = entradilla_tag.get_text(
                    " ",
                    strip=True
                )

            vistos.add(link)

            items.append({
                "titular": titular,
                "link": link,
                "fecha": fecha,
                "entradilla": entradilla
            })

            if len(items) >= self.news_number:
                break

        return items

    def _items_desde_titulares(self, soup):

        items = []
        vistos = set()

        for titulo in soup.select("h2, h3"):

            a = titulo.find_parent("a") or titulo.find("a")

            if a is None:
                continue

            link = self._link_valido(a.get("href"))

            if not link or link in vistos:
                continue

            titular = titulo.get_text(" ", strip=True)

            if not titular:
                continue

            vistos.add(link)

            items.append({
                "titular": titular,
                "link": link,
                "fecha": "",
                "entradilla": ""
            })

            if len(items) >= self.news_number:
                break

        return items

    def _link_valido(self, href):

        if not href:
            return ""

        link = urljoin(BASE_URL, href)

        partes = urlparse(link)

        # Solo notas de peru21.pe
        if not partes.netloc.endswith("peru21.pe"):
            return ""

        segmentos = [
            s for s in partes.path.split("/") if s
        ]

        # Descartar secciones y páginas de etiquetas
        if len(segmentos) < 2:
            return ""

        if segmentos[0] in ("noticias", "autor"):
            return ""

        return link

    # ============================================================
    # TITULARES Y LINKS
    # ============================================================

    def header_scraper(self):

        return [item["titular"] for item in self.items]

    def link_scraper(self):

        return [item["link"] for item in self.items]

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
    # DATOS DE UNA NOTA (fecha de publicación + texto completo)
    # ============================================================

    def _datos_nota(self, link):

        if link in self._cache:
            return self._cache[link]

        datos = {"fecha": "", "cuerpo": "", "resumen": ""}

        if not DESCARGAR_TEXTO_COMPLETO:

            self._cache[link] = datos

            return datos

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
            datos["cuerpo"] = cuerpo.strip()
            datos["resumen"] = resumen.strip()

        except Exception as error:

            print(
                f"Error procesando nota de Perú 21: {error}"
            )

        self._cache[link] = datos

        return datos

    # ============================================================
    # FECHAS
    #
    # Prioridad: fecha de publicación de la nota (JSON-LD);
    # si no hay, la fecha que muestra el listado.
    # ============================================================

    def date_scraper(self):

        fechas = []

        total = len(self.items)

        for i, item in enumerate(self.items, start=1):

            if DESCARGAR_TEXTO_COMPLETO:

                print(
                    f"Extrayendo fecha Perú 21 {i}/{total}..."
                )

            fecha = (
                self._datos_nota(item["link"])["fecha"]
                or item["fecha"]
            )

            fechas.append(fecha)

        return fechas

    # ============================================================
    # CONTENIDO
    #
    # Prioridad: texto completo (articleBody) > resumen del
    # listado > descripción de la nota.
    # ============================================================

    def news_scraper(self):

        descripciones = []

        total = len(self.items)

        for i, item in enumerate(self.items, start=1):

            if DESCARGAR_TEXTO_COMPLETO:

                print(
                    f"Extrayendo contenido Perú 21 {i}/{total}..."
                )

            datos = self._datos_nota(item["link"])

            descripciones.append(
                datos["cuerpo"]
                or item["entradilla"]
                or datos["resumen"]
            )

        return descripciones
