import pandas as pd
import re

from datetime import datetime

from .andina_scraper import Scraper8


class Andina:
    """
    Scraper del portal Andina.

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

        print("Creando Scraper8...")

        news = Scraper8(
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
        # Determinar cantidad de noticias completas
        # --------------------------------------------------

        cantidad = min(
            len(fechas),
            len(titulares),
            len(links),
            len(descripciones)
        )

        print(f"Noticias completas: {cantidad}")

        # --------------------------------------------------
        # Crear DataFrame
        # --------------------------------------------------

        noticias = pd.DataFrame({
            "DIARIO": ["Andina"] * cantidad,
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

            try:

                fecha_obj = datetime.strptime(
                    fecha,
                    "%d/%m/%Y"
                ).date()

                fechas_convertidas.append(
                    fecha_obj
                )

            except ValueError:

                print(
                    f"No se pudo convertir fecha: {fecha}"
                )

                fechas_convertidas.append(None)

        noticias.loc[:, "DIA"] = fechas_convertidas

        print("Fechas convertidas.")

        return noticias


def scrape_andina(
    region,
    news_number=20
):
    """
    Ejecuta el scraper de Andina.

    Andina utiliza una búsqueda por región,
    por lo que no necesitamos recorrer páginas.
    """

    url = (
        "https://andina.pe/agencia/"
        f"busqueda.aspx?search={region}"
    )

    print()
    print("=" * 60)
    print("ANDINA")
    print(f"Región: {region}")
    print(f"URL: {url}")
    print("=" * 60)

    scraper = Andina(
        main_url=url,
        news_number=news_number
    )

    andina = scraper.dframe()

    print()
    print(f"Noticias obtenidas de Andina: {len(andina)}")

    return andina


if __name__ == "__main__":

    resultado = scrape_andina(
        region="piura",
        news_number=20
    )

    print()
    print(resultado)
