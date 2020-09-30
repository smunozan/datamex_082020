#importamos archivo con funciones
from functions import *
from IPython.core.display import display

user_input = mic_rec()
clean_input = clean_city_input(user_input)
cities_input = find_best_match(clean_input)
recomendaciones = reco_cities(cities_input)
recomendados_mapa = mapa_reco(recomendaciones)
ruta, days = ruta_recomendada(recomendaciones,200)
ruta_mapa = mapa_ruta(ruta)



