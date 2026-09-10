# %% [markdown]
# # Código RPP

# %%
import pandas as pd
from rpp_scraper import Scraper6
from helpers import Helper
from datetime import datetime
import os
import json
import re

# %%
class RPP:
    """ Un scraper de las paginas del diario peruano Peru21.
        Se extrae el titulo, breve descripción y el enlace de referencia. """

    def __init__(self, main_url, news_number):
        self.main_url = main_url
        self.news_number = news_number

    def dframe(self):
        """ Haciendo el data-frame y exportandolo a un archivo .csv """
        news = Scraper6(self.main_url, self.news_number)
        news_scraper = pd.DataFrame({
            'DIARIO': 'RPP',
            'DIA': news.date_scraper(),
            'TITULAR': news.header_scraper(),
            'DESCRIPCIÓN': news.news_scraper(),
            'LINKS': news.link_scraper()
        })
        news_scraper.loc[news_scraper['DIA'].str.contains(':'), 'DIA'] = datetime.now().strftime("%Y-%m-%d")
        news_scraper['DIA'] = pd.to_datetime(news_scraper['DIA'], format='%Y-%m-%d').dt.date
        
        return news_scraper
    
    def _export_to_xlsx(self):
        self.dframe().to_excel(f"./excel_files/rpp_" + 'paginas' + f"_{Helper.filename_generator(1)}", index=False)
    
    def export(self, output):
        """ Funcion que exporta datos en diferentes formatos, format_option: 1: CSV ,  2:JSON. """
        if output == 1:
            self._export_to_xlsx()

# %%
if __name__ == "__main__":

    try:
        output = 1
        p_number = 20
        
        rpp = pd.DataFrame()
        
        noticias_et = RPP('https://rpp.pe/peru/' + region, p_number)
        pagina = noticias_et.dframe()
        rpp = rpp._append(pagina, ignore_index = True)

        fecha_ref = datetime.now()
        
#        peru21.to_excel(f"./excel_files/peru21_{fecha_ref.year}_{fecha_ref.month}_{fecha_ref.day}.xlsx", index=False)
        
        print(f'¡El archivo de RPP está listo!')

    except ValueError as ex:
        print(ex)


