import pandas as pd

from datetime import datetime

from .comercio_scraper import Scraper


class ElComercio:
    """
    Scraper del diario El Comercio.

    Extrae:

    - DIARIO
    - DIA
    - TITULAR
    - DESCRIPCIÓN
    - LINKS
    """

    def __init__(
        self,
        main_url,
        news_number=20
    ):

        self.main_url = main_url
        self.news_number = news_number


    def dframe(self):

        print(
            "Creando Scraper de El Comercio..."
        )

        news = Scraper(
            self.main_url,
            self.news_number
        )


        # ==================================================
        # EXTRAER DATOS
        # ==================================================

        print(
            "Extrayendo fechas..."
        )

        fechas = news.date_scraper()


        print(
            "Extrayendo titulares..."
        )

        titulares = news.header_scraper()


        print(
            "Extrayendo links..."
        )

        links = news.link_scraper()


        print(
            "Extrayendo descripciones..."
        )

        descripciones = news.news_scraper()


        # ==================================================
        # MOSTRAR RESULTADOS
        # ==================================================

        print(
            f"Fechas obtenidas: "
            f"{len(fechas)}"
        )

        print(
            f"Titulares obtenidos: "
            f"{len(titulares)}"
        )

        print(
            f"Links obtenidos: "
            f"{len(links)}"
        )

        print(
            f"Descripciones obtenidas: "
            f"{len(descripciones)}"
        )


        # ==================================================
        # EVITAR NONE
        # ==================================================

        fechas = fechas or []
        titulares = titulares or []
        links = links or []
        descripciones = descripciones or []


        # ==================================================
        # DETERMINAR CANTIDAD
        # ==================================================

        cantidad = min(
            len(fechas),
            len(titulares),
            len(links),
            len(descripciones)
        )

        print(
            f"Noticias completas: {cantidad}"
        )


        # ==================================================
        # DATAFRAME VACÍO
        # ==================================================

        if cantidad == 0:

            print(
                "El Comercio no devolvió noticias."
            )

            return pd.DataFrame(
                columns=[
                    "DIARIO",
                    "DIA",
                    "TITULAR",
                    "DESCRIPCIÓN",
                    "LINKS"
                ]
            )


        # ==================================================
        # CREAR DATAFRAME
        # ==================================================

        noticias = pd.DataFrame({

            "DIARIO": [
                "El Comercio"
            ] * cantidad,

            "DIA": fechas[:cantidad],

            "TITULAR": titulares[:cantidad],

            "DESCRIPCIÓN": (
                descripciones[:cantidad]
            ),

            "LINKS": links[:cantidad]
        })


        print(
            f"DataFrame creado: "
            f"{len(noticias)} filas"
        )


        # ==================================================
        # LIMPIAR DESCRIPCIÓN
        # ==================================================

        noticias.loc[:, "DESCRIPCIÓN"] = (

            noticias["DESCRIPCIÓN"]
            .fillna("")
            .astype(str)

            .str.replace(
                r"&[a-zA-Z]+?;",
                " ",
                regex=True
            )

            .str.replace(
                r"\s+",
                " ",
                regex=True
            )

            .str.strip()
        )


        # ==================================================
        # CONVERTIR FECHAS
        # ==================================================

        fechas_convertidas = []


        for fecha in noticias["DIA"].tolist():

            if not fecha:

                fechas_convertidas.append(
                    None
                )

                continue


            fecha = str(
                fecha
            ).strip()


            # ----------------------------------------------
            # El Comercio normalmente devuelve:
            #
            # 2026-09-10T12:30:00-05:00
            #
            # Nos quedamos con:
            #
            # 2026-09-10
            # ----------------------------------------------

            if "T" in fecha:

                fecha = fecha.split(
                    "T"
                )[0]


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
                    f"No se pudo convertir "
                    f"fecha de El Comercio: "
                    f"{fecha}"
                )

                fechas_convertidas.append(
                    None
                )


        noticias.loc[:, "DIA"] = (
            fechas_convertidas
        )


        print(
            "Fechas convertidas."
        )


        return noticias



def scrape_el_comercio(
    region,
    paginas_i=1,
    paginas_f=2,
    news_number=20
):
    """
    Ejecuta el scraper de El Comercio.

    paginas_f es exclusivo.

    Ejemplo:

        paginas_i=1
        paginas_f=2

    procesa únicamente la página 1.
    """


    columnas = [
        "DIARIO",
        "DIA",
        "TITULAR",
        "DESCRIPCIÓN",
        "LINKS"
    ]


    elcomercio = pd.DataFrame(
        columns=columnas
    )


    print()
    print("=" * 60)
    print("INICIANDO EL COMERCIO")
    print("=" * 60)


    # ======================================================
    # RECORRER PÁGINAS
    # ======================================================

    for pagina in range(
        paginas_i,
        paginas_f
    ):

        url = (
            "https://elcomercio.pe/noticias/"
            f"{region}/{pagina}"
        )


        print()
        print("-" * 60)

        print(
            f"El Comercio - página {pagina}"
        )

        print(
            f"URL: {url}"
        )

        print("-" * 60)


        try:

            scraper = ElComercio(
                main_url=url,
                news_number=news_number
            )


            resultado = scraper.dframe()


            if resultado.empty:

                print(
                    f"Página {pagina}: "
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


        except Exception as error:

            print()
            print(
                f"ERROR procesando "
                f"El Comercio página {pagina}:"
            )

            print(error)


    # ======================================================
    # FINAL
    # ======================================================

    print()
    print("=" * 60)
    print("EL COMERCIO TERMINÓ")
    print("=" * 60)

    print(
        f"Total de noticias: "
        f"{len(elcomercio)}"
    )

    print("=" * 60)


    return elcomercio



# ==========================================================
# PRUEBA DIRECTA
# ==========================================================

if __name__ == "__main__":

    resultado = scrape_el_comercio(
        region="piura",
        paginas_i=1,
        paginas_f=2,
        news_number=20
    )

    print()

    print(resultado)
