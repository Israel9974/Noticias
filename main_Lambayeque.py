# %%
import pandas as pd
from helpers import Helper
from datetime import date, timedelta, datetime
import os
import json
import re
import winsound

# %%
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

# %%
start_date = date(2026, 9, 5)
end_date = date(2026, 9, 8)

# %%
paginas_i = input('¿Desea empezar desde el inicio? Coloque "1" para "Sí" o el número de la página donde desea comenzar: ')
paginas_i = int(paginas_i)
if paginas_i < 0:
    raise ValueError('Por favor inserte un número de página valido')
    
paginas_f = input('¿Hasta dónde desea revisar?: (para Diarios del Grupo EL Comercio, recomendado poner 1)')
paginas_f = int(paginas_f)
if paginas_f < paginas_i:
    raise ValueError('Por favor inserte un número de página valido')
paginas_f_noelc = paginas_f + 1

# %%
region = 'lambayeque'

# %%
# para medios que no pertenecen a El Comercio y requerirían de más páginas para completar la semana:
paginas_f = paginas_f_noelc

# %%
#%run el_tiempo.ipynb

# %%
%run el_comercio.ipynb
%run gestion.ipynb
#%run peru21.ipynb
#%run rpp.ipynb
%run andina.ipynb

# %%
%run agraria.ipynb

# %%
noticias = pd.DataFrame()
noticias = pd.concat([elcomercio, gestion, eltiempo, agraria, andina], ignore_index=True)

# %%
noticias

# %%
noticias = noticias[(noticias['DIA'] >= start_date) & (noticias['DIA'] <= end_date)]
noticias.sort_values(by = 'DIA', ascending = False, inplace = True)

# %%
str_stt_date = start_date.strftime("%Y%m%d")
str_end_date = end_date.strftime("%Y%m%d")

# %%
noticias.to_excel(f"./excel_files/noticias_{region}_{str_stt_date}_{str_end_date}.xlsx", index = False)

# %%
duration = 1000  # milliseconds
freq = 320  # Hz
winsound.Beep(freq, duration)
winsound.Beep(freq, duration)
winsound.Beep(freq, duration)


