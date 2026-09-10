# %%
from wordcloud import WordCloud
from nltk.corpus import stopwords
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
import spacy
import re

nlp = spacy.load("es_core_news_sm")
spanish_stopwords = set(stopwords.words('spanish'))

# %%
def tokenize_phrase(phrase):
    return [token.lemma_.lower() for token in nlp(phrase)
            if not token.is_punct and not token.is_stop and token.text.lower() not in spanish_stopwords]

# %%
# Cargar datos del Excel
aux = pd.read_excel("./excel_files/43. REPORTE SEMANAL DE NOTICIAS LOCALES - 04_10_ABRIL.xlsx", sheet_name='Para el Word - sin del')
texto_piura = aux['TITULAR'].dropna().tolist()  # Evita valores NaN

# %%
word_counter = Counter(token for frase in texto_piura for token in tokenize_phrase(frase) if not re.search(r'\d', token))

# stopwords en el counter
ignore = [' ','sol','kg','us$','sicario','octubre','talara','incautar','setiembre','septiembre','sullana','muerto','video','|','agosto','cerrado','cierre','concurso','enero','s/','\n','casa','médico','expareja','tonelada','km2','ii','iii','mil','millón','iniciar','peruano','perú','sector','castilla','nacional','año','fertilizant','piura']
for word in list(word_counter):
    if word in ignore:
        del word_counter[word]

nube = WordCloud(width = 1700, height = 500, colormap = 'winter_r', background_color = None, mode = 'RGBA', max_words=80).generate_from_frequencies(word_counter)
plt.imshow(nube,interpolation='bilinear')
plt.axis("off")
plt.show()

nube.to_file("nube.png")

# %%
word_counter

# %%
print(word_counter.keys())


