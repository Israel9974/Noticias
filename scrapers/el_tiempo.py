import pandas as pd

from datetime import datetime

from .tiempo_scraper import Scraper2


class ElTiempo:
    """
    Scraper del portal El Tiempo.
    """

    def __init__(self, main_url, news_number=30):
        self.main_url = main_url
        self.news_number = news_number

    def dframe(self):

        print("Creando Scraper2...")

        news = Scraper2(
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
        # Determinar cantidad de noticias
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

        news_scraper = pd.DataFrame({
            "DIARIO": ["El Tiempo"] * cantidad,
            "DIA": fechas[:cantidad],
            "TITULAR": titulares[:cantidad],
            "DESCRIPCIÓN": descripciones[:cantidad],
            "LINKS": links[:cantidad]
        })

        print("DataFrame creado.")
        print(f"Filas: {len(news_scraper)}")

        # --------------------------------------------------
        # Limpiar descripción
        # --------------------------------------------------

        descripciones_limpias = (
            news_scraper["DESCRIPCIÓN"]
            .fillna("")
            .astype(str)
            .str.replace(
                r"&[a-zA-Z]+?;",
                " ",
                regex=True
            )
            .str.strip()
        )

        news_scraper.loc[:, "DESCRIPCIÓN"] = (
            descripciones_limpias
        )

        print("Descripción limpiada.")

        # --------------------------------------------------
        # Limpiar y convertir fechas
        # --------------------------------------------------

        meses = {
            "Ene": "Jan",
            "Abr": "Apr",
            "Ago": "Aug",
            "Set": "Sep",
            "Dic": "Dec"
        }

        fechas_convertidas = []

        for fecha in news_scraper["DIA"].tolist():

            if not fecha:
                fechas_convertidas.append(None)
                continue

            fecha = str(fecha).strip()

            # Cambiar meses españoles a ingleses
            for mes_es, mes_en in meses.items():

                fecha = fecha.replace(
                    mes_es,
                    mes_en
                )

            try:

                fecha_obj = datetime.strptime(
                    fecha,
                    "%b %d, %Y"
                ).date()

                fechas_convertidas.append(
                    fecha_obj
                )

            except ValueError:

                print(
                    f"No se pudo convertir fecha: {fecha}"
                )

                fechas_convertidas.append(None)

        news_scraper.loc[:, "DIA"] = (
            fechas_convertidas
        )

        print("Fechas convertidas.")

        return news_scraper


def scrape_el_tiempo(
    paginas_i,
    paginas_f,
    region="piura",
    news_number=30
):
    """
    Ejecuta el scraper de El Tiempo.

    paginas_i:
        Página inicial.

    paginas_f:
        Página final + 1.

    region:
        Región.

    news_number:
        Número máximo de noticias por página.
    """

    resultados = []

    for i in range(paginas_i, paginas_f):

        if region.lower() == "piura":

            url = (
                "https://eltiempo.pe/"
                f"categoria/local/page/{i}"
            )

        else:

            url = (
                "https://eltiempo.pe/"
                f"page/{i}/?s={region}"
            )

        print()
        print("=" * 60)
        print(f"El Tiempo - página {i}")
        print(f"URL: {url}")
        print("=" * 60)

        scraper = ElTiempo(
            main_url=url,
            news_number=news_number
        )

        pagina = scraper.dframe()

        resultados.append(pagina)

        print()
        print(f"Página {i} terminada.")
        print(f"Noticias obtenidas: {len(pagina)}")

    # ------------------------------------------------------
    # Unir páginas
    # ------------------------------------------------------

    if resultados:

        eltiempo = pd.concat(
            resultados,
            ignore_index=True
        )

    else:

        eltiempo = pd.DataFrame(
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
    print("¡EL TIEMPO TERMINÓ!")
    print(f"Total de noticias: {len(eltiempo)}")
    print("=" * 60)

    return eltiempo


if __name__ == "__main__":

    resultado = scrape_el_tiempo(
        paginas_i=1,
        paginas_f=2,
        region="piura",
        news_number=30
    )

    print()
    print(resultado)
