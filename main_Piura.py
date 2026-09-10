port os
import pandas as pd

from datetime import date, timedelta

from scrapers.el_tiempo import scrape_el_tiempo
from scrapers.andina import scrape_andina
from scrapers.el_comercio import scrape_el_comercio


# ============================================================
# CONFIGURACIÓN
# ============================================================

REGION = "piura"


# ------------------------------------------------------------
# EL TIEMPO
# ------------------------------------------------------------

NEWS_NUMBER_EL_TIEMPO = 30

PAGINAS_TIEMPO_I = 1
PAGINAS_TIEMPO_F = 2


# ------------------------------------------------------------
# ANDINA
# ------------------------------------------------------------

NEWS_NUMBER_ANDINA = 5


# ------------------------------------------------------------
# EL COMERCIO
# ------------------------------------------------------------

NEWS_NUMBER_EL_COMERCIO = 20

PAGINAS_COMERCIO_I = 1
PAGINAS_COMERCIO_F = 2


# ============================================================
# FECHAS
# ============================================================

FECHA_FINAL = date.today()

FECHA_INICIAL = (
    FECHA_FINAL - timedelta(days=7)
)


# ============================================================
# COLUMNAS
# ============================================================

COLUMNAS = [
    "DIARIO",
    "DIA",
    "TITULAR",
    "DESCRIPCIÓN",
    "LINKS"
]


# ============================================================
# DATAFRAME VACÍO
# ============================================================

def dataframe_vacio():

    return pd.DataFrame(
        columns=COLUMNAS
    )


# ============================================================
# NORMALIZAR FECHA
# ============================================================

