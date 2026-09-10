import pandas as pd

from datetime import date, timedelta

from scrapers.el_tiempo import scrape_el_tiempo
from scrapers.andina import scrape_andina


# ============================================================
# CONFIGURACIÓN
# ============================================================

REGION = "piura"

NEWS_NUMBER_EL_TIEMPO = 30
NEWS_NUMBER_ANDINA = 5

PAGINAS_I = 1
PAGINAS_F = 2


# ============================================================
# FECHAS
# ============================================================

FECHA_FINAL = date.today()
FECHA_INICIAL = FECHA_FINAL - timedelta(days=7)


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def main():

    print("=" * 60)
    print("SCRAPER DE NOTICIAS - PIURA")
    print("=" * 60)

    print(f"Región: {REGION}")
    print(f"Fecha inicial: {FECHA_INICIAL}")
    print(f"Fecha final: {FECHA_FINAL}")
    print()


    # ========================================================
    # EL TIEMPO
    # ========================================================

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
        print("ERROR EN EL TIEMPO:")
        print(error)

        eltiempo = pd.DataFrame(
            columns=[
                "DIARIO",
                "DIA",
                "TITULAR",
                "DESCRIPCIÓN",
                "LINKS"
            ]
        )


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
        print("ERROR EN ANDINA:")
        print(error)

        andina = pd.DataFrame(
            columns=[
                "DIARIO",
                "DIA",
                "TITULAR",
                "DESCRIPCIÓN",
                "LINKS"
            ]
        )


    # ========================================================
    # UNIR
    # ========================================================

    print()
    print("=" * 60)
    print("UNIENDO NOTICIAS")
    print("=" * 60)

    noticias = pd.concat(
        [eltiempo, andina],
        ignore_index=True
    )

    print(
        f"Total de noticias: {len(noticias)}"
    )


    # ========================================================
    # FILTRAR POR FECHA
    # ========================================================

    print()
    print("Filtrando noticias por fecha...")

    noticias = noticias[
        (noticias["DIA"] >= FECHA_INICIAL)
        &
        (noticias["DIA"] <= FECHA_FINAL)
    ].copy()

    print(
        f"Noticias después del filtro: "
        f"{len(noticias)}"
    )


    # ========================================================
    # ORDENAR
    # ========================================================

    print()
    print("Ordenando noticias...")

    noticias = noticias.sort_values(
        by="DIA",
        ascending=False
    )

    print("Noticias ordenadas.")


    # ========================================================
    # NOMBRE DEL ARCHIVO
    # ========================================================

    fecha_inicial_str = FECHA_INICIAL.strftime(
        "%Y%m%d"
    )

    fecha_final_str = FECHA_FINAL.strftime(
        "%Y%m%d"
    )

    nombre_archivo = (
        f"noticias_{REGION}_"
        f"{fecha_inicial_str}_"
        f"{fecha_final_str}.xlsx"
    )


    # ========================================================
    # RUTA
    # ========================================================

    ruta_salida = (
        f"Data/{nombre_archivo}"
    )


    # ========================================================
    # GUARDAR
    # ========================================================

    print()
    print("Guardando archivo...")

    noticias.to_excel(
        ruta_salida,
        index=False
    )

    print()
    print("=" * 60)
    print("ARCHIVO GUARDADO")
    print("=" * 60)

    print(ruta_salida)

    print()
    print("=" * 60)
    print("¡PROCESO TERMINADO CORRECTAMENTE!")
    print("=" * 60)


# ============================================================
# EJECUTAR
# ============================================================

if __name__ == "__main__":
    main()
