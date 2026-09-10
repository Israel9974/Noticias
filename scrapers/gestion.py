import pandas as pd

from datetime import datetime

from .gestion_scraper import Scraper4


class Gestion:
    """
    Scraper del diario Gestión.

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

        print(
            "Creando Scraper de Gestión..."
        )

        news = Scraper4(
            self.main_url,
            self.news_number
        )

        # --------------------------------------------------------
        # Extraer
        # --------------------------------------------------------

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

        # --------------------------------------------------------
        # Evitar None
        # --------------------------------------------------------

        fechas = fechas or []
        titulares = titulares or []
        links = links or []
        descripciones = descripciones or []

        print(
            f"Fechas obtenidas: {len(fechas)}"
        )

        print(
            f"Titulares obtenidos: {len(titulares)}"
        )

        print(
            f"Links obtenidos: {len(links)}"
        )

        print(
            f"Descripciones obtenidas: "
            f"{len(descripciones)}"
        )

        # --------------------------------------------------------
        # Cantidad
        # --------------------------------------------------------

        cantidad = min(
            len(fechas),
            len(titulares),
            len(links),
            len(descripciones)
        )

        print(
            f"Noticias completas: {cantidad}"
        )

        if cantidad == 0:

            print(
                "⚠ Gestión no devolvió "
                "noticias completas."
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

        # --------------------------------------------------------
        # DataFrame
        # --------------------------------------------------------

        noticias = pd.DataFrame({
            "DIARIO": [
                "Gestión"
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

        # ========================================================
        # LIMPIAR DESCRIPCIÓN
        # ========================================================

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

        print(
            "Descripción limpiada."
        )

        # ========================================================
        # CONVERTIR FECHAS
        # ========================================================

        print(
            "Normalizando fechas de Gestión..."
        )

        fechas_convertidas = []

        for fecha in noticias[
            "DIA"
        ].tolist():

            if fecha is None:

                fechas_convertidas.append(
                    None
                )

                continue

            fecha = str(
                fecha
            ).strip()

            if not fecha:

                fechas_convertidas.append(
                    None
                )

                continue

            # ----------------------------------------------------
            # Eliminar hora
            # ----------------------------------------------------

            fecha_solo_dia = (
                fecha.split("T")[0]
            )

            # ----------------------------------------------------
            # Convertir manualmente
            # ----------------------------------------------------

            try:

                fecha_obj = (
                    datetime.strptime(
                        fecha_solo_dia,
                        "%Y-%m-%d"
                    ).date()
                )

                fechas_convertidas.append(
                    fecha_obj
                )

            except ValueError:

                print(
                    "⚠ No se pudo convertir "
                    f"fecha Gestión: {fecha}"
                )

                fechas_convertidas.append(
                    None
                )

        # --------------------------------------------------------
        # Asignación segura
        # --------------------------------------------------------

        noticias.loc[:, "DIA"] = (
            fechas_convertidas
        )

        print(
            "Fechas de Gestión convertidas."
        )

        return noticias


# ================================================================
# FUNCIÓN PRINCIPAL
# ================================================================

def scrape_gestion(
    region,
    paginas_i=1,
    paginas_f=2,
    news_number=20
):

    resultados = []

    print()
    print("=" * 60)
    print("GESTIÓN")
    print("=" * 60)

    for pagina in range(
        paginas_i,
        paginas_f
    ):

        url = (
            "https://gestion.pe/noticias/"
            f"{region}/{pagina}/"
        )

        print()
        print("-" * 60)
        print(
            f"Gestión - página {pagina}"
        )
        print(
            f"URL: {url}"
        )
        print("-" * 60)

        try:

            scraper = Gestion(
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

                resultados.append(
                    resultado
                )

                print()
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
                f"❌ Error procesando "
                f"Gestión página {pagina}:"
            )

            print(error)

    # ============================================================
    # UNIR PÁGINAS
    # ============================================================

    if resultados:

        gestion = pd.concat(
            resultados,
            ignore_index=True
        )

    else:

        gestion = pd.DataFrame(
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
    print("¡GESTIÓN TERMINÓ!")
    print(
        f"Total de noticias: "
        f"{len(gestion)}"
    )
    print("=" * 60)

    return gestion


# ================================================================
# PRUEBA DIRECTA
# ================================================================

if __name__ == "__main__":

    resultado = scrape_gestion(
        region="piura",
        paginas_i=1,
        paginas_f=2,
        news_number=20
    )

    print()
    print(resultado)