def normalizar_fecha(fecha):
    """
    Convierte diferentes formatos de fecha
    a datetime.date.

    Formatos soportados:

    - datetime.date
    - datetime.datetime
    - 2026-09-10
    - 2026-09-10T12:30:00
    - 10/09/2026
    - Sep 10, 2026
    """

    if fecha is None:
        return None

    # --------------------------------------------------------
    # Ya es date
    # --------------------------------------------------------

    if isinstance(fecha, date):

        return fecha


    # --------------------------------------------------------
    # Convertir a string
    # --------------------------------------------------------

    fecha = str(
        fecha
    ).strip()


    if not fecha:
        return None


    # --------------------------------------------------------
    # Formato ISO
    #
    # 2026-09-10T12:30:00
    # --------------------------------------------------------

    if "T" in fecha:

        fecha = fecha.split(
            "T"
        )[0]


    # --------------------------------------------------------
    # Intentar formatos conocidos
    # --------------------------------------------------------

    formatos = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%b %d, %Y",
        "%B %d, %Y"
    ]


    for formato in formatos:

        try:

            return date.fromisoformat(
                fecha
            ) if formato == "%Y-%m-%d" else (
                pd.Timestamp.strptime(
                    fecha,
                    formato
                ).date()
            )

        except Exception:

            continue


    # --------------------------------------------------------
    # Si no se pudo convertir
    # --------------------------------------------------------

    return None


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def main():

    print()
    print("=" * 70)
    print("SCRAPER DE NOTICIAS - PIURA")
    print("=" * 70)

    print(
        f"Región: {REGION}"
    )

    print(
        f"Fecha inicial: {FECHA_INICIAL}"
    )

    print(
        f"Fecha final: {FECHA_FINAL}"
    )

    print("=" * 70)


    # ========================================================
    # EL TIEMPO
    # ========================================================

    print()
    print("=" * 70)
    print("INICIANDO EL TIEMPO")
    print("=" * 70)


    try:

        eltiempo = scrape_el_tiempo(
            paginas_i=PAGINAS_TIEMPO_I,
            paginas_f=PAGINAS_TIEMPO_F,
            region=REGION,
            news_number=NEWS_NUMBER_EL_TIEMPO
        )


        print()

        print(
            f"El Tiempo terminado: "
            f"{len(eltiempo)} noticias"
        )


    except Exception as error:

        print()
        print(
            "ERROR EN EL TIEMPO:"
        )

        print(error)

        eltiempo = dataframe_vacio()


    # ========================================================
    # ANDINA
    # ========================================================

    print()
    print("=" * 70)
    print("INICIANDO ANDINA")
    print("=" * 70)


    try:

        andina = scrape_andina(
            region=REGION,
            news_number=NEWS_NUMBER_ANDINA
        )


        print()

        print(
            f"Andina terminado: "
            f"{len(andina)} noticias"
        )


    except Exception as error:

        print()
        print(
            "ERROR EN ANDINA:"
        )

        print(error)

        andina = dataframe_vacio()


    # ========================================================
    # EL COMERCIO
    # ========================================================

    print()
    print("=" * 70)
    print("INICIANDO EL COMERCIO")
    print("=" * 70)


    try:

        elcomercio = scrape_el_comercio(
            region=REGION,
            paginas_i=PAGINAS_COMERCIO_I,
            paginas_f=PAGINAS_COMERCIO_F,
            news_number=NEWS_NUMBER_EL_COMERCIO
        )


        print()

        print(
            f"El Comercio terminado: "
            f"{len(elcomercio)} noticias"
        )


    except Exception as error:

        print()
        print(
            "ERROR EN EL COMERCIO:"
        )

        print(error)

        elcomercio = dataframe_vacio()


    # ========================================================
    # RESUMEN DE SCRAPERS
    # ========================================================

    print()
    print("=" * 70)
    print("RESUMEN DE SCRAPERS")
    print("=" * 70)

    print(
        f"El Tiempo:    {len(eltiempo)}"
    )

    print(
        f"Andina:       {len(andina)}"
    )

    print(
        f"El Comercio:  {len(elcomercio)}"
    )


    # ========================================================
    # UNIR
    # ========================================================

    print()
    print("=" * 70)
    print("UNIENDO NOTICIAS")
    print("=" * 70)


    noticias = pd.concat(
        [
            eltiempo,
            andina,
            elcomercio
        ],
        ignore_index=True
    )


    print(
        f"Total de noticias antes "
        f"del filtro: {len(noticias)}"
    )


    # ========================================================
    # ASEGURAR COLUMNAS
    # ========================================================

    for columna in COLUMNAS:

        if columna not in noticias.columns:

            noticias[columna] = ""


    noticias = noticias[
        COLUMNAS
    ]


    # ========================================================
    # NORMALIZAR FECHAS
    # ========================================================

    print()
    print(
        "Normalizando fechas..."
    )


    # IMPORTANTE:
    # No usamos pd.to_datetime().
    #
    # Convertimos cada fecha individualmente.
    # Esto evita problemas con pandas/numpy.


    noticias["DIA"] = [
        normalizar_fecha(fecha)
        for fecha in noticias["DIA"]
    ]


    print(
        "Fechas normalizadas."
    )


    # ========================================================
    # CONTAR FECHAS INVÁLIDAS
    # ========================================================

    fechas_invalidas = sum(
        fecha is None
        for fecha in noticias["DIA"]
    )


    if fechas_invalidas > 0:

        print(
            f"⚠ Fechas inválidas: "
            f"{fechas_invalidas}"
        )


    # ========================================================
    # FILTRAR POR FECHA
    # ========================================================

    print()
    print(
        "Filtrando noticias por fecha..."
    )


    noticias = noticias[
        noticias["DIA"].apply(
            lambda fecha:
                fecha is not None
                and
                FECHA_INICIAL <= fecha <= FECHA_FINAL
        )
    ].copy()


    print(
        f"Noticias después del filtro: "
        f"{len(noticias)}"
    )


    # ========================================================
    # ELIMINAR DUPLICADOS
    # ========================================================

    print()
    print(
        "Eliminando noticias duplicadas..."
    )


    noticias_con_link = noticias[
        noticias["LINKS"]
        .fillna("")
        .astype(str)
        .str.strip()
        != ""
    ].copy()


    noticias_sin_link = noticias[
        noticias["LINKS"]
        .fillna("")
        .astype(str)
        .str.strip()
        == ""
    ].copy()


    noticias_con_link = (
        noticias_con_link
        .drop_duplicates(
            subset=["LINKS"],
            keep="first"
        )
    )


    noticias = pd.concat(
        [
            noticias_con_link,
            noticias_sin_link
        ],
        ignore_index=True
    )


    print(
        f"Noticias después de eliminar "
        f"duplicados: {len(noticias)}"
    )


    # ========================================================
    # ORDENAR
    # ========================================================

    print()
    print(
        "Ordenando noticias..."
    )


    noticias = noticias.sort_values(
        by="DIA",
        ascending=False
    ).reset_index(
        drop=True
    )


    print(
        "Noticias ordenadas."
    )


    # ========================================================
    # RESUMEN FINAL
    # ========================================================

    print()
    print("=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)


    if noticias.empty:

        print(
            "No se encontraron noticias "
            "dentro del rango de fechas."
        )

    else:

        resumen = (
            noticias["DIARIO"]
            .value_counts()
        )


        for diario, cantidad in resumen.items():

            print(
                f"{diario}: "
                f"{cantidad} noticias"
            )


    print()

    print(
        f"TOTAL FINAL: "
        f"{len(noticias)} noticias"
    )


    # ========================================================
    # CREAR CARPETA DATA
    # ========================================================

    print()
    print(
        "Verificando carpeta Data..."
    )


    os.makedirs(
        "Data",
        exist_ok=True
    )


    # ========================================================
    # NOMBRE DEL ARCHIVO
    # ========================================================

    fecha_inicial_str = (
        FECHA_INICIAL.strftime(
            "%Y%m%d"
        )
    )


    fecha_final_str = (
        FECHA_FINAL.strftime(
            "%Y%m%d"
        )
    )


    nombre_archivo = (
        f"noticias_{REGION}_"
        f"{fecha_inicial_str}_"
        f"{fecha_final_str}.xlsx"
    )


    ruta_salida = os.path.join(
        "Data",
        nombre_archivo
    )


    # ========================================================
    # GUARDAR
    # ========================================================

    print()
    print("=" * 70)
    print("GUARDANDO ARCHIVO")
    print("=" * 70)


    try:

        noticias.to_excel(
            ruta_salida,
            index=False
        )


        print()

        print(
            "✓ Archivo guardado correctamente:"
        )

        print(
            ruta_salida
        )


    except Exception as error:

        print()

        print(
            "ERROR GUARDANDO EXCEL:"
        )

        print(error)

        return


    # ========================================================
    # FINAL
    # ========================================================

    print()
    print("=" * 70)
    print("PROCESO TERMINADO CORRECTAMENTE")
    print("=" * 70)

    print(
        f"Archivo: {ruta_salida}"
    )

    print(
        f"Noticias finales: "
        f"{len(noticias)}"
    )

    print("=" * 70)


# ============================================================
# EJECUTAR
# ============================================================

if __name__ == "__main__":

    main()