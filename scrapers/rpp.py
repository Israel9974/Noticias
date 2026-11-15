import pandas as pd

from datetime import datetime

from .rpp_scraper import Scraper6


COLUMNAS = [
    "DIARIO",
    "DIA",
    "TITULAR",
    "DESCRIPCIÓN",
    "LINKS"
]


class RPP:
    """
    Scraper del diario RPP.

    Extrae:
    - Diario
    - Fecha
    - Titular
    - Descripción
    - Link
    """

    def __init__(
        self,
        main_url,
        news_number=20
    ):

        self.main_url = main_url
        self.news_number = news_number

    # ============================================================
    # DATAFRAME
    # ============================================================

    def dframe(self):

        print("Creando Scraper de RPP...")

        news = Scraper6(
            self.main_url,
            self.news_number
        )

        print("Extrayendo fechas...")
        fechas = news.date_scraper() or []

        print("Extrayendo titulares...")
        titulares = news.header_scraper() or []

        print("Extrayendo links...")
        links = news.link_scraper() or []

        print("Extrayendo descripciones...")
        descripciones = news.news_scraper() or []

        print(f"Fechas obtenidas: {len(fechas)}")
        print(f"Titulares obtenidos: {len(titulares)}")
        print(f"Links obtenidos: {len(links)}")
        print(f"Descripciones obtenidas: {len(descripciones)}")

        cantidad = min(
            len(fechas),
            len(titulares),
            len(links),
            len(descripciones)
        )

        print(f"Noticias completas: {cantidad}")

        if cantidad == 0:

            print("⚠ RPP no devolvió noticias completas.")

            return pd.DataFrame(columns=COLUMNAS)

        noticias = pd.DataFrame({
            "DIARIO": ["RPP"] * cantidad,
            "DIA": fechas[:cantidad],
            "TITULAR": titulares[:cantidad],
            "DESCRIPCIÓN": descripciones[:cantidad],
            "LINKS": links[:cantidad]
        })

        print(f"DataFrame creado: {len(noticias)} filas")

        # --------------------------------------------------------
        # Limpiar descripción
        # --------------------------------------------------------

        noticias.loc[:, "DESCRIPCIÓN"] = (
            noticias["DESCRIPCIÓN"]
            .fillna("")
            .astype(str)
            .str.replace(r"&[a-zA-Z]+?;", " ", regex=True)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

        # --------------------------------------------------------
        # Convertir fechas
        #
        # 2026-11-10T12:30:00-05:00  ->  2026-11-10
        # --------------------------------------------------------

        fechas_convertidas = []

        for fecha in noticias["DIA"].tolist():

            fecha = str(fecha or "").strip()

            if not fecha:

                fechas_convertidas.append(None)
                continue

            fecha = fecha.split("T")[0]

            try:

                fechas_convertidas.append(
                    datetime.strptime(
                        fecha,
                        "%Y-%m-%d"
                    ).date()
                )

            except ValueError:

                print(
                    f"⚠ No se pudo convertir "
                    f"fecha de RPP: {fecha}"
                )

                fechas_convertidas.append(None)

        noticias["DIA"] = pd.Series(
            fechas_convertidas,
            index=noticias.index,
            dtype="object"
        )

        print("Fechas de RPP convertidas.")

        return noticias


# ================================================================
# FUNCIÓN PRINCIPAL
# ================================================================

def scrape_rpp(
    region,
    news_number=20
):
    """
    Ejecuta el scraper de RPP.

    Prueba primero https://rpp.pe/peru/<region> y, si no devuelve
    noticias, https://rpp.pe/noticias/<region>.
    """

    print()
    print("=" * 60)
    print("RPP")
    print("=" * 60)

    urls = [
        f"https://rpp.pe/peru/{region}",
        f"https://rpp.pe/noticias/{region}"
    ]

    rpp = pd.DataFrame(columns=COLUMNAS)

    for url in urls:

        print()
        print("-" * 60)
        print(f"RPP - {url}")
        print("-" * 60)

        try:

            resultado = RPP(
                main_url=url,
                news_number=news_number
            ).dframe()

            if resultado.empty:

                print(
                    "⚠ Esta URL no devolvió noticias. "
                    "Probando la siguiente..."
                )

                continue

            rpp = resultado

            break

        except Exception as error:

            print()
            print("❌ Error procesando RPP:")
            print(error)

    print()
    print("=" * 60)
    print("¡RPP TERMINÓ!")
    print(f"Total de noticias: {len(rpp)}")
    print("=" * 60)

    return rpp


# ================================================================
# PRUEBA DIRECTA
# ================================================================

if __name__ == "__main__":

    resultado = scrape_rpp(
        region="piura",
        news_number=20
    )

    print()
    print(resultado)
