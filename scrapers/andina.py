# %% [markdown]
# # Código Andina

# %%
import pandas as pd
from andina_scraper import Scraper8
from helpers import Helper
from datetime import datetime
import os
import json
import re

# %%
class Andina:
    """ Un scraper de las paginas del diario Andina.
        Se extrae el titulo, breve descripción y el enlace de referencia. """

    def __init__(self, main_url, news_number):
        self.main_url = main_url
        self.news_number = news_number

    def dframe(self):
        """ Haciendo el data-frame y exportandolo a un archivo .csv """
        news = Scraper8(self.main_url, self.news_number)
        news_scraper = pd.DataFrame({
            'DIARIO': 'Andina',
            'DIA': news.date_scraper(),
            'TITULAR': news.header_scraper(),
            'DESCRIPCIÓN': news.news_scraper(),
            'LINKS': news.link_scraper()
        })

        news_scraper['DESCRIPCIÓN'] = news_scraper['DESCRIPCIÓN'].replace(re.compile("&[a-zA-Z]+?;")," ")
        news_scraper['DIA'] = pd.to_datetime(news_scraper['DIA'], format='%d/%m/%Y').dt.date

        return news_scraper
    
    def _export_to_xlsx(self):
        self.dframe().to_excel(f"./excel_files/elcomercio_" + paginas + f"_{Helper.filename_generator(1)}", index=False)
    
    def export(self, output):
        """ Funcion que exporta datos en diferentes formatos, format_option: 1: CSV ,  2:JSON. """
        if output == 1:
            self._export_to_xlsx()

# %%
if __name__ == "__main__":

    try:
        output = 1
        p_number = 20

        # paginas_i = input('¿Desea empezar desde el inicio? Coloque "1" para "Sí" o el número de la página donde desea comenzar: ')
        # paginas_i = int(paginas_i)
        # if paginas_i < 0:
        #     raise ValueError('Por favor inserte un número de página valido')      
        # paginas_i = paginas_i
        
        # paginas_f = input('¿Hasta dónde desea revisar?: ')
        # paginas_f = int(paginas_f)
        # if paginas_f < paginas_i:
        #     raise ValueError('Por favor inserte un número de página valido')
        # paginas_f = int(paginas_f)+1

        andina = pd.DataFrame()
        
        for i in range(paginas_i, paginas_f):
            i = str(i)
            noticias_et = Andina('https://andina.pe/agencia/busqueda.aspx?search=' + region, p_number)
            globals()['pagina_' + i] = noticias_et.dframe()
            andina = pd.concat([andina, globals()['pagina_' + i]], ignore_index=True)

        fecha_ref = datetime.now()
        
#        elcomercio.to_excel(f"./excel_files/elcomercio_{fecha_ref.year}_{fecha_ref.month}_{fecha_ref.day}.xlsx", index=False)
        
        print(f'¡El archivo de ANDINA está listo!')

    except ValueError as ex:
        print(ex)


