import pandas as pd
import re

from scrapers.tiempo_scraper import Scraper2



class ElTiempo:
    """Scraper del diario El Tiempo."""

    def __init__(self, main_url, news_number=30):
        self.main_url = main_url
        self.news_number = news_number

    def dframe(self):
        """Obtiene las noticias de una página y las devuelve como DataFrame."""

        news = Scraper2(
            self.main_url,
            self.news_number
        )

        news_scraper = pd.DataFrame({
            'DIARIO': 'El Tiempo',
            'DIA': news.date_scraper(),
            'TITULAR': news.header_scraper(),
            'DESCRIPCIÓN': news.news_scraper(),
            'LINKS': news.link_scraper()
        })

        # Limpiar descripción
        news_scraper['DESCRIPCIÓN'] = (
            news_scraper['DESCRIPCIÓN']
            .replace(re.compile(r"&[a-zA-Z]+?;"), " ")
        )

        # Convertir meses del español al inglés
        meses = {
            'Ene': 'Jan',
            'Abr': 'Apr',
            'Ago': 'Aug',
            'Set': 'Sep',
            'Dic': 'Dec'
        }

        for mes_es, mes_en in meses.items():
            news_scraper['DIA'] = (
                news_scraper['DIA']
                .replace(mes_es, mes_en, regex=True)
            )

        news_scraper['DIA'] = news_scraper['DIA'].str.strip()

        # Convertir fecha
        news_scraper['DIA'] = pd.to_datetime(
            news_scraper['DIA'],
            format='%b %d, %Y'
        ).dt.date

        return news_scraper


def scrape_el_tiempo(
    paginas_i,
    paginas_f,
    region='piura',
    news_number=30
):
    """
    Ejecuta el scraping de El Tiempo.

    Parameters
    ----------
    paginas_i : int
        Primera página que se desea revisar.

    paginas_f : int
        Última página + 1.

    region : str
        Región utilizada para la búsqueda.

    news_number : int
        Número máximo de noticias por página.
    """

    eltiempo = pd.DataFrame()

    # Para Piura utilizamos la categoría local.
    if region.lower() == 'piura':

        for i in range(paginas_i, paginas_f):

            url = f'https://eltiempo.pe/categoria/local/page/{i}'

            scraper = ElTiempo(
                main_url=url,
                news_number=news_number
            )

            pagina = scraper.dframe()

            eltiempo = pd.concat(
                [eltiempo, pagina],
                ignore_index=True
            )

    # Para otras regiones utilizamos la búsqueda.
    else:

        for i in range(paginas_i, paginas_f):

            url = f'https://eltiempo.pe/page/{i}/?s={region}'

            scraper = ElTiempo(
                main_url=url,
                news_number=news_number
            )

            pagina = scraper.dframe()

            eltiempo = pd.concat(
                [eltiempo, pagina],
                ignore_index=True
            )

    print('¡El archivo de EL TIEMPO está listo!')

    return eltiempo


if __name__ == "__main__":

    # Prueba independiente del scraper
    resultado = scrape_el_tiempo(
        paginas_i=1,
        paginas_f=2,
        region='piura'
    )

    print(resultado)