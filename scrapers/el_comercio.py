import pandas as pd
import re
from datetime import datetime

from .comercio_scraper import Scraper


class ElComercio:
    """
    Scraper del diario El Comercio.

    Extrae:
    - Diario
    - Fecha
    - Titular
    - Descripción
    - Link
    """

    def __init__(self, main_url, news_number=20):
        self.main_url = main_url
        self.news_number = news_number

    def dframe(self):

        print("Creando Scraper de El Comercio...")

        news = Scraper(
            self.main_url,
            self.news_number
        )

        print("Extrayendo fechas...")
        fechas = news.date_scraper()

        print("Extrayendo titulares...")
        titulares = news.header_scraper()

        print("Extrayendo links...")
        links = news.link_scraper()

        print("Extrayendo descripciones...")
        descripciones = news.news_scraper()

        # --------------------------------------------------
        # Verificar resultados
        # --------------------------------------------------

        print(f"Fechas obtenidas: {len(fechas) if fechas else 0}")
        print(f"Titulares obtenidos: {len(titulares) if titulares else 0}")
        print(f"Links obtenidos: {len(links) if links else 0}")
        print(
            f"Descripciones obtenidas: "
            f"{len(descripciones) if descripciones else 0}"
        )

        # Evitar errores si alguna función devuelve None
        fechas = fechas or []
        titulares = titulares or []
        links = links or []
        descripciones = descripciones or []

        # --------------------------------------------------
        # Determinar cantidad de noticias completas
        # --------------------------------------------------

        cantidad = min(
            len(fechas),
            len(titulares),
            len(links),
            len(descripciones)
        )

        print(f"Noticias completas: {cantidad}")

        if cantidad == 0:
            print("⚠ El Comercio no devolvió noticias.")
            return pd.DataFrame(
                columns=[
                    "DIARIO",
                    "DIA",
                    "TITULAR",
                    "DESCRIPCIÓN",
                    "LINKS"
                ]
            )

        # --------------------------------------------------
        # Crear DataFrame
        # --------------------------------------------------

        noticias = pd.DataFrame({
            "DIARIO": ["El Comercio"] * cantidad,
            "DIA": fechas[:cantidad],
            "TITULAR": titulares[:cantidad],
            "DESCRIPCIÓN": descripciones[:cantidad],
            "LINKS": links[:cantidad]
        })

        print(f"DataFrame creado: {len(noticias)} filas")

        # --------------------------------------------------
        # Limpiar descripción
        # --------------------------------------------------

        noticias.loc[:, "DESCRIPCIÓN"] = (
            noticias["DESCRIPCIÓN"]
            .fillna("")
            .astype(str)
            .str.replace(
                r"&[a-zA-Z]+?;",
                " ",
                regex=True
            )
            .str.strip()
        )

        # --------------------------------------------------
        # Convertir fechas
        # --------------------------------------------------

        fechas_convertidas = []

        for fecha in noticias["DIA"].tolist():

            if not fecha:
                fechas_convertidas.append(None)
                continue

            fecha = str(fecha).strip()

            # El Comercio normalmente devuelve:
            # 2026-09-10T...
            fecha = fecha.split("T")[0]

            try:

                fecha_obj = datetime.strptime(
                    fecha,
                    "%Y-%m-%d"
                ).date()

                fechas_convertidas.append(
                    fecha_obj
                )

            except ValueError:

                print(
                    f"⚠ No se pudo convertir fecha: {fecha}"
                )

                fechas_convertidas.append(None)

        noticias.loc[:, "DIA"] = fechas_convertidas

        print("Fechas convertidas.")

        return noticias


def scrape_el_comercio(
    region,
    paginas_i=1,
    paginas_f=2,
    news_number=20
):
    """
    Ejecuta el scraper de El Comercio.

    paginas_f es exclusivo:
        range(paginas_i, paginas_f)

    Por ejemplo:
        paginas_i=1
        paginas_f=2

    revisa solamente la página 1.
    """

    elcomercio = pd.DataFrame(
        columns=[
            "DIARIO",
            "DIA",
            "TITULAR",
            "DESCRIPCIÓN",
            "LINKS"
        ]
    )

    print()
    print("=" * 60)
    print("INICIANDO EL COMERCIO")
    print("=" * 60)

    for pagina in range(paginas_i, paginas_f):

        url = (
            f"https://elcomercio.pe/noticias/"
            f"{region}/{pagina}"
        )

        print()
        print("-" * 60)
        print(f"El Comercio - página {pagina}")
        print(f"URL: {url}")
        print("-" * 60)

        try:

            scraper = ElComercio(
                main_url=url,
                news_number=news_number
            )

            resultado = scraper.dframe()

            if resultado.empty:

                print(
                    f"⚠ Página {pagina}: "
                    "no se obtuvieron noticias."
                )

            else:

                elcomercio = pd.concat(
                    [
                        elcomercio,
                        resultado
                    ],
                    ignore_index=True
                )

                print(
                    f"Página {pagina} terminada."
                )

                print(
                    f"Noticias obtenidas: "
                    f"{len(resultado)}"
                )

        except Exception as e:

            print()
            print(
                f"❌ Error procesando "
                f"El Comercio página {pagina}:"
            )
            print(e)

    print()
    print("=" * 60)
    print("¡EL COMERCIO TERMINÓ!")
    print(
        f"Total de noticias: "
        f"{len(elcomercio)}"
    )
    print("=" * 60)

    return elcomercio


if __name__ == "__main__":

    resultado = scrape_el_comercio(
        region="piura",
        paginas_i=1,
        paginas_f=2,
        news_number=20
    )

    print()
    print(resultado)
