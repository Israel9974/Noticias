import pandas as pd
from datetime import date, timedelta
from pathlib import Path
import winsound

from scrapers.el_tiempo import scrape_el_tiempo


# ============================================================
# CONFIGURACIÓN
# ============================================================

REGION = 'piura'

# Fecha final = hoy
END_DATE = date.today()

# Fecha inicial = hace una semana
START_DATE = END_DATE - timedelta(weeks=1)

# Páginas a revisar
PAGINAS_I = 1
PAGINAS_F = 2

# Número de noticias por página
NEWS_NUMBER = 30

# Ruta de salida
RUTA_DATA = Path(
    r'E:\Users\2957\OneDrive - BCRP\1. Israel\7.Optimizaciones\1. Web Scrapping\1. ScraperNewsPaper\4.Data'
)


# ============================================================
# MAIN
# ============================================================

def main():

    print('=' * 60)
    print('SCRAPER DE NOTICIAS - PIURA')
    print('=' * 60)

    print(f'Región: {REGION}')
    print(f'Fecha inicial: {START_DATE}')
    print(f'Fecha final: {END_DATE}')
    print(f'Página inicial: {PAGINAS_I}')
    print(f'Página final: {PAGINAS_F - 1}')
    print()

    # ========================================================
    # EL TIEMPO
    # ========================================================

    eltiempo = scrape_el_tiempo(
        paginas_i=PAGINAS_I,
        paginas_f=PAGINAS_F,
        region=REGION,
        news_number=NEWS_NUMBER
    )

    # ========================================================
    # UNIR RESULTADOS
    # ========================================================

    noticias = pd.concat(
        [eltiempo],
        ignore_index=True
    )

    print()
    print('=' * 60)
    print('RESULTADOS')
    print('=' * 60)

    print(f'Total de noticias obtenidas: {len(noticias)}')

    # ========================================================
    # FILTRAR POR FECHA
    # ========================================================

    noticias = noticias[
        (noticias['DIA'] >= START_DATE) &
        (noticias['DIA'] <= END_DATE)
    ].copy()

    noticias.sort_values(
        by='DIA',
        ascending=False,
        inplace=True
    )

    print(f'Noticias después del filtro: {len(noticias)}')

    # ========================================================
    # CREAR CARPETA DE SALIDA
    # ========================================================

    RUTA_DATA.mkdir(
        parents=True,
        exist_ok=True
    )

    # ========================================================
    # NOMBRE DEL ARCHIVO
    # ========================================================

    str_start_date = START_DATE.strftime('%Y%m%d')
    str_end_date = END_DATE.strftime('%Y%m%d')

    nombre_archivo = (
        f'noticias_{REGION}_'
        f'{str_start_date}_'
        f'{str_end_date}.xlsx'
    )

    ruta_salida = RUTA_DATA / nombre_archivo

    # ========================================================
    # EXPORTAR
    # ========================================================

    noticias.to_excel(
        ruta_salida,
        index=False
    )

    print()
    print('Archivo guardado:')
    print(ruta_salida)

    # ========================================================
    # AVISO SONORO
    # ========================================================

    winsound.Beep(320, 1000)
    winsound.Beep(320, 1000)
    winsound.Beep(320, 1000)

    print()
    print('Proceso terminado correctamente.')


# ============================================================
# EJECUTAR
# ============================================================

if __name__ == '__main__':
    main()