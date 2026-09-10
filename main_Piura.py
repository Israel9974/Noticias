import os
import pandas as pd

from datetime import date, timedelta, datetime

from scrapers.el_tiempo import scrape_el_tiempo
from scrapers.andina import scrape_andina
from scrapers.el_comercio import scrape_el_comercio
from scrapers.gestion import scrape_gestion


# ============================================================
# CONFIGURACIÓN
# ============================================================

REGION = "piura"

NEWS_NUMBER_EL_TIEMPO = 30
NEWS_NUMBER_ANDINA = 5
NEWS_NUMBER_EL_COMERCIO = 20
NEWS_NUMBER_GESTION = 20

PAGINAS_I = 1
PAGINAS_F = 2


# ============================================================
# FECHAS
# ============================================================

FECHA_FINAL = date.today()

FECHA_INICIAL = (
    FECHA_FINAL -
    timedelta(days=8)
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
# NORMALIZAR FECHAS
# ============================================================

def normalizar_fechas(df):

    if df.empty:
        return df.copy()

    df = df.copy()

    fechas = []

    for fecha in df["DIA"].tolist():

        if fecha is None:

            fechas.append(None)
            continue

        if pd.isna(fecha):

            fechas.append(None)
            continue

        fecha = str(fecha).strip()

        if not fecha:

            fechas.append(None)
            continue

        # --------------------------------------------------------
        # Si viene con hora
        # --------------------------------------------------------

        fecha = fecha.split("T")[0]

        # --------------------------------------------------------
        # Si viene como datetime
        # --------------------------------------------------------

        try:

            fecha_obj = datetime.strptime(
                fecha,
                "%Y-%m-%d"
            ).date()

            fechas.append(
                fecha_obj
            )

            continue

        except ValueError:

            pass

        # --------------------------------------------------------
        # Formato dd/mm/yyyy
        # --------------------------------------------------------

        try:

            fecha_obj = datetime.strptime(
                fecha,
                "%d/%m/%Y"
            ).date()

            fechas.append(
                fecha_obj
            )

            continue

        except ValueError:

            pass

        # --------------------------------------------------------
        # No reconocida
        # --------------------------------------------------------

        print(
            f"⚠ Fecha no reconocida: "
            f"{fecha}"
        )

        fechas.append(None)

    # IMPORTANTE:
    # usar .loc para evitar chained assignment

    df.loc[:, "DIA"] = fechas

    return df


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print(
        "SCRAPER DE NOTICIAS - PIURA"
    )
    print("=" * 60)

    print(
        f"Región: {REGION}"
    )

    print(
        f"Fecha inicial: "
        f"{FECHA_INICIAL}"
    )

    print(
        f"Fecha final: "
        f"{FECHA_FINAL}"
    )

    print("=" * 60)

    # ========================================================
    # EL TIEMPO
    # ========================================================

    print()
    print("=" * 60)
    print("INICIANDO EL TIEMPO")
    print("=" * 60)

    try:

        eltiempo = scrape_el_tiempo(
            paginas_i=PAGINAS_I,
            paginas_f=PAGINAS_F,
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
    print("=" * 60)
    print("INICIANDO ANDINA")
    print("=" * 60)

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
    print("=" * 60)
    print("INICIANDO EL COMERCIO")
    print("=" * 60)

    try:

        elcomercio = scrape_el_comercio(
            region=REGION,
            paginas_i=PAGINAS_I,
            paginas_f=PAGINAS_F,
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
    # GESTIÓN
    # ========================================================

    print()
    print("=" * 60)
    print("INICIANDO GESTIÓN")
    print("=" * 60)

    try:

        gestion = scrape_gestion(
            region=REGION,
            paginas_i=PAGINAS_I,
            paginas_f=PAGINAS_F,
            news_number=NEWS_NUMBER_GESTION
        )

        print()
        print(
            f"Gestión terminado: "
            f"{len(gestion)} noticias"
        )

    except Exception as error:

        print()
        print(
            "ERROR EN GESTIÓN:"
        )

        print(error)

        gestion = dataframe_vacio()

    # ========================================================
    # RESUMEN
    # ========================================================

    print()
    print("=" * 60)
    print("RESUMEN DE SCRAPERS")
    print("=" * 60)

    print(
        f"El Tiempo:    "
        f"{len(eltiempo)}"
    )

    print(
        f"Andina:       "
        f"{len(andina)}"
    )

    print(
        f"El Comercio:  "
        f"{len(elcomercio)}"
    )

    print(
        f"Gestión:      "
        f"{len(gestion)}"
    )

    # ========================================================
    # UNIR
    # ========================================================

    print()
    print("=" * 60)
    print("UNIENDO NOTICIAS")
    print("=" * 60)

    noticias = pd.concat(
        [
            eltiempo,
            andina,
            elcomercio,
            gestion
        ],
        ignore_index=True
    )

    print(
        f"Total de noticias antes "
        f"del filtro: {len(noticias)}"
    )

    # ========================================================
    # NORMALIZAR FECHAS
    # ========================================================

    print()
    print(
        "Normalizando fechas..."
    )

    noticias = normalizar_fechas(
        noticias
    )

    print(
        "Fechas normalizadas."
    )

    # ========================================================
    # FILTRAR FECHAS
    # ========================================================

    print()
    print(
        "Filtrando noticias por fecha..."
    )

    noticias = noticias[
        noticias["DIA"].notna()
    ].copy()

    noticias = noticias[
        (
            noticias["DIA"]
            >= FECHA_INICIAL
        )
        &
        (
            noticias["DIA"]
            <= FECHA_FINAL
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

    antes = len(noticias)

    # Primero por LINK
    noticias = noticias.drop_duplicates(
        subset=["LINKS"],
        keep="first"
    )

    # Eliminar posibles duplicados
    # sin link
    noticias_con_link = noticias[
        noticias["LINKS"].astype(str).str.strip() != ""
    ]

    noticias_sin_link = noticias[
        noticias["LINKS"].astype(str).str.strip() == ""
    ]

    noticias = pd.concat(
        [
            noticias_con_link,
            noticias_sin_link
        ],
        ignore_index=True
    )

    despues = len(noticias)

    print(
        f"Noticias antes: {antes}"
    )

    print(
        f"Noticias después: {despues}"
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
        ascending=False,
        na_position="last"
    ).reset_index(
        drop=True
    )

    print(
        "Noticias ordenadas."
    )

    # ========================================================
    # RESUMEN FINAL POR DIARIO
    # ========================================================

    print()
    print("=" * 60)
    print("RESUMEN FINAL")
    print("=" * 60)

    resumen = (
        noticias["DIARIO"]
        .value_counts()
    )

    for diario in [
        "El Tiempo",
        "Andina",
        "El Comercio",
        "Gestión"
    ]:

        cantidad = resumen.get(
            diario,
            0
        )

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

    # ========================================================
    # CARPETA
    # ========================================================

    os.makedirs(
        "Data",
        exist_ok=True
    )

    ruta_salida = os.path.join(
        "Data",
        nombre_archivo
    )

    # ========================================================
    # GUARDAR
    # ========================================================

    print()
    print("=" * 60)
    print("GUARDANDO ARCHIVO")
    print("=" * 60)

    noticias.to_excel(
        ruta_salida,
        index=False
    )

    print()
    print(
        "✓ Archivo guardado correctamente:"
    )

    print(ruta_salida)

    print()
    print("=" * 60)
    print(
        "PROCESO TERMINADO CORRECTAMENTE"
    )
    print("=" * 60)

    print(
        f"Archivo: {ruta_salida}"
    )

    print(
        f"Noticias finales: "
        f"{len(noticias)}"
    )


# ============================================================
# EJECUTAR
# ============================================================

if __name__ == "__main__":

    main()
