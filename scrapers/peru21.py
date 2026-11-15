import pandas as pd

from datetime import datetime

from .peru21_scraper import Scraper3


COLUMNAS = [
    "DIARIO",
    "DIA",
    "TITULAR",
    "DESCRIPCIÓN",
    "LINKS"
]


class Peru21:
    """
    Scraper del diario Perú 21.

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

        print("Creando Scraper de Perú 21...")

        news = Scraper3(
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

            print("⚠ Perú 21 no devolvió noticias completas.")

            return pd.DataFrame(columns=COLUMNAS)

        noticias = pd.DataFrame({
            "DIARIO": ["Perú 21"] * cantidad,
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
        # Perú 21 puede devolver:
        # 2026-11-10T12:30:00-05:00   (JSON-LD de la nota)
        # 2026-11-10 12:01            (listado)
        # En ambos casos nos quedamos con 2026-11-10
        # --------------------------------------------------------

        fechas_convertidas = []

        for fecha in noticias["DIA"].tolist():

            fecha = str(fecha or "").strip()

            if not fecha:

                fechas_convertidas.append(None)
                continue

            # "AAAA-MM-DD" son los primeros 10 caracteres,
            # venga con "T" o con espacio
            fecha = fecha[:10]

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
                    f"fecha de Perú 21: {fecha}"
                )

                fechas_convertidas.append(None)

        noticias["DIA"] = pd.Series(
            fechas_convertidas,
            index=noticias.index,
            dtype="object"
        )

        print("Fechas de Perú 21 convertidas.")

        return noticias


# ================================================================
# FUNCIÓN PRINCIPAL
# ================================================================

def scrape_peru21(
    region,
    paginas_i=1,
    paginas_f=2,
    news_number=20
):
    """
    Ejecuta el scraper de Perú 21.

    paginas_f es exclusivo: paginas_i=1 y paginas_f=2
    procesa únicamente la página 1.
    """

    resultados = []

    print()
    print("=" * 60)
    print("PERÚ 21")
    print("=" * 60)

    for pagina in range(paginas_i, paginas_f):

        # La página 1 es la URL sin número;
        # de la 2 en adelante lleva /<número>/
        if pagina == 1:

            url = f"https://peru21.pe/noticias/{region}/"

        else:

            url = f"https://peru21.pe/noticias/{region}/{pagina}/"

        print()
        print("-" * 60)
        print(f"Perú 21 - página {pagina}")
        print(f"URL: {url}")
        print("-" * 60)

        try:

            resultado = Peru21(
                main_url=url,
                news_number=news_number
            ).dframe()

            if resultado.empty:

                print(
                    f"⚠ Página {pagina}: "
                    "no se obtuvieron noticias."
                )

            else:

                resultados.append(resultado)

                print(
                    f"Página {pagina} terminada. "
                    f"Noticias obtenidas: {len(resultado)}"
                )

        except Exception as error:

            print()
            print(
                f"❌ Error procesando "
                f"Perú 21 página {pagina}:"
            )

            print(error)

    if resultados:

        peru21 = pd.concat(
            resultados,
            ignore_index=True
        )

    else:

        peru21 = pd.DataFrame(columns=COLUMNAS)

    print()
    print("=" * 60)
    print("¡PERÚ 21 TERMINÓ!")
    print(f"Total de noticias: {len(peru21)}")
    print("=" * 60)

    return peru21


# ================================================================
# PRUEBA DIRECTA
# ================================================================

if __name__ == "__main__":

    resultado = scrape_peru21(
        region="piura",
        paginas_i=1,
        paginas_f=2,
        news_number=20
    )

    print()
    print(resultado)
