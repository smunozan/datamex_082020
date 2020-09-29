#importamos archivo con funciones
from functions import *
from IPython.core.display import display

user_input = mic_rec()
clean_input = clean_city_input(user_input)
cities_input = find_best_match(clean_input)
recomendaciones = reco_cities(cities_input)
mapa = mapa_reco(recomendaciones)
display(mapa)




